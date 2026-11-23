# Roadmap thinking

Prioritised with a simple question: **does it make results more trustworthy, or does it create a reason to come back?**

## Now: trust in the results

* **Category accuracy.** Each source has its own taxonomy, and mapping them onto one is where most visible errors come from. Plan: a labelled sample per source, a classifier on title and description, and a weekly accuracy check.
* **Freshness.** Expire past events promptly in every surface, including cached and offline results.
* **Search speed.** Prioritise the sources that historically return the most unique events per city, so the first results are the best ones.

## Next: reasons to come back

* **Organizer revenue forecasts.** Before choosing a date, an organizer sees expected demand for that city and week, how many similar events compete on the same night, and a revenue range. Prototype: [event_demand_forecast](https://github.com/sarimyawaredu-crypto/event_demand_forecast).
* **Personalised recommendations** from saved events and alert topics.
* **Weekly digests** for saved searches: "12 new events in Stockholm match your interests".

## Later: revenue

* **Paid promotion** for organizers, clearly labelled.
* **Partnerships with tourism boards** that want to show visitors what's on.
* **Self serve API plans** alongside per call agent pricing.

## Deliberately not doing (yet)

* **Paid ticketing.** Payments, refunds and fraud would pull focus from data quality.
* **Social features** such as friends and chat. Valuable, but only once the core results are reliably good.
