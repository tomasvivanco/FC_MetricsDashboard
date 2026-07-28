const fs=require('fs');
const js=fs.readFileSync('assets/data.js','utf8');
const M=new Function(js+'; return {CELLS,PILLARS,SCALES,FEEDER_META,FEASIBILITY,DATA_STATES,READING_KINDS,CSV_SCHEMA,META};')();
const {CELLS,PILLARS,SCALES,FEEDER_META,FEASIBILITY,DATA_STATES,READING_KINDS,CSV_SCHEMA}=M;
let o=[];
o.push('# 05 · Data model reference');
o.push('');
o.push('> **Generated from `assets/data.js`.** Do not edit by hand — regenerate with');
o.push('> `node scripts/gen_datamodel_doc.js > context/05-data-model.md` after changing the model.');
o.push('');
o.push('The file `assets/data.js` is the single source of truth for the dashboard. It defines no behaviour —');
o.push('only structure, content and provenance. Everything the interface renders comes from here.');
o.push('');
o.push('## Top-level exports');
o.push('');
o.push('| Constant | What it holds |');
o.push('|---|---|');
[['META','Version, methodology status, upstream counts, disclaimer'],
 ['SCALES','The five territorial tiers, with aggregation rule and plain-language gloss'],
 ['PILLARS','The four impact dimensions'],
 ['DATA_STATES','Upstream data vocabulary: live · partial · mock · placeholder'],
 ['READING_KINDS','How a reading got here: live · static · estimate — and what each counts as'],
 ['FEEDER_META','Who produces the data: lab · mixed · institutional · fixed'],
 ['SOVEREIGNTY','The per-scale audit of who can measure what'],
 ['NETWORK_SOURCES','Nine network-own data sources'],
 ['FEASIBILITY','High / medium / low tiers with definitions'],
 ['CELLS','The twenty cells and their indicators — the core of the model'],
 ['METHODOLOGY','Formula, terms, Boeing recovery, aggregation, open gaps'],
 ['SIM','Exhibition-console layer: mock archetypes, console weight table (comparison only), narrative bands'],
 ['FULL_STACK_LAYERS','The seven layers'],
 ['INGESTION_ROUTES','The four ways data enters'],
 ['CSV_SCHEMA','Submission column definitions'],
 ['DATA_HYGIENE','Seven rules for usable data'],
 ['REVIEW_PIPELINE','What happens to an uploaded file'],
 ['CITIES','Pilot cities and reconstructed Generation 1/2 points'],
 ['WORKSHOP','WS3 stakes, steps and dashboard role']
].forEach(r=>o.push('| `'+r[0]+'` | '+r[1]+' |'));
o.push('');
o.push('## Cell schema');
o.push('');
o.push('Each entry in `CELLS` is keyed `pillar:scale` (e.g. `environmental:community`) and carries:');
o.push('');
o.push('```js');
o.push('"environmental:community": {');
o.push('  pito: 0.5,              // PITO weight — throughput side. pito + dido === 1');
o.push('  dido: 0.5,              // DIDO weight — capacity side');
o.push('  wSource: "site",        // "site" = documented upstream | "reconstructed" = proposed here');
o.push('  underReview: true,      // flagged upstream for sharpened argument before weights harden');
o.push('  dataState: "mock",      // upstream state: live | partial | mock | placeholder');
o.push('  feeder: "lab",          // who produces it: lab | mixed | institutional | fixed');
o.push('  boundary: false,        // true = read as a limit, never aggregated upward');
o.push('  generation12: false,    // true only for the Economic × City / Region cell');
o.push('  thin: false,            // flagged upstream as one of the thinnest cells');
o.push('  question: "...",        // the plain-language question this cell answers');
o.push('  note: "...",            // provenance and methodological caveats');
o.push('  indicators: [ ... ]     // see below');
o.push('}');
o.push('```');
o.push('');
o.push('### Indicator schema');
o.push('');
o.push('```js');
o.push('{');
o.push('  name: "Products repaired",      // must match submissions exactly — CSVs bind to this string');
o.push('  unit: "units / month",          // the unit of the RAW value, not of the 0–1 reading');
o.push('  direction: "dido",              // "dido" = higher is better | "pito" = higher is worse (inverted on normalise)');
o.push('  feasibility: "high",            // high | medium | low');
o.push('  norm: "...",                    // how the raw value becomes 0–1, stated so it can be disagreed with');
o.push('  source: "..."                   // where this number typically comes from');
o.push('}');
o.push('```');
o.push('');
o.push('**`direction` is the one to get right.** Normalisation orients every reading so that **1 is always');
o.push('regenerative (green)** and 0 always extractive (red). A `pito`-direction indicator is inverted:');
o.push('80 tonnes imported on a 0–100 scale becomes a reading of 0.20, not 0.80.');
o.push('');
o.push('## Vocabularies');
o.push('');
o.push('### Reading kinds');
o.push('');
o.push('| Key | Label | Counts as | Rendering |');
o.push('|---|---|---|---|');
Object.keys(READING_KINDS).forEach(k=>{const v=READING_KINDS[k];o.push('| `'+k+'` | '+v.label+' | '+v.rigor+' | '+(k==='estimate'?'**cross-hatched**':'solid colour')+' |');});
o.push('');
o.push('### Feeder categories');
o.push('');
o.push('| Key | Label | Meaning |');
o.push('|---|---|---|');
Object.keys(FEEDER_META).forEach(k=>{const v=FEEDER_META[k];o.push('| `'+k+'` | '+v.short+' | '+v.label+' |');});
o.push('');
o.push('### Feasibility tiers');
o.push('');
o.push('| Key | Label | Meaning |');
o.push('|---|---|---|');
Object.keys(FEASIBILITY).forEach(k=>{const v=FEASIBILITY[k];o.push('| `'+k+'` | '+v.label+' | '+v.plain+' |');});
o.push('');
o.push('### Upstream data states');
o.push('');
o.push('| Key | Label | Meaning |');
o.push('|---|---|---|');
Object.keys(DATA_STATES).forEach(k=>{const v=DATA_STATES[k];o.push('| `'+k+'` | '+v.label+' | '+v.plain+' |');});
o.push('');
o.push('## Submission columns');
o.push('');
o.push('| Column | Required | Example | Purpose |');
o.push('|---|---|---|---|');
CSV_SCHEMA.forEach(c=>o.push('| `'+c.col+'` | '+(c.required?'**yes**':'no')+' | `'+c.example+'` | '+c.plain+' |'));
o.push('');
o.push('---');
o.push('');
o.push('## The twenty cells');
o.push('');
let tot=0,byFeeder={},byFeas={};
Object.values(CELLS).forEach(c=>{tot+=c.indicators.length;byFeeder[c.feeder]=(byFeeder[c.feeder]||0)+1;c.indicators.forEach(i=>byFeas[i.feasibility]=(byFeas[i.feasibility]||0)+1);});
o.push('**'+Object.keys(CELLS).length+' cells · '+tot+' indicators.** Feeder split: '+Object.entries(byFeeder).map(([k,v])=>v+' '+k).join(', ')+'. Feasibility split: '+Object.entries(byFeas).map(([k,v])=>v+' '+k).join(', ')+'.');
o.push('');
PILLARS.forEach(p=>{
  o.push('### '+p.label);
  o.push('');
  o.push('*'+p.plain+'*');
  o.push('');
  SCALES.forEach(s=>{
    const k=p.id+':'+s.id,c=CELLS[k];if(!c)return;
    const flags=[];
    if(c.generation12)flags.push('**GENERATION 1+2 CELL**');
    if(c.underReview)flags.push('⚠ weight under review');
    if(c.boundary)flags.push('boundary — not aggregated');
    if(c.thin)flags.push('among the thinnest cells');
    o.push('#### `'+k+'` — '+p.label+' × '+s.label);
    o.push('');
    o.push('> '+c.question);
    o.push('');
    o.push('| | |');
    o.push('|---|---|');
    o.push('| Weights | PITO '+c.pito.toFixed(2)+' · DIDO '+c.dido.toFixed(2)+' |');
    o.push('| Weight provenance | '+(c.wSource==='site'?'documented upstream':'**reconstructed** — working proposal')+' |');
    o.push('| Upstream data state | '+DATA_STATES[c.dataState].label+' |');
    o.push('| Who feeds it | '+FEEDER_META[c.feeder].short+' — '+FEEDER_META[c.feeder].label+' |');
    if(flags.length)o.push('| Flags | '+flags.join(' · ')+' |');
    o.push('');
    o.push(c.note);
    o.push('');
    o.push('| Indicator | Unit | Direction | Feasibility | Typical source |');
    o.push('|---|---|---|---|---|');
    c.indicators.forEach(i=>o.push('| '+i.name+' | `'+i.unit+'` | '+(i.direction==='dido'?'higher = better':'higher = worse')+' | '+FEASIBILITY[i.feasibility].label+' | '+i.source+' |'));
    o.push('');
    c.indicators.forEach(i=>o.push('- **'+i.name+'** → '+i.norm));
    o.push('');
  });
});
o.push('---');
o.push('');
o.push('*Generated from `assets/data.js` · '+M.META.version+'*');
fs.writeFileSync('context/05-data-model.md',o.join('\n')+'\n');
console.log('written:',o.length,'lines');
