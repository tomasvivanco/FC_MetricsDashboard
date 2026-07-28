/* Generate data/weights.json from assets/data.js — the machine-readable
   weight table this dashboard actually uses, side by side with the
   exhibition console's table and the upstream site status, so the
   canonisation conversation has one artifact to point at.

   Run from the repo root:  node scripts/gen_weights_json.js
   Regenerate whenever CELLS weights or SIM.wts change. */
const fs = require('fs');
const js = fs.readFileSync('assets/data.js', 'utf8');
const M = new Function(js + '; return {CELLS, PILLARS, SCALES, SIM, META};')();
const { CELLS, PILLARS, SCALES, SIM, META } = M;

const cells = [];
let agree = 0;
PILLARS.forEach(p => {
  SCALES.forEach((s, j) => {
    const key = p.id + ':' + s.id, c = CELLS[key];
    if (!c) return;
    const sim = (SIM.wts[p.id] || [])[j] || null;
    const agrees = !!sim && Math.abs(c.pito - sim[0]) < 0.001 && Math.abs(c.dido - sim[1]) < 0.001;
    if (agrees) agree++;
    cells.push({
      cell: key,
      pillar: p.id,
      scale: s.id,
      dashboard: {
        pito: c.pito, dido: c.dido,
        provenance: c.wSource,             // "site" = documented upstream · "reconstructed" = proposed here
        under_review: !!c.underReview,
        boundary: !!c.boundary,
        generation12: !!c.generation12
      },
      exhibition_console: sim ? { pito: sim[0], dido: sim[1] } : null,
      agrees
    });
  });
});

const out = {
  $schema: null,
  title: 'FCI 3.0 — PITO/DIDO weight table (working comparison)',
  version: META.version,
  generated_by: 'scripts/gen_weights_json.js — do not edit by hand',
  status: 'NOT CANON. Three weight tables circulate (FCI 3.0 site v0, this dashboard, the exhibition console); this file makes the divergence machine-readable. The Foundation publishing a versioned canonical table supersedes all three.',
  sources: {
    dashboard: 'assets/data.js (CELLS[key].pito/dido) — active set for this surface',
    exhibition_console: SIM.source,
    site: META.siteUrl + ' — methodology v0, 12 of 20 cells populated'
  },
  agreement: { cells_total: cells.length, cells_agreeing: agree },
  formula: 'FCI = DIDO · (1 − PITO) · ρ   — cell projection: cell = (1−PITO)·w_pito + DIDO·w_dido',
  cells
};

fs.writeFileSync('data/weights.json', JSON.stringify(out, null, 2) + '\n');
console.log('data/weights.json written — ' + cells.length + ' cells, ' + agree + ' agreeing with the console table.');
