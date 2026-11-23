"""Cross source event deduplication: a standalone illustration.

The same concert shows up on a ticketing site, the venue's calendar and a
community listing, each with slightly different titles, times and venue names.
Showing all three copies makes search results feel broken, so they have to be
merged into one event. This module shows the approach in about 150 lines.

This is NOT EventCast production code. It is a clean reimplementation of the
idea for this case study, run on fictional sample data.
"""
from __future__ import annotations

import csv
import math
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

NOISE_WORDS = {
    "tickets", "ticket", "live", "in", "at", "the", "concert", "tour", "presents",
    "official", "sweden", "stockholm", "gothenburg", "goteborg", "gbg", "malmo",
    "2026", "2027", "feat", "ft", "and", "with", "i", "pa", "med", "och",
}
VENUE_ALIASES = {
    "avicii arena": "globen", "ericsson globe": "globen", "globen arena": "globen",
    "kulturhuset stadsteatern": "kulturhuset", "kulturhuset": "kulturhuset",
}
# When fields disagree, trust sources in this order.
SOURCE_PRIORITY = ["venue_calendar", "ticketmaster", "seetickets", "eventbrite", "meetup", "community"]


def _ascii(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def normalize_title(title: str) -> str:
    tokens = re.findall(r"[a-z0-9]+", _ascii(title))
    return " ".join(t for t in tokens if t not in NOISE_WORDS)


def normalize_venue(venue: str) -> str:
    v = " ".join(re.findall(r"[a-z0-9]+", _ascii(venue)))
    for alias, canonical in VENUE_ALIASES.items():
        if alias in v:
            return canonical
    return v


@dataclass
class Listing:
    id: str
    source: str
    title: str
    venue: str
    city: str
    start: datetime
    price: str
    truth: str = ""  # ground truth cluster, only used for evaluation
    norm_title: str = field(init=False)
    norm_venue: str = field(init=False)

    def __post_init__(self):
        self.norm_venue = normalize_venue(self.venue)
        venue_tokens = set(re.findall(r"[a-z0-9]+", _ascii(self.venue))) | {self.norm_venue}
        self.norm_title = " ".join(t for t in normalize_title(self.title).split() if t not in venue_tokens)


MAX_CLOCK_DRIFT_HOURS = 1.5  # sources often disagree on doors vs show time
TITLE_GATE = 0.8              # titles must agree before anything else counts


def idf_weights(listings: list[Listing]) -> dict[str, float]:
    """Rare words ("python", "rust") matter more than common ones ("meetup", "december")."""
    df: dict[str, int] = {}
    for l in listings:
        for t in set(l.norm_title.split()):
            df[t] = df.get(t, 0) + 1
    n = len(listings)
    return {t: math.log((n + 1) / (c + 1)) + 1 for t, c in df.items()}


def _tokens_match(a: str, b: str) -> bool:
    if a == b:
        return True
    if min(len(a), len(b)) >= 4 and (a.startswith(b) or b.startswith(a)):
        return True  # "lucia" vs "luciakonsert"
    return SequenceMatcher(None, a, b).ratio() >= 0.85  # typos


def title_similarity(a: str, b: str, idf: dict[str, float]) -> float:
    """IDF weighted containment of the shorter title in the longer one, with fuzzy token matching."""
    ta, tb = a.split(), b.split()
    if not ta or not tb:
        return 0.0
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    w = lambda t: idf.get(t, 1.0)
    matched = sum(w(t) for t in short if any(_tokens_match(t, u) for u in long_))
    return matched / sum(w(t) for t in short)


def similarity(a: Listing, b: Listing, idf: dict[str, float] | None = None) -> float:
    """Score in [0, 1] that two listings are the same real world event."""
    idf = idf or {}
    if a.city.lower() != b.city.lower():
        return 0.0
    hours_apart = abs((a.start - b.start).total_seconds()) / 3600
    if hours_apart > MAX_CLOCK_DRIFT_HOURS:  # a different session (early vs late show) or a different day
        return 0.0
    title_score = title_similarity(a.norm_title, b.norm_title, idf)
    if title_score < TITLE_GATE:
        return 0.0
    venue_score = 1.0 if a.norm_venue == b.norm_venue else SequenceMatcher(None, a.norm_venue, b.norm_venue).ratio()
    time_score = 1.0 - hours_apart / MAX_CLOCK_DRIFT_HOURS
    return 0.6 * title_score + 0.25 * venue_score + 0.15 * time_score


class _UnionFind:
    def __init__(self, items):
        self.parent = {i: i for i in items}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        self.parent[self.find(a)] = self.find(b)


def cluster(listings: list[Listing], threshold: float = 0.72) -> list[list[Listing]]:
    """Group listings into events. Blocking by city and date keeps pair counts small."""
    blocks: dict[tuple, list[Listing]] = {}
    for l in listings:
        blocks.setdefault((l.city.lower(), l.start.date()), []).append(l)
    idf = idf_weights(listings)
    uf = _UnionFind([l.id for l in listings])
    for block in blocks.values():
        for a, b in combinations(block, 2):
            if similarity(a, b, idf) >= threshold:
                uf.union(a.id, b.id)
    groups: dict[str, list[Listing]] = {}
    by_id = {l.id: l for l in listings}
    for l in listings:
        groups.setdefault(uf.find(l.id), []).append(by_id[l.id])
    return list(groups.values())


def merge(group: list[Listing]) -> dict:
    """Build one canonical event from a group, preferring trusted sources."""
    ranked = sorted(group, key=lambda l: SOURCE_PRIORITY.index(l.source) if l.source in SOURCE_PRIORITY else 99)
    best = ranked[0]
    prices = [l.price for l in ranked if l.price and l.price.lower() not in {"see website", ""}]
    return {
        "title": best.title,
        "venue": best.venue,
        "start": best.start.isoformat(timespec="minutes"),
        "price": prices[0] if prices else "See website",
        "sources": sorted({l.source for l in group}),
        "listing_ids": [l.id for l in group],
    }


def evaluate(groups: list[list[Listing]]) -> dict:
    """Pairwise precision and recall against the ground truth labels."""
    predicted, actual = set(), set()
    all_listings = [l for g in groups for l in g]
    for g in groups:
        predicted |= {tuple(sorted((a.id, b.id))) for a, b in combinations(g, 2)}
    for a, b in combinations(all_listings, 2):
        if a.truth and a.truth == b.truth:
            actual.add(tuple(sorted((a.id, b.id))))
    tp = len(predicted & actual)
    precision = tp / len(predicted) if predicted else 1.0
    recall = tp / len(actual) if actual else 1.0
    return {"precision": precision, "recall": recall, "true_pairs": len(actual), "predicted_pairs": len(predicted)}


def load(path: str | Path) -> list[Listing]:
    with open(path, newline="", encoding="utf-8") as f:
        return [
            Listing(r["id"], r["source"], r["title"], r["venue"], r["city"],
                    datetime.fromisoformat(r["start"]), r["price"], r.get("truth", ""))
            for r in csv.DictReader(f)
        ]


if __name__ == "__main__":
    listings = load(Path(__file__).with_name("sample_listings.csv"))
    groups = cluster(listings)
    print(f"{len(listings)} raw listings -> {len(groups)} unique events\n")
    for g in sorted(groups, key=len, reverse=True):
        if len(g) > 1:
            m = merge(g)
            print(f"  {m['title']}  ({len(g)} listings from {', '.join(m['sources'])})")
    scores = evaluate(groups)
    print(f"\nPairwise precision {scores['precision']:.0%}, recall {scores['recall']:.0%}")
