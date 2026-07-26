# Submitting data

This is where workshop teams and city operators put their readings. Anything valid that lands in
`submissions/` shows up in the dashboard matrix.

---

## Five steps

### 1 · Start from the template

Copy [`template.csv`](template.csv). It has the correct columns in the correct order.
[`example-filled.csv`](example-filled.csv) shows four worked rows if you want to see it done.

### 2 · Fill one row per observation

**Raw values only.** Send `143` repairs, not `0.7`. The normalisation to a 0–1 reading happens in the
dashboard, in the open, using the range you declare — so anyone can check it. If you pre-compute the
score in your own spreadsheet, that reasoning is lost and the reading stops being auditable.

| Column | Required | Example | What it is |
|---|---|---|---|
| `cell` | **yes** | `environmental:community` | Which of the twenty cells. Format is `pillar:scale`. |
| `indicator` | **yes** | `Products repaired` | Must match an indicator name defined in that cell, exactly. |
| `value` | **yes** | `143` | The raw number as measured. |
| `unit` | **yes** | `units / month` | The unit of the raw number. |
| `observation_date` | **yes** | `2026-06-30` | When the measurement *refers to*, not when you typed it. ISO `YYYY-MM-DD`. |
| `source` | **yes** | `Repair café log, Sants` | Specific enough that somebody else could go and check. |
| `scale_min` | **yes** | `0` | The raw value that would count as 0. |
| `scale_max` | **yes** | `200` | The raw value that would count as 1. |
| `team` | no | `Table 4 — Boston` | Who submitted it. |
| `method` | no | `Manual count at close of each session` | How it was collected. Optional, but this is what makes it trustworthy a year from now. |
| `geography` | no | `Sants-Montjuïc` | The exact area, if narrower than the cell's scale. |
| `confidence` | no | `high` | Your own honest read: high, medium, low. |
| `notes` | no | `Two sessions cancelled in June` | Anything a reader needs in order to not misread it. |

**Valid `cell` keys** — the twenty combinations of pillar and scale:

```
environmental:community   social:community   economic:community   governance:community
environmental:city        social:city        economic:city        governance:city
environmental:region      social:region      economic:region      governance:region
environmental:bioregion   social:bioregion   economic:bioregion    governance:bioregion
environmental:planet      social:planet      economic:planet       governance:planet
```

Valid `indicator` names per cell are listed in [`schema.json`](schema.json), in
[`../context/05-data-model.md`](../context/05-data-model.md), and in the dashboard itself — click any cell.

#### About `scale_min` and `scale_max`

This is the part people skip, and it is the part that makes the number mean something. You are declaring
the range you want your value read against:

- **A practical ceiling** — "200 repairs a month is what this lab could realistically do at capacity"
- **A peer benchmark** — "the best comparable lab in the network does 400"
- **A science-based target** — "the city's own 2030 trajectory"

Whichever you choose, state it in `notes` if it is not obvious. Someone will ask.

Indicators where **higher is worse** (imported tonnes, emissions, days of delay) are inverted
automatically — you do not need to do anything. Declare the raw value and the real range; the dashboard
handles direction from the indicator definition.

### 3 · Name and place your file

```
data/submissions/<city>-<team>.csv
```

For example `boston-table4.csv`. Lower case, no spaces.

### 4 · Add yourself to the manifest

Add one entry to [`submissions/index.json`](submissions/index.json):

```json
{
  "file": "boston-table4.csv",
  "team": "Table 4 — Ana R.",
  "city": "Boston",
  "workshop": "WS3 · FAB26",
  "submitted": "2026-07-26"
}
```

The dashboard reads this manifest to know what to load.

### 5 · Validate, then open a pull request

```bash
python3 scripts/validate_submission.py data/submissions/boston-table4.csv
```

The validator applies **the same rules the dashboard does**, so a file that passes here will load
cleanly. It names the offending row and says what is wrong:

```
✗ data/submissions/boston-table4.csv — 2 error(s), 3 row(s) would load
    error  row 4 (environmental:community · Products repaired): value 'abc' is not a number
    error  row 6 (social:community · Participation): source is required
```

Run it with no arguments to check every file in the folder.

---

## Seeing your data in the dashboard

**Served over http** (GitHub Pages, or `python3 -m http.server` in the repo root) — open the
**Team data** tab and press *Load submissions from repo*.

**Opened as a local file** — browsers block reading neighbouring files, so use the file picker in the same
tab. It parses in your browser; nothing is uploaded anywhere.

Either way you get a row-by-row report of what loaded, what was rejected and why.

---

## Rules that decide whether your data survives

1. **One row, one observation.** A row packing three months into one line cannot be trended or checked.
2. **Raw values, not scores.** Normalisation is a documented step, not something you do privately.
3. **Units always, and always the same unit for the same indicator.** kg one month and tonnes the next is
   the most common way a metrics programme quietly destroys its own time series.
4. **Observation date, not upload date.** The index reads trajectories. A value stamped with the day you
   uploaded it is invisible to that.
5. **Name the source specifically enough to re-check.** "City data" is not a source. "Open data portal,
   dataset 4471, downloaded 2026-06-02" is.
6. **Say when you don't know.** A cell honestly left empty is worth more than one confidently filled with
   a guess. The whole instrument depends on that distinction holding.
7. **No personal data.** Aggregate before it leaves your lab. Counts, not names. If a row could identify a
   participant, it does not belong in the file.

---

## A note on community data

Some readings belong to a community, not to a city or a foundation. The upstream FCI 3.0 design puts those
behind a **sovereignty gate**: they publish only with the consent of the community that owns them, granted
one publication at a time, renewed at least annually, withdrawable at any point. In Bali that gate follows
Tri Hita Karana as three sign-offs that must all agree.

**This repository does not implement that gate** — it has no accounts and no roles. So: if the data is not
yours to publish, do not put it in a pull request. Ask first, and record that you asked.
