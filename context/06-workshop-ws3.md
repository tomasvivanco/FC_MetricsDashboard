# 06 · WS3 — Measuring the Fab City

**Workshop 3, FAB26 Boston.** Tomas Diez × Tomás Vivanco.
Deck: `sources/FAB26_WS3_Deck_v2.pptx` (11 slides, with speaker notes).

This document covers the workshop's argument and **how the dashboard serves each move**. For the delivery
notes — timing, staging, what to say when — read the deck's own speaker notes; they are detailed and
should not be duplicated here.

## The argument, in four beats

**1. The ceiling.** Paris scored 37.58 (Utopies, 2018). Hamburg scored 37.00 (Boeing, 2024). Two teams
that never met, six years apart, two independent statistical systems — the same number. That is not two
cities failing. It is the geometry of global supply chains, measured twice. Both computed **one cell of
twenty**; the other nineteen were dark.

**2. The wound.** Twelve years of the pledge. 2,700+ fab labs. 56 signatory cities. And a 2025 review of
~1,000 fab lab impact studies found **zero rigorous causal evidence** at the tier where the planetary
stakes live. The pledge needs an instrument.

**3. The instrument.** The Full Stack folds into a 4 × 5 matrix — twenty parts of city life. Three dials,
multiplied, not added: `FCI = DIDO · (1 − PITO) · ρ`. Capacity, times independence, times reflexes.

**4. The deal.** PLANETAI: production capacity at every scale, computation a city could not buy, and
sovereignty by design — the node lives at the lab, community council veto, humans approve, every deploy
on a public ledger. 36 months, four bioregion pilots, two pre-registered hypotheses, and a null is
publishable.

## The vote (slide 7) — the mechanism made physical

Three cities, hands up, no reveal until everyone commits:

- **City A — the dashboard city.** Sensors everywhere, a beautiful open-data portal, imports everything.
  No observation has ever changed anything.
- **City B — the self-sufficient village.** Grows its own food, barely imports. Almost no labs, no data,
  no network.
- **City C — the responsive maker city.** Decent labs, moderate imports. When the river sensor spikes, a
  fitted response is fabricated and deployed within weeks.

**C wins, and A scores near zero.** Multiplication is merciless: ρ ≈ 0 zeroes the product no matter how
good the portal. B is subsistence, not resilience — independence without capacity. You cannot compensate
paralysis with dashboards, and you cannot average your way past a zero.

Run the vote *before* showing the formula, so the reveal confirms a mechanism the room already saw.

## Why the exercise happens on the Community row

This is the part worth saying out loud, because it is the difference between a workshop that feels like
homework and one that feels like power.

We audited every indicator in the framework and asked who can actually produce it. The answer:

| Scale | Lab can measure alone |
|---|---|
| Community | **16 of 21** |
| City | 0 of 21 |
| Region | 0 of 21 |
| Bioregion | 2 of 23 |

The network owns the bottom row and almost nothing above it. So the exercise puts participants where they
have sovereignty — and then shows the nine network-own sources as the honest route upward. Nobody is asked
to guess about the planet. They are asked what they could pull this month, and who they would have to
email for the rest.

Full detail in [`04-sovereignty-audit.md`](04-sovereignty-audit.md).

## The exercise — 17 minutes, three moves

### 1 · Dot the matrix (7 min)

Scan the twenty cells. Dot only the **3–4 you actually know something about** — not all twenty.

- **Green** — you could pull this data *this month*. Write the source on the dot.
- **Yellow** — it exists but it is locked.
- **Dark** — leave it.

> **The classic mistake is over-claiming green.** Push back: "could you pull it this month?" Downgrade
> liberally. Ask who actually has hands on the source — it is often not the enthusiast in the room. The
> provenance discipline is taught here, in conversation, not on a slide.

**In the dashboard:** turn on **Workshop mode** in the matrix panel, enter table name and city (Boston is
the default so no table burns five minutes on "whose city?"), then click a cell and mark it. The matrix
goes from grey to coloured as tables dot. That picture is the point — the room is watching which parts of
a city are legible and which are dark.

The dashboard caps a table at four dotted cells and says why, so the "3–4, not twenty" rule enforces
itself instead of needing a facilitator at every table.

### 2 · Pick ONE cell (5 min)

Not the easiest. The one that **matters and is reachable in 30 days**. If a dark cell matters more than
any green one, commit instead to the smallest campaign that would create that data.

**In the dashboard:** open the chosen cell and read its indicators — unit, method, direction, who normally
feeds it, whether it is lab-fed or something you must go and ask for. That converts "we should measure
repairs" into "143 units per month, from the repair log, scaled against a stated ceiling".

### 3 · Fill the card (5 min)

**One cell · one source · one name · one date** — plus the first step and the real day it happens.

> "Email the data officer, Aug 4" is a first step. "Explore options" is not.

**In the dashboard:** fill the card in the cell panel and save. Every card across every table lands in the
**Workshop cards** tab — one sheet the facilitator can read out, copy as text, or export as CSV.

**Hard gate at minute 40:** markers down, one cell you can defend and one email you will send.

## After the workshop

Every card gets a personal email within 72 hours, drafted from the card, never auto-sent, **quoting their
own first step back to them**. Two doors: an active Fab City becomes a co-participant (your matrix, your
operator, our support); everyone else goes through the network at fab.city.

Teams that want their readings in the instrument submit a CSV — see [`../data/README.md`](../data/README.md).

## Facilitator setup checklist

- [ ] Open the dashboard and confirm **Workshop mode** toggles on cleanly
- [ ] Clear any leftover cards from a previous session (**Workshop cards → Clear all cards**)
- [ ] Confirm the city list includes the cities in the room; Boston is default
- [ ] Have `data/template.csv` ready for teams who want to submit afterwards
- [ ] Screenshot fallback for the phase plot and the Boston page — conference wifi is a coin-flip
- [ ] Pre-seed the wall with the four pilots before doors open, so it is never empty in a thin room

## Adapting it elsewhere

The dashboard does not hard-code Boston. Change the default city in `WORKSHOP` and `CITIES` in
`assets/data.js`. The three-move structure and the four-cell cap travel unchanged — they are the parts
that make the exercise produce commitments instead of opinions.

If you run it in a city that is *not* a pilot, keep the sovereignty framing: it is what makes a room of
people with no official data feel like they have something real to contribute. They do — it is called the
Community row.
