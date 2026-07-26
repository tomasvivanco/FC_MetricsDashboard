# 04 · Data sovereignty audit — who can actually produce each number

**If you read one context file, read this one.** It is the empirical finding that shapes the workshop
design, the ingestion priorities, and the argument the whole instrument makes.

Source: `sources/WS3_Planilla_Metricas_FabLab_vs_Externo.md`, derived from
`sources/3. Detailed Metrics.docx` (Vivanco's full ~95-indicator sheet).

## The question

Vivanco's Detailed Metrics sheet defines roughly 95–108 indicators across five scales and four pillars.
It describes what *should* be measured. It does not ask who *can* measure it.

So we went indicator by indicator and asked one blunt question: **who actually produces this number?**

Three answers:

| | Category | Meaning |
|---|---|---|
| 🔧 | **Lab-fed** | The lab or community generates it directly — logs, sensors, its own surveys, workshop records. No permission needed, no external dependency. |
| ⚖️ | **Mixed** | The lab can contribute a real input — a sub-sample, a proxy, its own sensors densifying an official network — but the complete indicator still needs somebody else's dataset. |
| 🌐 | **External** | Requires a statistical agency, municipal or regional government, or an international database. The lab does not measure this and will not. |

## The result

| Scale | Indicators | 🔧 Lab | ⚖️ Mixed | 🌐 External | Verdict |
|---|---|---|---|---|---|
| **Community** | 21 | **16** | 4 | 0 | Maximum data sovereignty. The network can act alone. |
| **City** | 21 | 0 | 2 | 19 | Most dependent on official statistics. |
| **Region** | 21 | 0 | 3 | 18 | The lab does not instrument this scale. |
| **Bioregion** | 23 | 2 | 2 | 19 | A context scale, not an ingestion scale. |
| **Planet** | 22 | 0 | 0 | 22 | 100% external, without exception. |
| **Total** | **~108** | **18** | **11** | **79** | |

> **Only ~18 of ~95–108 indicators (17%) can be measured by a fab lab with no external input — and they
> are almost entirely concentrated in the Community row.**

## What this means

**The Fab City network holds real data sovereignty over exactly one horizontal strip of the matrix.**
Everything above Community depends, in greater or lesser degree, on public or institutional statistics.

This is not a flaw in the framework. It is an accurate map of where the network is currently strong and
where it has to go and ask. Two consequences follow directly:

**For the workshop.** The exercise is built on the Community row because that is where participants have
agency. Asking a table to estimate a bioregional indicator produces a guess; asking them what they could
pull from their own repair log this month produces a commitment. This is why WS3's practical block sits
where it sits — this audit is the methodological justification for that choice.

**For ingestion strategy.** At City and Region scale the job is not *measurement*, it is *relationship*.
The deliverable is not a sensor, it is knowing who owns the export and having their email. The dashboard
reflects this: cells are labelled by who feeds them, so a participant can see at a glance whether a cell
is theirs to measure or theirs to go and ask for.

## Scale-by-scale detail

**Community — the scale where the fab lab IS the source.** 16 of 21 direct. Nearly the entire indicator
set was designed with the lab itself in mind: material reused, products repaired, waste diverted,
participation, training sessions, skills acquired, community satisfaction, value of goods produced,
savings from repair, meetings held, partnerships, documented knowledge. The four mixed ones are energy
(the lab meters consumption; the renewable share is grid-dependent), local jobs, and revenue retained.

**City — 19 of 21 external.** Sectoral self-sufficiency, material consumption, recycling rate, GHG
emissions, urban metabolism, green space, unemployment, Gini, life expectancy, housing, GDP, business
density, R&D, policy coherence, budget allocation, open data availability. The network's only native
inputs: **air quality** (Smart Citizen kits densify the official monitoring network) and **citizen
engagement** (participation on Decidim-style platforms the lab can promote and record).

**Region — 18 of 21 external.** The lab does not instrument this scale. Its three mixed contributions are
innovation ecosystems (the network's own cluster counts as one data point inside a wider mapping),
regional data sharing (fablabs.io is itself an instance of federated open data), and multi-stakeholder
forums (Fab City network forums count as one such forum).

**Bioregion — 19 of 23 external.** A context scale. The only direct contributions are **environmental
education** and **stewardship participation** the lab itself organises. Water quality is mixed —
official monitoring stations plus community photo classification for turbidity. Traditional knowledge
preservation is mixed but requires a data sovereignty protocol, not a simple lab log: custodian
communities (banjar adat, juntas de vecinos) are the primary source and the terms are theirs to set.

**Planet — 22 of 22 external.** GHG ppm, global temperature, world GDP, SDG indicators, climate finance.
Identical for every city. **No fab lab instruments anything here — this layer travels down, never up.**

## The way out: nine network-own sources

The original theoretical sheet does not capture these. They come from the Data Points Catalog, built
afterwards **precisely to compensate this imbalance** — real, already-instrumentable sources the network
itself owns, which feed City, Region and Bioregion cells with network data instead of leaving them wholly
dependent on official statistics.

| Source | Feeds | Where from | Effort |
|---|---|---|---|
| fablabs.io lab roster (50 km catchment) | Economic × City | fablabs.io API | low |
| Fab Academy alumni density | Economic / Social × City, Region, Bioregion | Fab Academy registry | low |
| Precious Plastic chapter throughput (kg) | Economic × Community / City | Precious Plastic Universe API | low |
| Smart Citizen kit count + uptime | Environmental × Community / City | Smart Citizen API | low |
| OpenStreetMap craft-tag density | Economic × Community / City | Overpass API | low |
| Community photo classification (waste, turbidity, vegetation) | Environmental × Community / Bioregion | AI over community-uploaded photos | medium |
| Lab-operated drone mapping | Environmental × Community | Lab mission logs (IAAC pattern) | medium |
| Decidim platform health | Governance × City | Decidim API | low |
| FAB / GOSH conference attendance from the bioregion | Social × Bioregion | Event attendance records | low |

**For a workshop participant these are the highest-value targets in the entire instrument:** reachable
this month, and they light up cells that would otherwise stay dark. Six of the nine are low-effort API
calls against registries the network already runs.

**Wiring two or three of these as real connectors is the single highest-leverage engineering task on this
project.**

## How this maps into the dashboard

`assets/data.js` encodes the audit in two places:

- `FEEDER_META` — the four categories (`lab`, `mixed`, `institutional`, `fixed`), each with a plain-language
  explanation. Every cell declares its `feeder`.
- `SOVEREIGNTY` — the per-scale counts above, rendered as a table in the **Getting data in** tab and as
  headline percentages in the **Workshop** tab.
- `NETWORK_SOURCES` — the nine sources, rendered as a table.

Current distribution across the 20 cells: 4 lab-fed, 7 mixed, 5 external, 4 boundary.

## A caveat worth keeping

The counts come from auditing a specific document (`3. Detailed Metrics.docx`) whose indicator set is a
theoretical proposal, not a fixed standard. The exact numbers will shift as the indicator set is revised.
**The pattern will not.** The concentration of network sovereignty in the Community row is structural: it
follows from what a fab lab is and where it sits, not from how any particular sheet was drafted.
