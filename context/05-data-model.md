written: 613 lines
reference

> **Generated from `assets/data.js`.** Do not edit by hand — regenerate with
> `node scripts/gen_datamodel_doc.js > context/05-data-model.md` after changing the model.

The file `assets/data.js` is the single source of truth for the dashboard. It defines no behaviour —
only structure, content and provenance. Everything the interface renders comes from here.

## Top-level exports

| Constant | What it holds |
|---|---|
| `META` | Version, methodology status, upstream counts, disclaimer |
| `SCALES` | The five territorial tiers, with aggregation rule and plain-language gloss |
| `PILLARS` | The four impact dimensions |
| `DATA_STATES` | Upstream data vocabulary: live · partial · mock · placeholder |
| `READING_KINDS` | How a reading got here: live · static · estimate — and what each counts as |
| `FEEDER_META` | Who produces the data: lab · mixed · institutional · fixed |
| `SOVEREIGNTY` | The per-scale audit of who can measure what |
| `NETWORK_SOURCES` | Nine network-own data sources |
| `FEASIBILITY` | High / medium / low tiers with definitions |
| `CELLS` | The twenty cells and their indicators — the core of the model |
| `METHODOLOGY` | Formula, terms, Boeing recovery, aggregation, open gaps |
| `SIM` | Exhibition-console layer: mock archetypes, console weight table (comparison only), narrative bands |
| `FULL_STACK_LAYERS` | The seven layers |
| `INGESTION_ROUTES` | The four ways data enters |
| `CSV_SCHEMA` | Submission column definitions |
| `DATA_HYGIENE` | Seven rules for usable data |
| `REVIEW_PIPELINE` | What happens to an uploaded file |
| `CITIES` | Pilot cities and reconstructed Generation 1/2 points |
| `WORKSHOP` | WS3 stakes, steps and dashboard role |

## Cell schema

Each entry in `CELLS` is keyed `pillar:scale` (e.g. `environmental:community`) and carries:

```js
"environmental:community": {
  pito: 0.5,              // PITO weight — throughput side. pito + dido === 1
  dido: 0.5,              // DIDO weight — capacity side
  wSource: "site",        // "site" = documented upstream | "reconstructed" = proposed here
  underReview: true,      // flagged upstream for sharpened argument before weights harden
  dataState: "mock",      // upstream state: live | partial | mock | placeholder
  feeder: "lab",          // who produces it: lab | mixed | institutional | fixed
  boundary: false,        // true = read as a limit, never aggregated upward
  generation12: false,    // true only for the Economic × City / Region cell
  thin: false,            // flagged upstream as one of the thinnest cells
  question: "...",        // the plain-language question this cell answers
  note: "...",            // provenance and methodological caveats
  indicators: [ ... ]     // see below
}
```

### Indicator schema

```js
{
  name: "Products repaired",      // must match submissions exactly — CSVs bind to this string
  unit: "units / month",          // the unit of the RAW value, not of the 0–1 reading
  direction: "dido",              // "dido" = higher is better | "pito" = higher is worse (inverted on normalise)
  feasibility: "high",            // high | medium | low
  norm: "...",                    // how the raw value becomes 0–1, stated so it can be disagreed with
  source: "..."                   // where this number typically comes from
}
```

**`direction` is the one to get right.** Normalisation orients every reading so that **1 is always
regenerative (green)** and 0 always extractive (red). A `pito`-direction indicator is inverted:
80 tonnes imported on a 0–100 scale becomes a reading of 0.20, not 0.80.

## Vocabularies

### Reading kinds

| Key | Label | Counts as | Rendering |
|---|---|---|---|
| `live` | Live | Measurement | solid colour |
| `static` | Static | Measurement | solid colour |
| `estimate` | Estimate | Judgement — not evidence | **cross-hatched** |
| `derived` | Derived | Model projection — not evidence | solid colour |

### Feeder categories

| Key | Label | Meaning |
|---|---|---|
| `lab` | Hub-fed | The hub — lab plus its community — produces this directly |
| `mixed` | Mixed | The lab supplies part; the rest needs external data |
| `institutional` | External | Requires a statistical agency, government, or international database |
| `fixed` | Boundary | Planetary or ecological reference — travels down, never up |

### Feasibility tiers

| Key | Label | Meaning |
|---|---|---|
| `high` | High | You could pull this from records you already keep, this month. |
| `medium` | Medium | It exists, but somebody has to formalise how it gets recorded first. |
| `low` | Low | Needs real instruments or a proper survey. Plan it, don't promise it. |

### Upstream data states

| Key | Label | Meaning |
|---|---|---|
| `live` | Live | A wired source that refreshes on its own. Nobody retypes it. |
| `partial` | Partial | Some indicators in this cell are real, others are still samples. |
| `mock` | Mock | Sample values, standing in so the structure can be seen. Not a measurement. |
| `placeholder` | Placeholder | No source wired yet. Methodology v0 has not defined an indicator here. |

## Submission columns

| Column | Required | Example | Purpose |
|---|---|---|---|
| `cell` | **yes** | `environmental:community` | Which of the twenty parts of city life this belongs to. Pillar and scale, separated by a colon. |
| `indicator` | **yes** | `Products repaired` | Exactly what was counted. Use the indicator name listed in the cell. |
| `value` | **yes** | `143` | The raw number as measured. Do not pre-convert it to 0–1 — the platform normalises. |
| `unit` | **yes** | `units/month` | The unit the number is in. Without this the value cannot be normalised or compared. |
| `observation_date` | **yes** | `2026-06-30` | When the measurement refers to (not when you typed it). ISO format, YYYY-MM-DD. |
| `source` | **yes** | `Repair café log, Barcelona Sants` | Where it came from, specific enough that somebody else could go and check. |
| `scale_min` | **yes** | `0` | The bottom of the range you are scaling against — the raw value that would count as 0. State it so your normalisation is auditable. |
| `scale_max` | **yes** | `200` | The top of that range — the raw value that would count as 1. A practical ceiling, a peer benchmark, or a science-based target. |
| `team` | no | `Table 4 — Boston` | Who submitted this. Used to attribute the reading back to your table. |
| `method` | no | `Manual count at close of each session` | How it was collected. Optional, but this is what makes the number auditable a year from now. |
| `geography` | no | `Sants-Montjuïc district` | The exact area the number covers, if narrower than the cell's scale. |
| `confidence` | no | `high` | Your own honest read: high, medium, or low. Low-confidence rows go to review rather than committing. |
| `notes` | no | `Two sessions cancelled in June; undercount likely` | Anything a reader would need to know to not misread the number. |
| `schema_version` | no | `1.1` | Which version of the indicator schema this file was written against (see SCHEMA_VERSION in assets/data.js). Optional, but it is what lets the pipeline warn you instead of silently misreading your file when the model evolves. |

---

## The twenty cells

**20 cells · 54 indicators.** Feeder split: 4 lab, 7 mixed, 5 institutional, 4 fixed. Feasibility split: 19 high, 23 medium, 12 low.

### Environmental

*Material and energy: what comes in, what goes out, what it costs the ecosystem.*

#### `environmental:community` — Environmental × Community

> Is this neighbourhood keeping material in use instead of throwing it away?

| | |
|---|---|
| Weights | PITO 0.50 · DIDO 0.50 |
| Weight provenance | documented upstream |
| Upstream data state | Mock |
| Who feeds it | Hub-fed — The hub — lab plus its community — produces this directly |
| Flags | ⚠ weight under review |

One of three cells the FCI 3.0 methodology explicitly flags for sharpened argument before the v0 weights harden — the 0.5/0.5 split is contested.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Material reused or recycled locally | `kg / month` | higher = better | High | Lab intake and repair logs |
| Products repaired | `units / month` | higher = better | High | Repair-café and workshop records |
| Waste diverted from landfill | `% of stream` | higher = better | Medium | Municipal collection data cross-checked with lab records |
| Renewable energy consumed | `% of lab load` | higher = better | Medium | Utility bills / submetering |
| Neighbourhood sensing uptime | `% of last 24 h` | higher = better | High | Meshtastic mesh via local bridge (scripts/meshtastic_bridge.py) — hub-own instrument |

- **Material reused or recycled locally** → Share of total material throughput diverted locally; 0 = none diverted, 1 = diversion at the practical ceiling agreed for the lab's catchment.
- **Products repaired** → Repairs per 1,000 catchment residents, min-max scaled against network peer labs.
- **Waste diverted from landfill** → Direct percentage, used as-is (already 0–1).
- **Renewable energy consumed** → Direct percentage of the facility's own consumption.
- **Neighbourhood sensing uptime** → Share of the last 24 hours in which the community's own sensor mesh delivered environment telemetry (5-minute buckets with at least one reading). Direct percentage. Measures the capacity to know your own air — the raw temperature/humidity/pressure values travel alongside but are not the indicator.

#### `environmental:city` — Environmental × City

> How much material and energy does the whole city pull in, and what does it emit?

| | |
|---|---|
| Weights | PITO 0.70 · DIDO 0.30 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Partial |
| Who feeds it | Mixed — The lab supplies part; the rest needs external data |

Reconstructed from [B]'s environmental pillar (material flows, energy/climate, ecosystem impacts, pollution) at city scale. In the Barcelona pilot the Smart Citizen sensor network is the first live source targeted here.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Domestic material consumption | `tonnes / capita / yr` | higher = worse | Medium | Urban material flow accounting (Eurostat-compatible MFA) |
| Territorial GHG emissions | `tCO₂e / capita / yr` | higher = worse | Medium | Municipal climate inventory |
| Air and water quality sensing coverage | `sensors / km²` | higher = better | High | Smart Citizen / municipal sensor fleet |
| Community sensors reporting | `active kits / 20 km` | higher = better | High | Smart Citizen API — network-own source, snapshot pipeline |

- **Domestic material consumption** → Inverted and min-max scaled against a bioregional sustainable-throughput benchmark; higher consumption drives the reading toward 0.
- **Territorial GHG emissions** → Inverted, scaled against the city's own science-based trajectory for the year.
- **Air and water quality sensing coverage** → Coverage against a target density; caps at 1 once the city can resolve neighbourhood-level variation.
- **Community sensors reporting** → Kits with a reading in the last 30 days within 20 km, scaled against a practical ceiling of 50 (proposed). Counts only kits actually reporting — the Barcelona archive audit found ~98% dormant, and counting the dormant ones flatters the indicator.

#### `environmental:region` — Environmental × Region

> Do the material flows across this whole region balance, or is the city exporting its problems next door?

| | |
|---|---|
| Weights | PITO 0.70 · DIDO 0.30 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Mock |
| Who feeds it | External — Requires a statistical agency, government, or international database |

Regional material flows and cross-jurisdiction ecological pressure. Reconstructed — the FCI 3.0 methodology names the Region tier as among its thinnest.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Regional material flow balance | `import : local ratio` | higher = worse | Low | Regional statistical accounts, MFA |
| Cross-jurisdiction emissions accounting | `% of flows accounted` | higher = better | Medium | Regional environment agency |

- **Regional material flow balance** → Inverted ratio; 1 when regional supply meets regional demand for the tracked material classes.
- **Cross-jurisdiction emissions accounting** → Share of inter-municipal flows that are actually measured rather than estimated.

#### `environmental:bioregion` — Environmental × Bioregion

> Is the natural region this city sits in still able to regenerate what the city takes?

| | |
|---|---|
| Weights | PITO 0.85 · DIDO 0.15 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Mock |
| Who feeds it | Mixed — The lab supplies part; the rest needs external data |
| Flags | boundary — not aggregated |

Boundary layer. Read as a limit the city's score has to live within — never aggregated upward. A region scoring well inside a bioregion in overshoot is not scoring well.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Watershed carrying capacity utilisation | `% of renewable supply` | higher = worse | Low | Basin authority / hydrological modelling |
| Biodiversity corridor integrity | `% connectivity retained` | higher = better | Low | Ecoregional assessment, remote sensing |

- **Watershed carrying capacity utilisation** → Inverted; 1 = withdrawal well inside renewable recharge, 0 = structural overshoot.
- **Biodiversity corridor integrity** → Landscape connectivity index, used directly.

#### `environmental:planet` — Environmental × Planet

> Where does this city's footprint sit against the planet's hard limits?

| | |
|---|---|
| Weights | PITO 0.90 · DIDO 0.10 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Mock |
| Who feeds it | Boundary — Planetary or ecological reference — travels down, never up |
| Flags | boundary — not aggregated |

Planetary boundary horizon (Rockström et al. 2009; Steffen et al. 2015; Richardson et al. 2023 — six of nine boundaries now crossed). A reference frame, not a reporting unit.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Planetary boundary status | `count of 9 transgressed` | higher = worse | Low | Earth-system science literature |
| Consumption-based material footprint | `tonnes / capita / yr` | higher = worse | Low | Multi-regional input-output models |

- **Planetary boundary status** → Global scientific reference, downscaled only as context. Not a city-level performance measure.
- **Consumption-based material footprint** → Inverted against a globally equitable per-capita share.

### Social

*People: who takes part, who learns, who is included, who is left out.*

#### `social:community` — Social × Community

> Are more people here gaining the skills and access to make things themselves?

| | |
|---|---|
| Weights | PITO 0.20 · DIDO 0.80 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Mock |
| Who feeds it | Hub-fed — The hub — lab plus its community — produces this directly |

The highest-feasibility cell in the whole matrix: [B] §5.4 identifies participation and training as measurable directly from records a lab already keeps.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Participation in making activities | `unique people / month` | higher = better | High | Workshop attendance sheets |
| Skills training sessions delivered | `sessions / month` | higher = better | High | Programme calendar |
| Skills acquired and retained | `% of participants certified` | higher = better | Medium | Post-course assessment |
| Equity of access | `% from under-represented groups` | higher = better | Medium | Voluntary self-reported registration data |

- **Participation in making activities** → Per 1,000 catchment residents, min-max scaled against network peers.
- **Skills training sessions delivered** → Scaled against the lab's own stated programme capacity.
- **Skills acquired and retained** → Direct percentage; requires a follow-up protocol to be meaningful.
- **Equity of access** → Participation share compared to the catchment's demographic baseline; 1 = parity or better.

#### `social:city` — Social × City

> Can everyone in this city reach a place where they could make or repair something?

| | |
|---|---|
| Weights | PITO 0.30 · DIDO 0.70 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Mock |
| Who feeds it | External — Requires a statistical agency, government, or international database |

Health and wellbeing, equity and inclusion, employment, community and culture at city scale ([B] §4, social pillar).

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Population within 2 km of a maker facility | `% of residents` | higher = better | Medium | Municipal facility registry + census geography |
| Employment in distributed manufacturing and repair | `jobs / 10,000 residents` | higher = better | Medium | Labour statistics, NACE/NAICS classes |
| Spatial equity of access | `Gini of facility access` | higher = worse | Low | Spatial analysis of facility registry |

- **Population within 2 km of a maker facility** → Direct percentage from spatial analysis.
- **Employment in distributed manufacturing and repair** → Min-max scaled against comparable cities.
- **Spatial equity of access** → Inverted Gini; 1 = access evenly distributed across districts.

#### `social:region` — Social × Region

> Do skills and people actually move between the cities of this region?

| | |
|---|---|
| Weights | PITO 0.30 · DIDO 0.70 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Mock |
| Who feeds it | External — Requires a statistical agency, government, or international database |
| Flags | among the thinnest cells |

Among the thinner cells. The Region tier is named in the FCI 3.0 open gaps as under-instrumented.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Inter-municipal skills programmes | `count of active programmes` | higher = better | Medium | Regional development agency |
| Workforce mobility | `% commuting across municipal lines` | higher = better | Medium | Census commuting matrices |

- **Inter-municipal skills programmes** → Scaled against the number of municipalities in the region.
- **Workforce mobility** → Used as a proxy for functional regional integration.

#### `social:bioregion` — Social × Bioregion

> Is the knowledge that belongs to this territory being recognised and kept alive?

| | |
|---|---|
| Weights | PITO 0.40 · DIDO 0.60 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Mock |
| Who feeds it | Mixed — The lab supplies part; the rest needs external data |
| Flags | boundary — not aggregated |

Boundary-layer social reading. Handle with the ethics of [B] §15: research must not be extractive, and community knowledge is not the Foundation's to publish.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Traditional and Indigenous knowledge integration | `qualitative rubric 0–4` | higher = better | Low | Co-produced assessment with customary authorities |
| Bioregional place attachment | `survey index` | higher = better | Low | Periodic population survey |

- **Traditional and Indigenous knowledge integration** → Participatory rubric scored with, never about, the communities concerned. Sovereignty-gated.
- **Bioregional place attachment** → Validated survey instrument required before this yields comparable data.

#### `social:planet` — Social × Planet

> Is what this city learns being shared back so anyone else can use it?

| | |
|---|---|
| Weights | PITO 0.30 · DIDO 0.70 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Mock |
| Who feeds it | Boundary — Planetary or ecological reference — travels down, never up |
| Flags | boundary — not aggregated |

Full Stack Layer 7 — global knowledge exchange. This is the layer that makes a local fix reusable in another bioregion.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Open documentation published | `designs / yr with open licence` | higher = better | High | Repository records, lab documentation practice |
| Reuse of local designs elsewhere | `forks / downloads by other nodes` | higher = better | Medium | Repository telemetry |

- **Open documentation published** → Scaled against projects completed — i.e. what share of work is actually documented and shared.
- **Reuse of local designs elsewhere** → Min-max scaled across the network.

### Economic

*Value: what is made locally, what is imported, where the money stays.*

#### `economic:community` — Economic × Community

> Does making and repairing here actually keep value in the neighbourhood?

| | |
|---|---|
| Weights | PITO 0.30 · DIDO 0.70 |
| Weight provenance | documented upstream |
| Upstream data state | Mock |
| Who feeds it | Hub-fed — The hub — lab plus its community — produces this directly |
| Flags | ⚠ weight under review |

Flagged in FCI 3.0 methodology §3 as needing sharpened argument before the weights harden.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Value of goods produced locally | `currency / month` | higher = better | Medium | Lab production records with unit costing |
| Savings from repair and reuse | `currency / month avoided` | higher = better | High | Repair logs with replacement-cost lookup |
| Local jobs and livelihoods created | `FTE` | higher = better | Medium | Lab employment and spin-out records |

- **Value of goods produced locally** → Scaled against the equivalent imported-goods cost the production displaces.
- **Savings from repair and reuse** → Replacement cost avoided, min-max scaled against peers.
- **Local jobs and livelihoods created** → Per 1,000 catchment residents.

#### `economic:city` — Economic × City

> How much of what this city consumes can it actually produce itself?

| | |
|---|---|
| Weights | PITO 0.50 · DIDO 0.50 |
| Weight provenance | documented upstream |
| Upstream data state | Partial |
| Who feeds it | Mixed — The lab supplies part; the rest needs external data |
| Flags | **GENERATION 1+2 CELL** |

THE GENERATION 1+2 CELL. This single cell is what Utopies measured for ~600 French urban areas (Paris 37.58, 2018) and what Boeing measured for Hamburg (37.00, 2024). Two independent statistical systems, six years apart, same number — the public-data ceiling, a property of global supply-chain geometry rather than of either city. The other 19 cells are the surface area FCI 3.0 adds.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Local production self-sufficiency | `% of consumption met locally` | higher = better | Medium | NACE/COICOP economic accounts; Metroverse ECI as proxy |
| Import dependency | `% of demand imported` | higher = worse | Medium | Regional trade and input-output accounts |
| Economic complexity | `ECI index` | higher = better | High | Metroverse / Harvard Growth Lab |
| Fab lab density in catchment | `labs / 50 km catchment` | higher = better | High | fablabs.io registry — network-own source, snapshot pipeline |

- **Local production self-sufficiency** → Boeing's discipline: priority × self-sufficiency by consumption class. Direct percentage.
- **Import dependency** → Inverted percentage — the mirror of the indicator above, kept separate for auditability.
- **Economic complexity** → Min-max scaled across the peer set; a proxy for the diversity of what a place knows how to make.
- **Fab lab density in catchment** → Count of registered labs within 50 km, scaled against a practical ceiling of 25 (network peer benchmark, proposed). Distributed-production capacity the network itself can verify.

#### `economic:region` — Economic × Region

> Can this region supply itself, or does everything come from outside it?

| | |
|---|---|
| Weights | PITO 0.50 · DIDO 0.50 |
| Weight provenance | documented upstream |
| Upstream data state | Partial |
| Who feeds it | Mixed — The lab supplies part; the rest needs external data |
| Flags | **GENERATION 1+2 CELL** |

The same Generation 1+2 measurement read at regional scope. Which of City or Region carries it depends on the data scope available in that pilot.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Regional economic diversification | `ECI / diversity index` | higher = better | High | Metroverse, national statistical institutes |
| Supply-chain integration | `% of inputs sourced in-region` | higher = better | Low | Regional input-output accounts |

- **Regional economic diversification** → Min-max scaled across comparable regions.
- **Supply-chain integration** → Direct percentage from input-output tables where they exist.

#### `economic:bioregion` — Economic × Bioregion

> How much of this bioregion's economy depends on pulling material from outside it?

| | |
|---|---|
| Weights | PITO 0.80 · DIDO 0.20 |
| Weight provenance | documented upstream |
| Upstream data state | Mock |
| Who feeds it | Boundary — Planetary or ecological reference — travels down, never up |
| Flags | ⚠ weight under review · boundary — not aggregated |

Third of the three cells FCI 3.0 flags for sharpened argument. The 0.8/0.2 split is the most contested in the v0 table.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Bioregional material dependency | `% of material imported into the bioregion` | higher = worse | Low | Bioregional accounts where they exist; otherwise documented proxy |
| Cross-boundary trade intensity | `tonnes / capita crossing the boundary` | higher = worse | Low | Freight and customs statistics |

- **Bioregional material dependency** → Inverted percentage.
- **Cross-boundary trade intensity** → Inverted, scaled against comparable bioregions.

#### `economic:planet` — Economic × Planet

> What does global supply-chain structure allow any city to achieve at all?

| | |
|---|---|
| Weights | PITO 0.75 · DIDO 0.25 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Mock |
| Who feeds it | Boundary — Planetary or ecological reference — travels down, never up |
| Flags | boundary — not aggregated |

The structural ceiling itself, as an explicit horizon. This is the cell that explains why Paris and Hamburg both landed on ~37 without either city failing.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Global value-chain dependency | `index` | higher = worse | Low | Multi-regional input-output literature |
| Distributed manufacturing capacity worldwide | `count of active nodes` | higher = better | High | Fab Foundation network registry |

- **Global value-chain dependency** → Reference frame only — establishes the ceiling against which city readings are interpreted.
- **Distributed manufacturing capacity worldwide** → Network-level count (2,700+ fab labs) used as context.

### Governance

*Decisions: who decides, how openly, how fast a reading becomes an action.*

#### `governance:community` — Governance × Community

> Do people here meet, decide together, and write down what they learned?

| | |
|---|---|
| Weights | PITO 0.10 · DIDO 0.90 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Mock |
| Who feeds it | Hub-fed — The hub — lab plus its community — produces this directly |

[B] argues governance is not one pillar among four but the condition for the other three: without regular meetings, clear responsibilities and documented protocols, the environmental, social and economic metrics cannot be maintained at all.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Council or assembly meetings held | `meetings / quarter` | higher = better | High | Meeting calendar — a record almost every lab already keeps |
| Meeting attendance | `% of members` | higher = better | High | Attendance records |
| Institutional partnerships active | `count` | higher = better | High | Partnership agreements on file |
| Knowledge documented and shared | `% of projects documented` | higher = better | High | Project repository |

- **Council or assembly meetings held** → Against the governance cadence the group itself committed to.
- **Meeting attendance** → Direct percentage.
- **Institutional partnerships active** → Min-max scaled against peer labs.
- **Knowledge documented and shared** → Direct percentage of completed projects with published documentation.

#### `governance:city` — Governance × City

> Is city data open enough that anyone could check this score — and does the city act on it?

| | |
|---|---|
| Weights | PITO 0.15 · DIDO 0.85 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Partial |
| Who feeds it | Mixed — The lab supplies part; the rest needs external data |

Institutional capacity, data availability, transparency. In the Barcelona pilot the Open Data Portal is the named source. This cell is also where ρ (how fast a reading becomes an action) is most directly observable.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Open data infrastructure | `% of relevant datasets published openly` | higher = better | High | Municipal open-data portal catalogue |
| Observation-to-action latency | `days from reading to fitted response` | higher = worse | Medium | Council decision logs cross-referenced with monitoring records |
| Institutional transparency | `rubric 0–4` | higher = better | Medium | Structured assessment of published governance records |

- **Open data infrastructure** → Direct percentage against a defined list of index-relevant datasets.
- **Observation-to-action latency** → Inverted and scaled against a pre-registered response budget. This is the ρ input.
- **Institutional transparency** → Documented rubric on publication, revision history, and machine readability.

#### `governance:region` — Governance × Region

> Do the cities in this region actually share data and align their rules?

| | |
|---|---|
| Weights | PITO 0.20 · DIDO 0.80 |
| Weight provenance | documented upstream |
| Upstream data state | Mock |
| Who feeds it | Mixed — The lab supplies part; the rest needs external data |
| Flags | among the thinnest cells |

Named in FCI 3.0 methodology §7 as one of the two thinnest cells in the matrix, alongside Governance × Bioregion.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Inter-city policy alignment | `count of harmonised instruments` | higher = better | Medium | Regional governance records |
| Regional data-sharing agreements | `count in force` | higher = better | Medium | Inter-municipal agreements register |

- **Inter-city policy alignment** → Scaled against the number of municipalities in the region.
- **Regional data-sharing agreements** → Scaled against the number of index-relevant domains.

#### `governance:bioregion` — Governance × Bioregion

> Is anyone actually governing at the scale of the watershed?

| | |
|---|---|
| Weights | PITO 0.20 · DIDO 0.80 |
| Weight provenance | documented upstream |
| Upstream data state | Mock |
| Who feeds it | External — Requires a statistical agency, government, or international database |
| Flags | among the thinnest cells |

The other thinnest cell per methodology §7. It matters because the honest answer is usually 'no' — and that absence is precisely why bioregion cannot aggregate into a score.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Bioregional governance bodies active | `count (watershed councils etc.)` | higher = better | Medium | Basin authority and ecoregional governance registries |
| Cross-jurisdiction monitoring agreements | `count in force` | higher = better | Medium | Environmental agency agreements |

- **Bioregional governance bodies active** → Presence and mandate strength against a documented rubric.
- **Cross-jurisdiction monitoring agreements** → Scaled against the jurisdictions sharing the bioregion.

#### `governance:planet` — Governance × Planet

> Is this city part of the global commons that shares how to fix things?

| | |
|---|---|
| Weights | PITO 0.15 · DIDO 0.85 |
| Weight provenance | **reconstructed** — working proposal |
| Upstream data state | Mock |
| Who feeds it | External — Requires a statistical agency, government, or international database |
| Flags | boundary — not aggregated |

Layer 7 plus what [B] calls planetary computation (Vivanco 2025): local readings becoming globally readable, collectively governed knowledge — measurement as participation in a planetary feedback system rather than as reporting.

| Indicator | Unit | Direction | Feasibility | Typical source |
|---|---|---|---|---|
| Participation in open-data commons | `count of shared datasets` | higher = better | High | Federation node records |
| Multilateral environmental engagement | `count of active commitments` | higher = better | Medium | International agreement registries |

- **Participation in open-data commons** → Scaled against the city's own index-relevant dataset count.
- **Multilateral environmental engagement** → Documented commitments with reporting obligations actually met.

---

*Generated from `assets/data.js` · v0.5 — model completion build*
