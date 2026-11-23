from datetime import datetime
from pathlib import Path

from dedupe import Listing, cluster, evaluate, load, merge, normalize_title, normalize_venue, similarity

DATA = Path(__file__).resolve().parents[1] / "sample_listings.csv"


def L(i, title, venue="Globen", city="Stockholm", start="2026-12-05T20:00", source="community"):
    return Listing(str(i), source, title, venue, city, datetime.fromisoformat(start), "")


def test_normalization_strips_noise_and_aliases():
    assert normalize_title("Nordic Lights Tour 2026 – Live in Stockholm") == "nordic lights"
    assert L(1, "Luciakonsert i Storkyrkan", "Storkyrkan").norm_title == "luciakonsert"
    assert normalize_venue("Ericsson Globe") == normalize_venue("Avicii Arena") == "globen"
    assert normalize_venue("Göta Lejon") == normalize_venue("Gota Lejon")


def test_same_event_scores_high_different_city_zero():
    assert similarity(L(1, "Nordic Lights"), L(2, "NORDIC LIGHTS live!!")) > 0.9
    assert similarity(L(1, "Lucia Concert", "Storkyrkan"), L(2, "Luciakonsert i Storkyrkan", "Storkyrkan")) > 0.9
    assert similarity(L(1, "Nordic Lights"), L(2, "Nordic Lights", city="Gothenburg")) == 0.0


def test_two_shows_same_night_stay_separate():
    early = L(1, "Lucia Concert", "Storkyrkan", start="2026-12-13T18:00")
    late = L(2, "Lucia Concert", "Storkyrkan", start="2026-12-13T21:00")
    assert len(cluster([early, late])) == 2


def test_similar_meetups_at_same_venue_not_merged():
    a = L(1, "Python Stockholm: December Meetup", "Norrsken House", start="2026-12-08T18:00")
    b = L(2, "Rust Stockholm: December Meetup", "Norrsken House", start="2026-12-08T18:00")
    assert len(cluster([a, b])) == 2


def test_merge_prefers_trusted_source_and_real_price():
    g = [L(1, "NORDIC LIGHTS live", source="community"), L(2, "Nordic Lights", source="venue_calendar")]
    g[0].price, g[1].price = "See website", "From 695 SEK"
    m = merge(g)
    assert m["title"] == "Nordic Lights" and m["price"] == "From 695 SEK"


def test_sample_dataset_quality():
    groups = cluster(load(DATA))
    scores = evaluate(groups)
    assert len(groups) == 13
    assert scores["precision"] == 1.0
    assert scores["recall"] >= 0.9
