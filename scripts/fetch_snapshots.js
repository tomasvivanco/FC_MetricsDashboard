/* Fetch network-own data sources and commit them as dated JSON snapshots.
   ----------------------------------------------------------------------
   The pattern (context/07, B·P1): a scheduled GitHub Action runs this
   script, which fetches each wired source, computes the indicator values,
   and writes data/snapshots/<slug>.json plus a manifest. The frontend
   stays a static file; git history is the provenance ledger; the dashboard
   renders snapshot readings as `static` (a real value frozen at its
   observation date — which is what a snapshot honestly is).

   Sources wired (both auth-free, both network-own):
   - fablabs.io lab roster  → Economic × City · "Fab lab density in catchment"
   - Smart Citizen devices  → Environmental × City · "Community sensors reporting"

   Run:  node scripts/fetch_snapshots.js            (all cities)
         node scripts/fetch_snapshots.js barcelona  (one city)
   Node 18+ (global fetch). Dependency-free. Exits 0 even on partial
   failure — a source being down must not kill the other snapshots —
   but exits 1 if NOTHING could be fetched. */

const fs = require('fs');
const path = require('path');

const OUT_DIR = path.join(__dirname, '..', 'data', 'snapshots');
const TODAY = new Date().toISOString().slice(0, 10);

/* The four pilot hubs. Coordinates are city-centre reference points. */
const PILOTS = [
  { id: 'boston',    name: 'Boston',    lat: 42.3601,  lng: -71.0589 },
  { id: 'barcelona', name: 'Barcelona', lat: 41.3874,  lng: 2.1686 },
  { id: 'santiago',  name: 'Santiago',  lat: -33.4489, lng: -70.6693 },
  { id: 'bali',      name: 'Bali',      lat: -8.6500,  lng: 115.2167 }
];

const km = (aLat, aLng, bLat, bLng) => {
  const R = 6371, dLat = (bLat - aLat) * Math.PI / 180, dLng = (bLng - aLng) * Math.PI / 180;
  const s = Math.sin(dLat / 2) ** 2 +
    Math.cos(aLat * Math.PI / 180) * Math.cos(bLat * Math.PI / 180) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(s));
};

async function getJson(url, timeoutMs = 30000) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, { signal: ctrl.signal, headers: { 'accept': 'application/json' } });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  } finally { clearTimeout(t); }
}

/* ── fablabs.io ─────────────────────────────────────────────────────── */
async function fetchFablabs(cities) {
  const raw = await getJson('https://api.fablabs.io/0/labs.json').catch(() =>
    getJson('https://api.fablabs.io/0/labs'));
  const labs = Array.isArray(raw) ? raw : (raw.labs || raw.data || []);
  if (!labs.length) throw new Error('fablabs.io returned no labs');
  const values = cities.map(c => {
    const inCatchment = labs.filter(l => {
      const lat = parseFloat(l.latitude), lng = parseFloat(l.longitude);
      if (isNaN(lat) || isNaN(lng)) return false;
      return km(c.lat, c.lng, lat, lng) <= 50;
    });
    return { city: c.id, value: inCatchment.length, unit: 'labs / 50 km catchment' };
  });
  return {
    slug: 'fablabs-io',
    source: 'fablabs.io registry (api.fablabs.io/0/labs)',
    fetched_at: new Date().toISOString(),
    observation_date: TODAY,
    binds_to: { cell: 'economic:city', indicator: 'Fab lab density in catchment' },
    normalisation: { scale_min: 0, scale_max: 25, direction: 'dido',
      note: 'Practical ceiling of 25 labs in a 50 km catchment — a proposed network peer benchmark, not canon.' },
    universe: labs.length,
    values
  };
}

/* ── Smart Citizen ──────────────────────────────────────────────────── */
async function fetchSmartCitizen(cities) {
  const cutoff = Date.now() - 30 * 24 * 3600 * 1000;
  const values = [];
  for (const c of cities) {
    let devices = [], page = 1;
    while (page <= 5) {
      const batch = await getJson(
        `https://api.smartcitizen.me/v0/devices?near=${c.lat},${c.lng}&within=20000&per_page=100&page=${page}`);
      const arr = Array.isArray(batch) ? batch : (batch.devices || []);
      devices = devices.concat(arr);
      if (arr.length < 100) break;
      page++;
    }
    const active = devices.filter(d => {
      const t = Date.parse(d.last_reading_at || (d.data && d.data.recorded_at) || '');
      return !isNaN(t) && t >= cutoff;
    });
    values.push({ city: c.id, value: active.length, unit: 'active kits / 20 km',
      total_registered: devices.length });
  }
  return {
    slug: 'smart-citizen',
    source: 'Smart Citizen API (api.smartcitizen.me/v0/devices, near+within)',
    fetched_at: new Date().toISOString(),
    observation_date: TODAY,
    binds_to: { cell: 'environmental:city', indicator: 'Community sensors reporting' },
    normalisation: { scale_min: 0, scale_max: 50, direction: 'dido',
      note: 'Only kits with a reading in the last 30 days count — the BCN archive audit found ~98% dormant.' },
    values
  };
}

/* ── main ───────────────────────────────────────────────────────────── */
(async () => {
  const only = process.argv[2];
  const cities = only ? PILOTS.filter(p => p.id === only) : PILOTS;
  if (!cities.length) { console.error('Unknown city: ' + only); process.exit(1); }
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const jobs = [
    ['fablabs-io', () => fetchFablabs(cities)],
    ['smart-citizen', () => fetchSmartCitizen(cities)]
  ];

  const written = [];
  for (const [slug, job] of jobs) {
    try {
      const snap = await job();
      const file = path.join(OUT_DIR, slug + '.json');
      fs.writeFileSync(file, JSON.stringify(snap, null, 2) + '\n');
      written.push(slug);
      console.log('✓ ' + slug + ' — ' + snap.values.map(v => v.city + ':' + v.value).join(' · '));
    } catch (e) {
      console.error('✗ ' + slug + ' failed: ' + e.message + ' — keeping the previous snapshot, if any.');
    }
  }

  /* manifest: every snapshot file currently present, whether or not this run refreshed it */
  const files = fs.readdirSync(OUT_DIR).filter(f => f.endsWith('.json') && f !== 'index.json');
  const manifest = {
    generated_at: new Date().toISOString(),
    note: 'Written by scripts/fetch_snapshots.js. Git history of this folder is the provenance ledger.',
    snapshots: files.map(f => {
      try {
        const s = JSON.parse(fs.readFileSync(path.join(OUT_DIR, f), 'utf8'));
        return { file: f, slug: s.slug, observation_date: s.observation_date, binds_to: s.binds_to };
      } catch (e) { return { file: f, error: 'unreadable' }; }
    })
  };
  fs.writeFileSync(path.join(OUT_DIR, 'index.json'), JSON.stringify(manifest, null, 2) + '\n');
  console.log((written.length ? 'Wrote ' + written.length + ' snapshot(s) + manifest.' : 'No source reachable.'));
  process.exit(written.length ? 0 : 1);
})();
