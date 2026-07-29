/* Headless smoke test for FC_MetricsDashboard index.html inline script.
   Minimal DOM stub — catches runtime reference errors and validates the
   model engine math. Not a rendering test. */
const fs = require('fs');
const path = process.argv[2] || 'index.html';
const html = fs.readFileSync(path, 'utf8');
const dataJs = fs.readFileSync('assets/data.js', 'utf8');
const m = html.match(/<script src="assets\/data.js"><\/script>\s*<script>([\s\S]*)<\/script>\s*<\/body>/);
if (!m) { console.error('FAIL: inline script not found'); process.exit(1); }

function el(id) {
  const store = {};
  return {
    id, innerHTML: '', textContent: '', value: '0.5', style: {}, dataset: {},
    options: { length: 1 },
    classList: { add(){}, remove(){}, toggle(){}, contains(){ return false; } },
    addEventListener(){}, removeEventListener(){},
    appendChild(){}, removeChild(){}, click(){}, focus(){},
    scrollIntoView(){}, dispatchEvent(){},
    setAttribute(){}, getAttribute(){ return null; },
    querySelector(s){ return el(s); }, querySelectorAll(){ return []; },
    _s: store
  };
}
const els = new Map();
const document = {
  querySelector(s){ if(!els.has(s)) els.set(s, el(s)); return els.get(s); },
  querySelectorAll(){ return []; },
  createElement(){ return el('created'); },
  getElementById(id){ return this.querySelector('#'+id); },
  body: el('body'),
  readyState: 'complete'
};
document.body.appendChild = ()=>{}; document.body.removeChild = ()=>{};
const localStorageMem = new Map();
const window = {
  localStorage: {
    setItem:(k,v)=>localStorageMem.set(k,String(v)),
    getItem:k=>localStorageMem.has(k)?localStorageMem.get(k):null,
    removeItem:k=>localStorageMem.delete(k)
  },
  scrollTo(){}, addEventListener(){}
};
const navigator = { clipboard: { writeText: async()=>{} } };
const fetchStub = () => Promise.reject(new Error('offline test'));
const URLstub = { createObjectURL: ()=>'blob:', revokeObjectURL: ()=>{} };
const BlobStub = function(){};
const FileReaderStub = function(){ this.readAsText = ()=>{}; };
const confirmStub = () => false;
const setTimeoutStub = (fn) => { try{ fn(); }catch(e){} return 0; };
const setIntervalStub = () => 0;   // never fires — a real interval would keep Node alive

const src = dataJs + '\n' + m[1] + `
;return { fitAxes, derivedFor, modelState, narrativeFor, tierStates, collectScores, MODE, SIMST, RHOEST, LS, normalise, SIM, CELLS, ingestCsv, SCHEMA_VERSION, meshFromJson, fmtMeshAvg, renderMeshPanel };`;

let api;
try {
  api = new Function('document','window','navigator','fetch','URL','Blob','FileReader','confirm','setTimeout','setInterval','location', src)(
    document, window, navigator, fetchStub, URLstub, BlobStub, FileReaderStub, confirmStub, setTimeoutStub, setIntervalStub, {href:''});
  console.log('PASS: full script boots without throwing');
} catch (e) {
  console.error('FAIL at boot:', e.message);
  console.error(e.stack.split('\n').slice(0,4).join('\n'));
  process.exit(1);
}

/* ---- math checks ---- */
const A = { pito: 0.62, dido: 0.55 };
const scores = {};
Object.keys(api.CELLS).forEach(k => { scores[k] = api.derivedFor(k, A); });
const fit = api.fitAxes(scores);
const ok1 = fit && Math.abs(fit.pito - A.pito) < 0.01 && Math.abs(fit.dido - A.dido) < 0.01;
console.log((ok1?'PASS':'FAIL') + ': fitAxes recovers axes from full projection — got', fit && fit.pito.toFixed(3), fit && fit.dido.toFixed(3));

/* recovery from a partial set (5 cells) */
const partial = {};
['environmental:community','economic:city','social:city','governance:community','economic:bioregion']
  .forEach(k => partial[k] = api.derivedFor(k, A));
const fit2 = api.fitAxes(partial);
const ok2 = fit2 && Math.abs(fit2.pito - A.pito) < 0.02 && Math.abs(fit2.dido - A.dido) < 0.02;
console.log((ok2?'PASS':'FAIL') + ': fitAxes recovers axes from 5 cells');

/* degenerate: one cell -> null */
const one = { 'economic:city': 0.5 };
console.log((api.fitAxes(one)===null?'PASS':'FAIL') + ': single cell refuses to fit');

/* ceiling: DIDO=1, rho=1, PITO=0.63 -> FCI 37 */
const fci = 1 * (1-0.63) * 1 * 100;
console.log((Math.abs(fci-37)<0.5?'PASS':'FAIL') + ': CEILING preset returns ~37 — got ' + fci.toFixed(1));

/* modelState in sim mode */
api.MODE.set('sim');
const st = api.modelState();
console.log((st.basis==='sim' && st.axes && typeof st.rho==='number' ? 'PASS':'FAIL') + ': sim modelState');
console.log('narrative sample:', api.narrativeFor(st.axes, st.rho));

/* tier states shape */
const ts = api.tierStates(st);
console.log((Array.isArray(ts) && ts.length===5 ? 'PASS':'FAIL') + ': five tier states');

/* model mode with two saved readings */
api.MODE.set('model');
api.LS.setRead('environmental:community', { kind:'static', score: api.derivedFor('environmental:community', A) });
api.LS.setRead('governance:community',    { kind:'static', score: api.derivedFor('governance:community', A) });
const st2 = api.modelState();
console.log((st2.axes && st2.basis==='measured' && st2.n===2 ? 'PASS':'FAIL') + ': model fits from 2 measured readings — pito ' + (st2.axes&&st2.axes.pito.toFixed(2)) + ' dido ' + (st2.axes&&st2.axes.dido.toFixed(2)));

/* estimate does not count as measured */
api.LS.setRead('social:city', { kind:'estimate', score: 0.9 });
const st3 = api.modelState();
console.log((st3.n===2 && st3.basis==='measured' ? 'PASS':'FAIL') + ': estimates excluded from measured fit basis');

/* schema_version gate in ingestCsv */
const hdr = 'cell,indicator,value,unit,observation_date,source,scale_min,scale_max,schema_version';
const row = 'environmental:community,Products repaired,143,units / month,2026-06-30,"Repair log",0,200,';
const major = api.ingestCsv(hdr+'\n'+row+'9.0', 'test');
console.log((major.applied===0 && major.report.some(r=>r.status==='rejected') ? 'PASS':'FAIL') + ': major schema mismatch refuses to load');
const minor = api.ingestCsv(hdr+'\n'+row+'1.0', 'test');
console.log((minor.applied===1 && minor.report.some(r=>r.status==='warning') ? 'PASS':'FAIL') + ': minor schema mismatch warns but loads');
const same = api.ingestCsv(hdr+'\n'+row+api.SCHEMA_VERSION, 'test');
console.log((same.applied===1 && !same.report.some(r=>r.status==='warning'&&r.label==='schema_version') ? 'PASS':'FAIL') + ': matching schema loads clean');

/* mesh (Meshtastic bridge) plumbing */
const bridgeJson = {
  uptime_24h_pct: 87.5, sensors_connected: 2, sensors_seen_24h: 3,
  averages: { temperature_c: 22.0, relative_humidity_pct: 45.0, barometric_pressure_hpa: 1012.0 },
  updated_at: '2026-07-29T12:00:00Z',
  sensors: [
    { node:'!11223344', name:'Patio sensor', short:'PAT', connected:true,
      last:{ temperature_c:21.0, relative_humidity_pct:50.0 },
      position:{ lat:41.3874, lng:2.1686 }, last_seen:'2026-07-29T11:58:00Z', uptime_24h_pct:91.2 },
    { node:'!deadbeef', name:'!deadbeef', connected:true,
      last:{ temperature_c:23.0, relative_humidity_pct:40.0, barometric_pressure_hpa:1012.0 },
      position:null, last_seen:'2026-07-29T11:59:00Z', uptime_24h_pct:83.8 }
  ]
};
const mesh = api.meshFromJson(bridgeJson);
console.log((mesh && mesh.connected===2 && mesh.sensors.length===2 ? 'PASS':'FAIL') + ': meshFromJson parses the bridge shape');
console.log((api.meshFromJson({foo:1})===null ? 'PASS':'FAIL') + ': non-mesh JSON yields no mesh block');
console.log((api.fmtMeshAvg(bridgeJson.averages,true)==='22.0 °C · 45 % RH · 1012 hPa' ? 'PASS':'FAIL') + ': averages format');
api.MODE.set('evidence');
api.LS.setRead('environmental:community', { kind:'live', score:0.875, url:'http://localhost:8787/reading.json',
  path:'uptime_24h_pct', min:0, max:100, dir:'dido', value:87.5, mesh });
const panel = api.renderMeshPanel('environmental:community');
const okPanel = panel.includes('Patio sensor') && panel.includes('41.38740, 2.16860')
  && panel.includes('2 connected now') && panel.includes('openstreetmap.org')
  && panel.includes('no fix') && panel.includes('meshRefresh');
console.log((okPanel ? 'PASS':'FAIL') + ': sensor list renders names, coordinates, count and refresh');

console.log('DONE');
