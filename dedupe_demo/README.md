# Deduplication demo

A standalone, dependency free reimplementation of cross source event deduplication, written for the EventCast case study. Not production code; the sample data is fictional.

```bash
python3 dedupe.py        # 22 raw listings -> 13 unique events
python3 -m pytest tests  # edge case tests
```

**Approach:** normalise titles and venues → block by city and day → gate on start time (over 1.5 hours apart means a different session) → IDF weighted fuzzy title match → union find clustering → merge with source priority.

**Edge cases covered by tests**
* Same event, three sources, three different titles and venue names → merged
* Early and late show of the same concert → kept separate
* Two different meetups at the same venue and time → kept separate
* Swedish and English titles ("Luciakonsert" vs "Lucia Concert") → merged
* Same tour in two cities → kept separate

The rules were tuned on this small sample, so its 100% precision and recall says the logic handles these cases, not how it would score on real traffic. In production, a larger labelled set and weekly sampling of merge errors would be needed.
