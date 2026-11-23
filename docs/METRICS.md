# Metrics

## North star

**Events a user saves, shares or books per week.** It captures the moment search turned into a plan, which is the value EventCast exists to create. Page views and searches alone would reward slow or confusing results.

## Input metrics

| Area | Metric | Why it matters | Healthy direction |
|---|---|---|---|
| Coverage | Events found per city vs a manual benchmark of what's really on | The core promise is "everything" | Up |
| Quality | Duplicate rate in results | Duplicates make results look broken | Down, below 2% |
| Quality | Wrong category rate (sampled and labelled weekly) | Wrong categories break filters | Down |
| Quality | Past events shown as upcoming | One stale event damages trust | Close to zero |
| Speed | Time to first result | Perceived speed | Under 2 seconds from cache |
| Speed | Time to complete search | Real coverage cost | Down, without losing coverage |
| Engagement | Search to event click rate | Results are relevant | Up |
| Engagement | Alerts created per active user | Intent to come back | Up |
| Organizers | Events published, tickets issued, check ins | Supply side traction | Up |
| Agents | MCP calls, paid calls, unique agent clients | New channel traction | Up |

## Guardrails

* **Source error rate**: share of source requests failing or timing out. A rise usually means an adapter broke.
* **Merge error rate**: share of merged events that were actually different events, sampled weekly. Deduplication that's too aggressive silently hides events.
