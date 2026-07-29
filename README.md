# Fab City Index 3.0 — Full Stack Metrics Dashboard

**▶ Live dashboard: <https://tomasvivanco.github.io/FC_MetricsDashboard/>**

An interactive research instrument for measuring a city's progress toward the 2054 Fab City pledge:
**twenty parts of city life, read as four pillars across five scales**, from a neighbourhood to a whole
bioregion.

Built for WS3 at FAB26 Boston, and for any city that wants to know which parts of its own metabolism it
can actually see.

> **New here, or taking this over?** Read **[HANDOVER.md](HANDOVER.md)** — one self-contained document
> with everything that matters: the argument, the key finding, the design rules that must not be broken,
> what is built, what is not, and where to take it next.

> **Status:** working research build. Methodology v0, in review. This is not an official publication of
> the Fab City Foundation. Weights marked *reconstructed* are a proposal for discussion, not canon.

---

## What the dashboard does

The Fab City pledge is twelve years old, 56 cities have signed it, and there is still almost no rigorous
causal evidence that any of it changes a city's trajectory. Not because nobody tried — because there was
no instrument connecting a repair log in one neighbourhood to a planetary limit. This dashboard is an
attempt at that instrument.

It does six things:

**1. Renders the twenty-cell matrix.** Four pillars (environmental, social, economic, governance) across
five scales (community, city, region, bioregion, planet). Each cell asks one plain question, names the
indicators that would answer it, and carries two documented weights — PITO and DIDO — that sum to 1.

**2. Colours each cell by its actual reading, not by its weights.** A continuous gradient from red
(0 — fully extractive) to green (1 — fully regenerative). Cells with no reading stay grey, which is the
honest state, not a failure.

**3. Distinguishes three kinds of knowledge, visibly.**

| Kind | What it is | How it looks |
|---|---|---|
| **Live** | Pulled from a connected API or webhook; refreshes itself | Solid colour, `live` tag |
| **Static** | A real value from a file or a signed manual entry, frozen at its observation date | Solid colour, `static` tag |
| **Estimate** | Nobody has data, so a person moved a slider | **Cross-hatched**, `estimate` tag |
| **Derived** | No reading — the model projected it from the cells that *are* measured | **Cross-hatched + dashed border**, `derived · model` tag |

An instrument that renders a measurement and a guess identically is lying by design. This one refuses to.

**4. Enforces provenance.** A static reading will not save without an observation date and a source.
Raw values only — the normalisation to 0–1 happens in the open, using a stated reference, so anyone can
disagree with it specifically rather than vaguely.

**5. Completes the picture with a model — and says so.** A city is three axes: PITO, DIDO and ρ.
Each cell is their projection through its weights (`cell = (1−PITO)·w_pito + DIDO·w_dido`) — the same
logic as the FCI exhibition console. In **Evidence + model** view, measured cells stay fixed and fit the
axes by least squares; dark cells fill with `derived` projections; measured cells show their Δ residual
against the model. In **Simulation** view the console itself runs here: three sliders, mock presets
(BCN · BOS · SCL · BALI · CEILING — the last one is the Generation 1+2 recovery: DIDO 1 · ρ 1 · PITO 0.63
→ FCI 37), everything badged *SIMULATION · NOT A MEASUREMENT*. A slider never overwrites a reading, and
**Evidence** view — grey means no data — is always one click away. The FCI banner keeps the formula, the
0–100 scale with the 37 ceiling, the five-FCIs-per-scale matryoshka strip, and a one-sentence plain
reading of the state, always in sight.

**Embedding:** any view can be iframed without chrome — `index.html?embed=matrix`,
`?embed=cities`, `?embed=formula` — so the FCI site or the PLANETAI observatory can embed this
instrument instead of re-implementing it. There is also a print stylesheet: ⌘P on the matrix or an
open cell panel produces a clean one-pager.

**6. Runs the WS3 workshop.** A dedicated mode where tables dot the matrix green / yellow / dark, fill one
card per cell (one cell, one source, one name, one date, one first step), and the facilitator collects
every card from a single sheet.

### The finding that shapes everything

We audited all ~95–108 indicators the framework defines and asked one blunt question: *who can actually
produce this number?*

| Scale | Indicators | Lab can measure alone | Mixed | Needs external |
|---|---|---|---|---|
| Community | 21 | **16** | 4 | 0 |
| City | 21 | 0 | 2 | 19 |
| Region | 21 | 0 | 3 | 18 |
| Bioregion | 23 | 2 | 2 | 19 |
| Planet | 22 | 0 | 0 | 22 |

Only ~17% of indicators are measurable by a fab lab with no external input, and they sit almost entirely
in the Community row. **The network owns the bottom row and almost nothing above it.** That is not a flaw
in the framework — it is the map of where the network is strong and where it has to go and ask. It is
also why the workshop exercise happens on the Community row, and why the dashboard surfaces ten
*network-own* data sources (fablabs.io, Fab Academy, Precious Plastic, Smart Citizen, OpenStreetMap,
Decidim, your own Meshtastic sensor mesh, and others) as the honest route upward.

**Live from your own hardware:** `scripts/meshtastic_bridge.py` subscribes to your Meshtastic
gateway's MQTT JSON feed and serves `http://localhost:8787/reading.json`; point the
Environmental × Community cell's Live-feed panel at it (path `uptime_24h_pct`, min 0, max 100,
higher = better) and the cell updates from your own mesh. `pip install paho-mqtt` is the only
dependency; `--selftest` verifies the arithmetic offline.

---

## Repository layout

```
.
├── index.html                  The dashboard. Single file, no build step.
├── LICENSE                     Apache 2.0 — aligned with the PLANETAI stack.
├── assets/
│   └── data.js                 The whole data model: 20 cells, 53 indicators,
│                               methodology, sovereignty audit, SIM layer, workshop script.
├── context/                    Everything needed to pick this up cold.
│   ├── README.md               Start here if you are new to the project.
│   ├── 01-project-brief.md     What this is, who it is for, decisions taken.
│   ├── 02-methodology.md       FCI 3.0: formula, weights, aggregation, ρ.
│   ├── 03-full-stack.md        Full Stack Metrics Framework: 7 layers, 5 scales, 4 pillars.
│   ├── 04-sovereignty-audit.md Who can produce which number, and the counts.
│   ├── 05-data-model.md        Every cell and indicator, with units and methods. Generated.
│   ├── 06-workshop-ws3.md      The workshop, and how the dashboard serves it.
│   ├── 07-professionalisation-roadmap.md  Every gap to production grade, prioritised.
│   ├── decisions/              Decision records (PLANETAI format): proposed → locked.
│   └── sources/                Original documents (papers, deck, planilla).
├── data/                       Where readings live and enter.
│   ├── README.md               How to submit, in five steps.
│   ├── template.csv            Blank, correct columns (incl. schema_version).
│   ├── example-filled.csv      Worked rows.
│   ├── schema.json             Machine-readable schema + valid cell keys.
│   ├── weights.json            The weight table, machine-readable, three sources
│   │                           side by side. Generated — do not edit by hand.
│   ├── connectors.yaml         This surface's connector manifest (network convention).
│   ├── snapshots/              Dated JSON from the scheduled fetch. Git = ledger.
│   └── submissions/            Team CSVs land here.
│       └── index.json          Manifest the dashboard reads.
├── scripts/
│   ├── validate_submission.py  Checks a CSV against the same rules the dashboard uses.
│   ├── fetch_snapshots.js      Fetches fablabs.io + Smart Citizen → data/snapshots/.
│   ├── gen_weights_json.js     Regenerates data/weights.json from data.js.
│   ├── gen_datamodel_doc.js    Regenerates context/05-data-model.md from data.js.
│   └── smoke_test.js           Headless boot + model-math test. Run before committing.
└── .github/workflows/
    └── snapshots.yml           Weekly scheduled fetch, commits snapshots.
```

---

## Running it

**Just look at it:** open `index.html` in any browser. Everything works except loading submissions from
the repo folder (browsers block local file reads) — use the file picker in the **Team data** tab instead.

**Full functionality, locally:**

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

**Publish it:** the repo is laid out for GitHub Pages served from the repository root.
In *Settings → Pages*, set **Source: Deploy from a branch**, **Branch: `main` / `/ (root)`**.
The dashboard is then live at `https://<user>.github.io/<repo>/`.

No build, no dependencies, no framework. One HTML file and one JS data file, deliberately — so that it
still opens in five years, and so anyone can read the whole thing without tooling.

---

## Submitting data as a workshop team

1. Copy `data/template.csv`.
2. Fill one row per observation. **Raw values only** — never pre-computed scores.
3. Save as `data/submissions/<city>-<team>.csv`, e.g. `boston-table4.csv`.
4. Add an entry to `data/submissions/index.json`.
5. Validate, then open a pull request:

```bash
python3 scripts/validate_submission.py data/submissions/boston-table4.csv
```

The validator applies the same rules as the dashboard and names the offending row. Full instructions in
[`data/README.md`](data/README.md).

---

## Where the numbers come from

Three sources, kept distinguishable everywhere in the code and the interface:

- **[A]** [FCI 3.0 prototype](https://staging.fci-index.pages.dev) — matrix, methodology, atlas, phase
  plot, operator workbench. Methodology v0, beta.
- **[B]** Vivanco, T. *Fab City Full Stack Metrics Framework: An Actionable Methodology for Multi-Scalar
  Implementation.* FAB26 working paper, Fab City Foundation / PUC Chile. Not yet peer-reviewed.
- **[C]** Diez, T., Charny, D., & Kohtala, C. (2024). *The Fab City Full Stack.* Fab City Foundation.
  [10.5281/zenodo.10492629](https://doi.org/10.5281/zenodo.10492629)

Every cell declares whether its weights are **documented** upstream or **reconstructed** here to fill a
gap. Six cells are documented; the rest are a working proposal.

Standing on: Florentin, Chabanel & Guimas (Utopies, 2018) — Paris 37.58 — and Boeing (Springer, 2024) —
Hamburg 37.00. Both measured one cell, with rigour, and got the right answer for that cell. FCI 3.0
contains that result rather than replacing it. PITO and DIDO are the founding Fab City vocabulary, coined
by Vicente Guallart and Neil Gershenfeld (Diez, Fab City Whitepapers, 2014 & 2016).

---

## What this instrument does not yet know

Named honestly, because the credibility depends on it:

- Twelve of twenty cells are meaningfully populated. The Region tier and Governance × Bioregion / × Region
  are thinnest.
- The weight table is v0. Three cells need sharpened argument before they harden: Economic × Bioregion
  (0.8/0.2), Environmental × Community (0.5/0.5), Economic × Community (0.3/0.7).
- The Boeing numerical recovery is sketched, not formal.
- The ρ measurement protocol is a v0 note; tier-weighting and council-rejection handling are open.
- The Full Stack Metrics Framework [Vivanco 2024] is a working paper plus a 2025 doctoral thesis, not peer-reviewed in its own right.
- A 2025 review of ~1,000 fab lab impact studies (Peuckert et al.) found strong evidence for learning and
  entrepreneurship outcomes, and almost none for bioregional or knowledge-sharing layers. The upper half
  of this matrix is, evidentially, close to empty.

The full list lives in the **What we don't know** tab and in `assets/data.js`.

---

## Contributing

The dashboard is deliberately dependency-free. If you extend it:

- Keep `index.html` and `assets/data.js` self-contained and readable without a build step.
- Any new number must declare its provenance and its normalisation. No unsourced values.
- Preserve the visual distinction between measurement and estimate. It is the point.
- If you change an indicator's `name`, `unit` or `direction`, run the validator — submissions bind to
  those strings.

---

*Fab City Foundation research and operations. Working build — comments to `index@fab.city`.*

---

## License

Apache License 2.0 — see [LICENSE](LICENSE). Aligned with the PLANETAI stack (Apache 2.0 across code surfaces). Weights, methodology text and cell notes carry their provenance flags regardless of licence: *documented* vs *reconstructed* is an epistemic distinction, not a legal one.
