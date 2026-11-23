# Product decision log

Short records of the decisions that shaped EventCast: the context, the options, what was chosen and what it cost.

## PD1 · Aggregate first, marketplace second

**Context.** Two sided marketplaces start empty. Attendees won't come without events; organizers won't list without attendees.
**Options.** (a) Recruit organizers city by city. (b) Aggregate existing public listings so every city has events from day one.
**Decision.** (b). Organizer tools come on top of an already useful search.
**Tradeoff.** Dependence on third party sources and their quality. Data cleaning becomes the core competence, not a side task.

## PD2 · Deep search with a live counter

**Context.** Querying hundreds of sources properly can take up to a minute. Most users leave a blank loading screen within seconds.
**Options.** (a) Search fewer sources and return faster. (b) Search everything, but show cached results immediately and a live count of events found.
**Decision.** (b), plus a "Stop search" button so the user stays in control.
**Tradeoff.** More engineering for streaming and cache freshness. The upside is that coverage, the main differentiator, isn't sacrificed for speed.

## PD3 · Free ticketing

**Context.** Organizers already pay fees on other platforms and have no reason to try a new one.
**Options.** (a) Undercut competitors' fees. (b) Free tickets for free events, with QR and barcode check in and capacity limits.
**Decision.** (b).
**Tradeoff.** No ticketing revenue at first. In return every ticketed event is first party data in the pool, and organizers start using EventCast's tools.

## PD4 · AI agents as a customer segment

**Context.** People are starting to ask AI assistants what to do this weekend. Those assistants need fresh, structured event data.
**Options.** (a) Ignore it, focus on apps. (b) Offer a classic REST API only. (c) Offer an MCP server that agents can connect to directly, with per call payments over x402.
**Decision.** (c), alongside the Enterprise API.
**Tradeoff.** An early, still moving standard. But being a native data source for agents is a distribution channel that doesn't require users to install anything.

## PD5 · One pool, many views

**Context.** Different users browse differently: some want a list, some a map, some a calendar.
**Decision.** Every view reads the same cleaned pool. Adding a view is a front end task only.
**Tradeoff.** The pool's schema has to be stable and rich enough for all views, which makes schema changes more expensive.

## PD6 · Show the source on every event

**Context.** Aggregated data raises a trust question: where is this from, and is it real?
**Decision.** Every event shows its source and links out to it.
**Tradeoff.** Some users click through and buy elsewhere. Trust in the results is worth more than holding every click.
