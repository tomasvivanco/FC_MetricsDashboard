# 01 · Project brief

## What this is

An interactive dashboard rendering the Fab City Index 3.0 twenty-cell metrics matrix, built as a working
research instrument for the Fab City Foundation and as the practical tool for workshop WS3 at FAB26,
Boston.

It is a **single HTML file plus a single JS data file**. No build step, no framework, no dependencies.
That is a deliberate constraint, for three reasons: it still opens in five years; anyone can read the
whole thing without tooling; and it can be handed to a city as one file that works offline.

## Who it serves

Three audiences, in tension, and the design has to hold all three:

**Researchers** need it to be defensible — every number sourced, every normalisation stated, every gap
named. If a reviewer asks "where did 0.72 come from?", the answer must be one click away.

**Workshop participants** need it to be legible in ninety seconds by someone who has never heard of PITO.
Jargon gets a plain-language gloss everywhere it appears. The plain sentence comes first, the technical
sentence second — never the reverse.

**City operators** need it to show honestly what is real and what is not, because their credibility is on
the line when they present it to a council.

The instrument fails if it serves any one of these at the cost of the others.

## Decisions taken (and why)

**Colour encodes the reading, not the weights.** An earlier build tinted each cell by its PITO/DIDO
weight split. That was wrong: the weights are fixed properties of the methodology and never change, so
the matrix looked identical regardless of what any city had measured. Colour now tracks the *reading* —
the evidence attached to that cell — which is the only thing that can actually move.

**Three reading kinds, visually distinct.** Live, static, and estimate. Estimates render cross-hatched
and labelled. This is the single most important design rule in the project: an instrument that renders a
measurement and a guess identically is lying by design. Do not "simplify" this away.

**Grey means no data, and grey is fine.** Unmeasured cells stay neutral rather than defaulting to a
midpoint. A cell honestly marked empty is worth more than a cell confidently filled with a guess. Most of
the matrix is grey and that is the accurate picture of where the evidence stands.

**Raw values in, normalisation in the open.** Submissions carry the raw number plus the min/max range
being scaled against. Never a pre-computed score. If somebody converts 143 repairs to 0.7 in their own
spreadsheet, the reasoning is lost and the reading stops being auditable.

**Direction is declared per indicator.** Some indicators mean the opposite of others — more repairs is
good, more imported tonnes is bad. Each indicator declares `dido` (higher is better) or `pito` (higher is
worse), and pito-direction values are inverted during normalisation. This guarantees that on screen,
**green always means regenerative** and never merely "big number".

**Reconstructed weights are marked as such.** The upstream methodology publishes weights for six cells.
The other fourteen are reconstructed here from Vivanco's paper as a working proposal. Every cell says
which it is. Do not quietly promote reconstructed weights to documented ones.

**Light mode only.** The upstream FCI 3.0 site renders on a warm paper background regardless of system
theme. The dashboard matches it. A dark-mode block was removed for exactly this reason.

## Current state

Working and verified:

- 20 cells, 51 indicators, each with unit, direction, normalisation method, feasibility tier
- Three-tier reading system with validation (a static reading will not save without date and source)
- Workshop mode: dot the matrix, four-cell cap per table, card collection, CSV export
- Team data ingestion: CSV parser, row-by-row validation report, repo manifest loader and file picker
- Nine views covering matrix, reading model, ingestion, formula, pilots, Full Stack, workshop, cards, gaps
- Python validator mirroring the dashboard's rules, so a file that passes will load

## Open questions

**Which domain is canonical.** The workshop deck points to `index.fab.city`; this build was developed
against `staging.fci-index.pages.dev`. Before publishing, confirm which is the public URL and update the
references in `assets/data.js` (`META.siteUrl`) and the README.

**The 20-cell table upstream is client-rendered.** The live matrix page renders its cell data in the
browser, so it could not be scraped directly. Weights for six cells were read from the methodology prose;
the rest are reconstructed. If the Foundation publishes a machine-readable weight table, replace the
reconstructed values and flip `wSource` to `"site"`.

**ρ is not yet computed.** The response coefficient is defined and explained but no city has a measured
value. The protocol itself is v0 upstream — tier-weighting and council-rejection handling are open. Until
then the FCI number cannot be completed for any pilot, and the dashboard says so rather than inventing one.

**Live API connectors are half-built.** The interface accepts an endpoint, a JSON path and a scaling
range, and will fetch and normalise on demand. What it does not do is refresh on a schedule — that needs a
server-side component. Browser CORS also blocks many public endpoints; the interface says so plainly
rather than failing silently.

**No sovereignty gate implemented.** The upstream design has community-tier data publishing only with
local-authority consent (in Bali, a three-body Tri Hita Karana flow). This dashboard documents the gate
but does not enforce it, because it has no accounts or roles. Anything handling real community data must
implement it before publishing.

## What would move this forward most

1. Confirm the canonical domain and the published weight table.
2. Wire two or three of the nine network-own sources (fablabs.io, Smart Citizen, Precious Plastic) as real
   connectors — they are the highest-value, lowest-effort path to genuinely live cells.
3. Run WS3 and ingest the real submissions, replacing the example file.
4. Get a worked Hamburg example on public NACE/COICOP data to formalise the Boeing recovery.
