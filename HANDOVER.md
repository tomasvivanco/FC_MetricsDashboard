# Fab City Metrics Dashboard — handover

**One document, self-contained.** Read this and you can continue the work without having been in the
room. Everything else in `context/` is detail you can reach for when you need it.

- **Live dashboard:** <https://tomasvivanco.github.io/FC_MetricsDashboard/>
- **Repository:** <https://github.com/tomasvivanco/FC_MetricsDashboard>
- **Status:** working research build · methodology v0, in review · not an official Fab City Foundation publication

---

## 1 · The problem this exists to solve

The Fab City pledge asks signatory cities to produce almost everything they consume by 2054.

Twelve years in: **56 signatory cities, 2,700+ fab labs, and essentially zero rigorous causal evidence**
that any of it changes a city's trajectory. A 2025 review of ~1,000 fab lab impact studies (Peuckert et
al.) found strong quantitative evidence for learning, skills and entrepreneurship outcomes — and almost
none at the bioregional, place-based or knowledge-sharing layers where the planetary stakes actually sit.

That gap is not for lack of effort. It is because **no instrument connected a repair log in one
neighbourhood to a planetary limit.** Measuring one scale tells you nothing about whether the system
moved. Measuring only the planet tells you nothing you can act on.

### The ceiling that makes the point

Utopies measured Paris in 2018: **37.58/100**.
Boeing measured Hamburg in 2024: **37.00/100**.

Two independent teams, two statistical systems, six years apart, never met — the same number.

That convergence is not two cities failing. It is the **public-data ceiling**: a property of global
supply-chain geometry, not of local policy. Both computed **one cell** of what should be twenty. The
other nineteen were dark. Any diversified Western metro measured that way lands on ~37.

**The way to move the number is not better measurement of that one cell. It is measuring the other
nineteen — and adding the dimension nobody scored: whether anyone acts on what they learn.**

---

## 2 · The instrument

### The matrix

Twenty parts of city life: **four pillars × five scales.**

|  | Community | City | Region | Bioregion | Planet |
|---|---|---|---|---|---|
| **Environmental** | | | | | |
| **Social** | | | | | |
| **Economic** | | **← the 37 cell** | ← or here | | |
| **Governance** | | | | | |

Pillars: environmental (material and energy), social (people), economic (value), governance (decisions).
Scales: from a neighbourhood to the whole planet.

Each cell asks **one plain question** ("Is this neighbourhood keeping material in use instead of throwing
it away?"), names the indicators that would answer it, and carries two documented weights.

### The formula

```
FCI(t) = DIDO(t) · (1 − PITO(t)) · ρ(t)
```

**What you can do, times what you don't depend on, times how fast you react.**

- **PITO** — Products In, Trash Out. Buy far, waste near. The linear-extractive signature.
- **DIDO** — Data In, Data Out. Sense, share, make locally. The regenerative-distributed signature.
- **ρ (rho)** — the response coefficient. How fast an observation becomes a fitted action.

*PITO and DIDO are the founding Fab City vocabulary, coined by Vicente Guallart and Neil Gershenfeld
(Diez, Fab City Whitepapers 2014, 2016). This work operationalises them; it did not invent them.*

### Why it multiplies instead of adding — the single most important idea

This is the argument, and it is worth defending precisely because it looks like a technicality.

- **High DIDO with high PITO is performative.** Fab labs and open data portals while importing
  everything. Capacity without metabolic shift.
- **Low PITO with low DIDO is a depleted city, not a Fab City.** Neither extracting much nor generating
  much. Subsistence is not resilience.
- **A zero anywhere zeroes the result.** A city that senses everything and acts on nothing scores
  nothing, no matter how beautiful its dashboards.

Addition would let a city compensate paralysis with instrumentation. Multiplication refuses.
**This is a modelling choice, it is deliberate, and it is falsifiable** — it is the project's first
pre-registered hypothesis.

### The Boeing recovery — how the prior work survives inside this

Set every weight to zero except Economic × Region, drop the coupling term, compute only
self-sufficiency, and the formula returns **~0.37 for Hamburg and 0.3758 for Paris**. The old numbers are
recovered exactly.

That is the respect move, and it should always be led with when talking to anyone who knows the prior
work: **Generations 1 and 2 computed one cell, with rigour, and got the right answer for that cell.**
Generation 3 computes twenty, weighted through PITO and DIDO, coupled through ρ. The 37/100 is exposed
as a projection of the full index onto its single best-instrumented cell — same instrument, less
resolution. FCI 3.0 *contains* the prior result rather than replacing it.

*Status: sketched, not formal. A worked Hamburg example on public NACE/COICOP data would close this and
pre-empt the most predictable reviewer objection. **This is the highest-value open research task.***

---

## 3 · The finding that shapes everything

We audited all ~95–108 indicators the framework defines and asked one blunt question:
**who can actually produce this number?**

| Scale | Indicators | 🔧 Lab can measure alone | ⚖️ Mixed | 🌐 Needs external |
|---|---|---|---|---|
| **Community** | 21 | **16** | 4 | 0 |
| City | 21 | 0 | 2 | 19 |
| Region | 21 | 0 | 3 | 18 |
| Bioregion | 23 | 2 | 2 | 19 |
| Planet | 22 | 0 | 0 | 22 |
| **Total** | ~108 | **18 (17%)** | 11 | 79 |

> **Only ~17% of indicators are measurable by a fab lab with no external input — and they sit almost
> entirely in the Community row. The network owns the bottom row and almost nothing above it.**

This is not a flaw in the framework. It is an accurate map of where the network is strong and where it
must go and ask. Two consequences follow, and both are load-bearing:

**For the workshop.** The exercise is built on the Community row because that is where participants have
agency. Asking a table to estimate a bioregional indicator produces a guess; asking what they could pull
from their own repair log this month produces a commitment.

**For ingestion strategy.** At City and Region scale the job is not *measurement*, it is *relationship*.
The deliverable is not a sensor — it is knowing who owns the export and having their email.

### The way out: ten sources the network already owns

Not in the original theoretical sheet. Added afterwards precisely to close this gap — real, already
queryable sources the network itself controls, which feed City/Region/Bioregion cells without depending
wholly on official statistics:

| Source | Feeds | Effort |
|---|---|---|
| fablabs.io lab roster (50 km catchment) | Economic × City | low |
| Fab Academy alumni density | Economic/Social × City, Region, Bioregion | low |
| Precious Plastic chapter throughput (kg) | Economic × Community/City | low |
| Smart Citizen kit count + uptime | Environmental × Community/City | low |
| OpenStreetMap craft-tag density | Economic × Community/City | low |
| Community photo classification (waste, turbidity) | Environmental × Community/Bioregion | medium |
| Lab-operated drone mapping | Environmental × Community | medium |
| Decidim platform health | Governance × City | low |
| FAB/GOSH attendance from the bioregion | Social × Bioregion | low |
| Meshtastic sensor mesh (via `scripts/meshtastic_bridge.py`) | Environmental × Community | low — **wired, live** |

**Wiring two or three of these as live connectors is the highest-leverage engineering task on this
project.** Six are low-effort API calls against registries the network already runs.

---

## 4 · The design rules — do not "simplify" these away

These are the decisions that give the instrument whatever credibility it has. Each was made deliberately
and each has been attacked at least once as unnecessary complexity.

### Rule 1 · Three kinds of knowledge must never look alike

| Kind | What it is | Rendering |
|---|---|---|
| **Live** | Pulled from a connected API/webhook, refreshes itself | Solid colour, `live` tag |
| **Static** | A real value from a file or signed entry, frozen at its observation date | Solid colour, `static` tag |
| **Estimate** | Nobody has data; a person moved a slider | **Cross-hatched**, `estimate` tag |

A live measurement, a report figure, and somebody's honest guess are three different epistemic objects.
**An instrument that renders them identically is lying by design.** This is the soul of the thing.

### Rule 2 · Colour tracks the reading, never the weights

An earlier build tinted cells by their PITO/DIDO weight split. That was wrong: weights are fixed
properties of the methodology, so the matrix looked identical no matter what any city had measured.
Colour now tracks the **evidence attached to the cell** — the only thing that can actually move.

### Rule 3 · Grey means no data, and grey is fine

Unmeasured cells stay neutral rather than defaulting to a midpoint. **A cell honestly marked empty is
worth more than a cell confidently filled with a guess.** Most of the matrix is grey. That is the
accurate picture of where evidence stands, and the instrument's job is to show it.

### Rule 4 · Raw values in, normalisation in the open

Submissions carry the raw number plus the min/max range being scaled against — never a pre-computed
score. If someone converts 143 repairs to 0.7 in their own spreadsheet, the reasoning is lost and the
reading stops being auditable.

### Rule 5 · Direction is declared per indicator

Some indicators mean the opposite of others: more repairs is good, more imported tonnes is bad. Each
declares `dido` (higher is better) or `pito` (higher is worse); pito-direction values are **inverted**
during normalisation. This guarantees that on screen **green always means regenerative** and never
merely "big number".

### Rule 6 · Provenance is marked, always

Six cells carry weights **documented** in the upstream methodology. The other fourteen are
**reconstructed** here as a working proposal. Every cell says which it is. **Do not quietly promote
reconstructed weights to documented ones.**

### Rule 7 · Attribution is not aggregation

A lab can credibly report how many repairs it completed. It **cannot** infer from that figure that a city
or bioregion became sustainable. Local success does not automatically sum to global sustainability.
Keeping these apart is what protects the framework from the overstated claims that discredit most
metrics programmes.

### Rule 8 · Aggregation stops at the Region

Community → City → Region nest and add up. Bioregion and Planet are **boundary conditions** — watched as
limits, never rolled up. Why: no government sits at those scales that could take a score and act on it
fast enough to matter, and that speed *is* ρ. A region scoring well inside a bioregion already in
overshoot is not, in fact, scoring well.

---

## 5 · What is built

**Dashboard** — `index.html` + `assets/data.js`. Single file, no build step, no dependencies, no
framework. Deliberate: it still opens in five years, anyone can read it without tooling, and it can be
handed to a city as one file that works offline.

- 20 cells · 51 indicators, each with unit, direction, normalisation method, feasibility tier, source
- Three-tier reading system with enforced validation (no static reading saves without date + source)
- **Model engine (v0.5, from the exhibition console's logic):** a city is three axes (PITO, DIDO, ρ);
  each cell is their projection through its weights, `cell = (1−PITO)·w_pito + DIDO·w_dido`. Three view
  modes: **Evidence** (only attached readings; grey means no data), **Evidence + model** (measured cells
  stay fixed and least-squares-fit the axes; dark cells fill with cross-hatched `derived` projections — a
  fourth reading kind that is never saveable; measured cells show their Δ residual against the model,
  which is the matryoshka divergence indicator), and **Simulation** (the console's behaviour: three
  sliders, mock presets BCN/BOS/SCL/BALI/CEILING, everything badged SIMULATION · NOT A MEASUREMENT).
  A slider never overwrites a reading.
- FCI banner: formula always visible, 0–100 scale with the 37 ceiling marked, ρ settable only as a
  labelled estimate (no city has a measured ρ), hollow marker = ρ=1 upper bound, one-sentence
  plain-language narrative generated from the state, and the five-FCIs-by-scale matryoshka strip
- Phase plane: iso-FCI=0.37 ceiling curve, the fitted/simulated city with its ρ ring, Gen 1+2 points
- Workshop mode: dot the matrix green/yellow/dark, four-cell cap per table, card collection, CSV export
  (model completion is disabled while dotting — dots are commitments, not readings)
- Plain-language gloss on every technical term — the plain sentence first, technical second
- `scripts/smoke_test.js` — headless boot + model-math test (`node scripts/smoke_test.js index.html`)
- `data/weights.json` (generated by `scripts/gen_weights_json.js`) — the weight table made
  machine-readable, side by side with the exhibition console's table: they agree on 5 of 20 cells,
  which is the canonisation gap made visible
- `data/connectors.yaml` — this surface's connector manifest, same schema shape as the PLANETAI
  observatory's, cross-referencing `github.com/fabcity/awesome-fabcity-data` instead of a parallel inventory

**Team data pipeline** — `data/` + `scripts/`

- CSV template, worked example, machine-readable schema, submissions manifest
- Two ingestion paths: from the repo over http, or a local file picker (works offline)
- Row-by-row validation report — nothing fails silently
- `validate_submission.py` mirrors the dashboard's rules exactly, so a file that passes will load
- **Schema versioning** (`SCHEMA_VERSION` in `assets/data.js`, `schema_version` CSV column): minor
  mismatch warns and loads, major mismatch refuses — the model can now evolve without silently
  misreading old submissions
- **Session export/import** — readings, cards and the ρ estimate move between machines as one JSON;
  imports merge by observation date and never delete
- **Snapshot pipeline** — `.github/workflows/snapshots.yml` runs `scripts/fetch_snapshots.js` weekly:
  fablabs.io (→ Economic × City) and Smart Citizen active kits (→ Environmental × City) committed as
  dated JSON in `data/snapshots/`, loadable per pilot city from the Team data view as `static` readings.
  Git history of that folder is the provenance ledger. This resolves the roadmap's P1-connectors,
  P3-persistence and P3-ledger in one move — the frontend stays a dependency-free single file
- **Decision-record drafts** in `context/decisions/` — ρ-symbol canonisation and the canonical
  weights.json mechanism, in the PLANETAI format, status `proposed`, ready to circulate

**Context** — `context/`, 1,500+ lines plus original source documents

---

## 6 · What is *not* built — read before promising anything

**ρ is not computed for any city.** The term is defined and explained; no pilot has a measured value, and
the protocol itself is v0 upstream (tier-weighting and council-rejection handling are open). **Until ρ
exists, no city has a complete FCI number, and the dashboard says so rather than inventing one.**

**Live connectors are half-built.** The interface accepts an endpoint, JSON path and scaling range, and
fetches on demand. It does **not** refresh on a schedule — that needs a server-side component. Browser
CORS also blocks many public endpoints.

**No sovereignty gate.** The upstream design has community-tier data publishing only with local-authority
consent (in Bali, a three-body Tri Hita Karana flow — which is a *design*, not an agreement in force).
This dashboard documents the gate but does not enforce it, because it has no accounts or roles.
**Anything handling real community data must implement this before publishing.**

**Twelve of twenty cells are meaningfully populated upstream.** Region tier and Governance × Bioregion /
× Region are thinnest.

**Three weight cells are contested:** Economic × Bioregion (0.8/0.2), Environmental × Community
(0.5/0.5), Economic × Community (0.3/0.7). All flagged upstream for sharpened argument.

**The Full Stack Metrics Framework [Vivanco 2024] is a working paper** plus a 2025 doctoral thesis — not peer-reviewed in its own right. (Canonical naming, per the PLANETAI project context: the framework is referred to by name in body text, with [Vivanco 2024] as citation — never "Vivanco's matrix".)

---

## 7 · The workshop (WS3, FAB26 Boston)

Three moves, 17 minutes. The dashboard serves each one.

**1 · Dot the matrix (7 min).** Scan twenty cells, dot only the **3–4 you actually know**. Green = you
could pull it *this month*. Yellow = exists but locked. Dark = leave it.
*The classic mistake is over-claiming green.* Push back: "could you pull it this month?" Ask who actually
has hands on the source — often not the enthusiast in the room. The dashboard caps a table at four cells
and says why, so the rule enforces itself.

**2 · Pick ONE cell (5 min).** Not the easiest — the one that matters and is reachable in 30 days. Open
it and read the indicators: unit, method, who feeds it. That converts "we should measure repairs" into
"143 units/month, from the repair log, scaled against a stated ceiling."

**3 · Fill the card (5 min).** One cell · one source · one name · one date · plus the first step and the
real day it happens. *"Email the data officer, Aug 4" is a first step. "Explore options" is not.*
All cards land in one collection sheet the facilitator can read out, copy or export.

**Hard gate at minute 40:** markers down, one cell you can defend and one email you will send.

---

## 8 · Where to take it next

Ordered by leverage.

**1. Wire two or three network-own connectors.** fablabs.io, Smart Citizen, Precious Plastic. Low effort,
they are the network's own registries, and they light up City/Region cells that are otherwise dark.
Highest ratio of impact to work in the whole project.

**2. Formalise the Boeing recovery.** A worked Hamburg example on public NACE/COICOP data. Closes the
most predictable reviewer objection and secures the lineage argument.

**3. Draft the ρ protocol to v1.** Without it the index stays a snapshot rather than a metabolism —
and the metabolism *is* the contribution.

**4. Run WS3 and ingest the real submissions.** Replace the example file with actual city data. The
pipeline is built and tested; it needs contact with reality.

**5. Sharpen the three contested weight cells,** or document why they should stay as they are.

**6. Implement the sovereignty gate** before any real community data is published. This is a
prerequisite, not an enhancement.

**Full gap analysis:** [`context/07-professionalisation-roadmap.md`](context/07-professionalisation-roadmap.md)
lists every gap between this build and a production-grade instrument — evidence, engineering, interface,
communication and governance — prioritised, with the capability that handles each.

### Two decisions waiting on the Foundation

**Which domain is canonical.** The workshop deck points to `index.fab.city`; this build was developed
against `staging.fci-index.pages.dev`. Update `META.siteUrl` in `assets/data.js` once settled.

**Whether the reconstructed weights become canon.** Fourteen of twenty cells carry weights proposed here.
If the Foundation publishes a machine-readable weight table, replace them and flip `wSource` to `"site"`.

---

## 9 · How to work on it

```bash
git clone https://github.com/tomasvivanco/FC_MetricsDashboard.git
cd FC_MetricsDashboard
python3 -m http.server 8000        # then open http://localhost:8000
```

No build, no install, no dependencies.

**If you change the data model** (`assets/data.js`), regenerate the reference:

```bash
node scripts/gen_datamodel_doc.js
```

**If you change an indicator's `name`, `unit` or `direction`,** run the validator — submissions bind to
those strings:

```bash
python3 scripts/validate_submission.py
```

**Contributing rules:** keep it dependency-free and readable without tooling. Any new number declares its
provenance and normalisation. Preserve the visual distinction between measurement and estimate — it is
the point, not decoration.

---

## 10 · Sources

Three, kept distinguishable everywhere in code and interface:

- **[A]** [FCI 3.0 prototype](https://staging.fci-index.pages.dev) — matrix, methodology, atlas, phase
  plot, operator workbench. Methodology v0, beta.
- **[B]** Vivanco, T. *Fab City Full Stack Metrics Framework: An Actionable Methodology for Multi-Scalar
  Implementation.* FAB26 working paper, Fab City Foundation / PUC Chile.
- **[C]** Diez, T., Charny, D., & Kohtala, C. (2024). *The Fab City Full Stack.* Fab City Foundation.
  [10.5281/zenodo.10492629](https://doi.org/10.5281/zenodo.10492629)

Standing on: Florentin, Chabanel & Guimas (Utopies, 2018) · Boeing (Springer, 2024) · Peuckert,
Wenzelmann & Rüdebusch (2025) · Rockström et al. (2009) · Steffen et al. (2015) · Richardson et al.
(2023) · Raworth (2017) · Meadows (2008).

Original documents in `context/sources/`. Deeper detail in `context/01`–`06`.

---

## The one-sentence version

> **The matrix has twenty cells and most of them are dark — and that is not a weakness, it is the map of
> the work.**

---

*Fab City Foundation research and operations · working build · comments to `index@fab.city`*
