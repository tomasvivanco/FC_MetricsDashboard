# Context — start here

This folder holds everything needed to pick up the project without having been in the room. It is written
for the person who inherits this repository six months from now with no other briefing.

## Read in this order

| # | File | What you get | Read it if… |
|---|---|---|---|
| 1 | [`01-project-brief.md`](01-project-brief.md) | What this is, who it serves, what has been decided and what is still open | Always. It is the shortest path to being useful. |
| 2 | [`02-methodology.md`](02-methodology.md) | The FCI 3.0 formula, the weight table, aggregation rules, ρ, the Boeing recovery | You are touching how a score is computed. |
| 3 | [`03-full-stack.md`](03-full-stack.md) | Vivanco's framework: seven layers, five scales, four pillars, feasibility tiers | You are adding or changing indicators. |
| 4 | [`04-sovereignty-audit.md`](04-sovereignty-audit.md) | Who can actually produce each number — and the nine network-own sources | You are working on data ingestion or the workshop. |
| 5 | [`05-data-model.md`](05-data-model.md) | Every cell, every indicator, unit, direction, normalisation | You are writing code against `assets/data.js`. |
| 6 | [`06-workshop-ws3.md`](06-workshop-ws3.md) | The workshop and the dashboard's role in each of its three moves | You are facilitating or adapting the workshop. |

## The three-minute version

The Fab City pledge asks cities to produce almost everything they consume by 2054. Twelve years in, 56
signatory cities, 2,700+ fab labs — and essentially no rigorous causal evidence that any of it moves a
city's trajectory. The missing piece was an instrument that connects a repair log in one neighbourhood to
a planetary limit.

FCI 3.0 is that instrument. It reads twenty parts of city life — four pillars across five scales — and
combines them into one number:

```
FCI(t) = DIDO(t) · (1 − PITO(t)) · ρ(t)
```

What you can do, times what you don't depend on, times how fast you react. **Multiplied, not added** —
so a zero anywhere zeroes the result. A city that senses everything and acts on nothing scores nothing.

This dashboard renders that matrix, lets readings be attached to cells from live feeds, files or honest
estimates, and keeps those three kinds visually distinct because they are not the same kind of knowledge.

## The one thing to understand before changing anything

**Only ~17% of the framework's indicators can be measured by a fab lab without external data, and they
are almost all in the Community row.**

That single finding shapes the workshop design, the ingestion priorities, and the argument the instrument
makes. Before you redesign anything, read `04-sovereignty-audit.md`.

## Original documents

`sources/` holds the primary material, unedited:

- `Fab 26- Fab City Full Stack Metrics Framework.docx` — Vivanco's working paper, the theoretical spine
- `1. Full Stack Metrics Framework.docx` — the longer framework document
- `2. Implementation Guide.docx` — the five-stage implementation sequence
- `3. Detailed Metrics.docx` — the full ~95-indicator sheet the sovereignty audit is built on
- `WS3_Planilla_Metricas_FabLab_vs_Externo.md` — the audit itself, indicator by indicator
- `FAB26_WS3_Deck_v2.pptx` — the workshop deck as delivered

The live prototype this dashboard is built against: <https://staging.fci-index.pages.dev>
(matrix, methodology, atlas, phase plot, and the operator workbench under `/operate`).
