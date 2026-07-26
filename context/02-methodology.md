# 02 · Methodology — FCI 3.0

Source: [A] FCI 3.0 prototype, `/methodology` (v0, beta, in review toward v1).

## The formula

```
FCI(t) = DIDO(t) · (1 − PITO(t)) · ρ(t)
```

In plain terms: **what you can do, times what you don't depend on, times how fast you react.**

The product is the whole argument. It does not add, and that matters:

- **High DIDO with high PITO is performative** — fab labs without metabolic shift. A city can have
  beautiful open data and a dozen labs while importing everything it consumes.
- **Low PITO with low DIDO is a depleted city, not a Fab City** — neither extracting much nor generating
  much. Subsistence is not resilience.
- **A zero anywhere zeroes the result.** A city that senses everything and acts on nothing scores nothing,
  regardless of how good its dashboards are. This is a modelling choice, it is deliberate, and it is
  falsifiable — it is hypothesis H₀-A.

The `(1 − PITO)` term reframes PITO from an absolute load into *distance walked off the linear-extractive
baseline*.

The trajectory form — the one that actually answers the 2054 pledge — is **ΔFCI/Δt**: the rate at which a
city is fab-cityifying. With quarterly resolution over a 36-month horizon, that trajectory is what the
pilots are built to measure.

## The three terms

### PITO — Products In, Trash Out

The linear-extractive metabolic signature. *Buy far, waste near.*

Measures what the city receives and rejects: imports of products, energy, food and raw materials; exports
of waste, emissions and externalised pollution. A stock variable in [0,1]; high PITO means heavy
linear-extractive metabolism.

```
PITO(t) = Σ(w_c^PITO · s_c^extractive) / Σ(w_c^PITO)
```

### DIDO — Data In, Data Out

The regenerative-distributed signature. *Sense what's happening, share what you learn, make more of it
close to home.*

Measures what the city generates and circulates: open data infrastructure, fab-lab activity, distributed
manufacturing capacity, recycling and remanufacturing capacity, community sensing, institutional
transparency, and the policy / research / innovation layer that lets a city act on what it knows.

```
DIDO(t) = Σ(w_c^DIDO · s_c^capacity) / Σ(w_c^DIDO)
```

**Why both axes and not one.** A city can have very high DIDO and still very high PITO — Barcelona is
closer to this than people would like. A city can have low DIDO and low PITO for bad reasons: sparse
instrumentation hiding both flows. A single number cannot tell those apart, and that is precisely the
weakness of the original 37/100.

*PITO and DIDO are the founding Fab City vocabulary, coined by Vicente Guallart and Neil Gershenfeld,
documented in the Fab City Whitepapers (Diez, 2014 and 2016). FCI 3.0 operationalises them; it did not
invent them.*

### ρ (rho) — the response coefficient

*How fast a reading turns into something actually being done.* A number nobody acts on changes nothing.

ρ ∈ [0,1] measures action latency: the speed at which an observation at any tier produces a fitted,
human-approved response at the appropriate governance tier, within a pre-registered budget.
ρ = 1 is perfect coupling; ρ = 0 means observations are made and never acted upon.

Generations 1 and 2 have ρ implicitly at 1 because their models are static. Generation 3 makes it
measurable and treats it as the third axis. Without ρ the index is a snapshot; with ρ it is a metabolism —
which is what the 2054 pledge has always implicitly asked us to measure.

**Status: v0 protocol note.** Tier-weighting and council-rejection handling are open items. No pilot has a
measured ρ yet, which is why no pilot has a complete FCI number.

## Cell scores

Each cell `c` produces a normalised score `s_c ∈ [0,1]` using Boeing's discipline: **priority ×
self-sufficiency where formal data exists; documented proxy where it does not, flagged as such.**

The same cell score is read two ways: `s_c^extractive` (interpreted as throughput) and `s_c^capacity`
(interpreted as regenerative capacity). Most cells contribute meaningfully to one side and faintly to the
other, in proportion to their weights. Only Economic × City (0.5/0.5) and Environmental × Community
(0.5/0.5) contribute equally to both.

## The weight table (v0)

Each cell carries a PITO weight and a DIDO weight, both in [0,1], summing to 1. Weights are not
philosophical — they are documented assignments derived from what the cell actually measures. Cells
measuring **throughput** weight toward PITO; cells measuring **capacity, transparency or institutional
response** weight toward DIDO.

**Documented upstream (six cells):**

| Cell | PITO | DIDO | Note |
|---|---|---|---|
| Economic × City | 0.5 | 0.5 | The Generation 1+2 cell |
| Economic × Region | 0.5 | 0.5 | Same measurement, regional scope |
| Economic × Bioregion | 0.8 | 0.2 | ⚠ flagged for sharpened argument |
| Environmental × Community | 0.5 | 0.5 | ⚠ flagged for sharpened argument |
| Economic × Community | 0.3 | 0.7 | ⚠ flagged for sharpened argument |
| Governance × Region, Governance × Bioregion | 0.2 | 0.8 | Named as the thinnest cells |

The other fourteen cells in this dashboard carry **reconstructed** weights, proposed from [B] to fill
gaps the v0 table has not published. They are marked as such in the interface and in `assets/data.js`
via `wSource: "reconstructed"`.

## Aggregation — where the adding stops

**Community → City → Region nest and add up. Bioregion and Planet do not.**

The framework gives three of five scales a job of aggregating, and the top two a job of setting limits:

- **Community** = operational — where instruments touch the ground
- **City** = governance — the first level that can act
- **Region** = governance, and the **aggregation ceiling** — the last level that can act
- **Bioregion** = boundary condition
- **Planet** = boundary condition + global knowledge

Why it stops at the region: no government sits at the bioregion or planetary scale that could take a score
and act on it fast enough to matter — and that speed *is* ρ. There is only ecological and planetary
reference above the region. A region scoring well inside a bioregion already in overshoot is not, in fact,
scoring well; the boundary layers exist to make that visible.

## Attribution is not aggregation

A distinction that protects the framework from overstated claims, and the most common way metrics
programmes lose credibility.

- **Attribution** — effects linkable with reasonable confidence to a specific intervention.
- **Aggregation** — the cumulative performance of larger systems.

A fab lab can credibly report how many repairs it completed, how many people it trained, how many
partnerships it activated. It **cannot** infer from those figures that a city or a bioregion has become
sustainable. Local success does not automatically sum to global sustainability. The matrix exists so a
city cannot fool itself on this point.

## The Boeing recovery

The most important methodological move in the whole instrument, and the one to lead with when talking to
anyone who knows the prior work.

Utopies' Paris score (37.58, 2018) and Boeing's Hamburg score (37.00, 2024) are both **single-cell,
single-snapshot computations** at Economic × Region — no DIDO axis, ρ implicit at 1.

Set every weight to zero except Economic × Region, drop the coupling term, compute only the
self-sufficiency dimension:

```
FCI_Boeing = s_capacity / (s_extractive + s_capacity)     at (Economic, Region)
```

For Hamburg this returns ~0.37. For Paris, 0.3758. **The numbers are recovered.**

That is the respect move: Generations 1 and 2 computed one cell, with rigour, and arrived at the right
answer *for that cell*. Generation 3 computes twenty cells, weighted through PITO and DIDO, coupled
through ρ. The 37/100 ceiling is exposed as a projection of the full index onto its single
best-instrumented cell — same instrument, less resolution.

The derivation also explains *why* both cities landed on ~37: at Economic × Region, with public data only
and no dynamic component, the most diversified Western metros hit the same bound, because the underlying
material flows are governed by global supply-chain geometry rather than local policy. The way to move the
number is by activating DIDO and ρ — which is exactly what FCI 3.0 measures.

**Status:** sketched, not formal. A worked Hamburg example on public NACE / COICOP data would close the
loop and pre-empt the most predictable reviewer objection. This is an open item.

## Open gaps (methodology §7)

1. **Twelve of twenty cells** are meaningfully populated. The Region tier and Governance × Bioregion /
   × Region are thinnest — either populated honestly with mock discipline or named as deferred deliverables.
2. **The weight table is v0.** Three cells need sharpened argument before hardening: Economic × Bioregion,
   Environmental × Community, Economic × Community.
3. **The Boeing recovery is sketched, not formal.**
4. **The ρ protocol is a v0 note** — tier-weighting and council-rejection handling open.
5. **Vivanco's matrix is a working paper** plus a 2025 doctoral thesis, not peer-reviewed in its own right.
   A bioregional peer-matching companion paper would fix that.
6. **LOCAL SHIFT® and LOCAL FOOTPRINT® Nature are proprietary Utopies products.** The published
   methodology and 2018 numbers are cited; reproducibility of simulator outputs is not claimed.
7. **The evidence base above Community is close to empty.** Peuckert et al. (2025) reviewed ~1,000 fab lab
   impact studies and found strong quantitative evidence for learning, skills and entrepreneurship
   outcomes — and almost none for bioregional, place-based or knowledge-sharing layers.

Naming these in the body of the methodology is the price of the credibility the instrument asks for.
