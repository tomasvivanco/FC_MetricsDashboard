/* ============================================================================
   Fab City Index 3.0 — Full Stack Metrics Dashboard · data model
   ----------------------------------------------------------------------------
   SOURCES (three, kept explicitly distinguishable throughout):
   [A] FCI 3.0 prototype — https://staging.fci-index.pages.dev
       /matrix · /methodology · /phase · /atlas · /operate (workbench: bench,
       coverage, intake, sources, sovereignty). Methodology v0, beta, in review.
   [B] Vivanco, T. "Fab City Full Stack Metrics Framework: An Actionable
       Methodology for Multi-Scalar Implementation" (FAB26 paper, Fab City
       Foundation / PUC Chile). Working paper — not yet peer-reviewed.
   [C] Diez, T., Charny, D., & Kohtala, C. (2024). The Fab City Full Stack.
       Fab City Foundation. https://doi.org/10.5281/zenodo.10492629

   PROVENANCE DISCIPLINE: every cell declares `wSource` — whether its PITO/DIDO
   weights are documented on the FCI 3.0 methodology page ("site") or
   reconstructed here from [B] to fill a gap the v0 table has not published
   ("reconstructed"). Reconstructed weights are a working proposal, not canon.
   The site itself states only 12 of 20 cells are meaningfully populated.
   ============================================================================ */

/* Submissions bind to indicator names/units/directions. Bump the MINOR number
   when indicators are added (old files still load); bump the MAJOR number when
   an existing indicator's name, unit or direction changes (old files break —
   write a migration note in data/README.md).
   1.0 — FAB26 build · 1.1 — adds the two network-registry indicators
   (fab lab density, community sensors reporting). */
const SCHEMA_VERSION = "1.1";

const META = {
  version: "v0.5 — model completion build",
  methodologyStatus: "Methodology v0 · beta · in review toward v1",
  cellsPopulatedOnSite: 12,
  cellsTotal: 20,
  weightsUnderReview: ["economic:bioregion", "environmental:community", "economic:community"],
  siteUrl: "https://staging.fci-index.pages.dev",
  disclaimer: "This dashboard is a working research instrument built from the FCI 3.0 prototype and the Full Stack Metrics Framework FAB26 working paper [Vivanco 2024]. It is not an official publication of the Fab City Foundation. Weights marked 'reconstructed' are a proposal for discussion, not canon. Values marked 'derived' are model projections, never measurements."
};

/* ---------------------------------------------------------------------------
   SCALES — the five territorial tiers.
   `role` follows the aggregation rule documented in FCI 3.0 /atlas: Community,
   City and Region aggregate upward into the score; Bioregion and Planet are
   boundary observations only — watched as limits, never rolled up.
   `plain` is the same idea said without jargon.
--------------------------------------------------------------------------- */
const SCALES = [
  { id:"community", label:"Community", sub:"Neighbourhood, maker network",
    size:"~1,000–50,000 people", horizon:"Project cycles (months–years)",
    role:"Operational", aggregates:true,
    plain:"Your block, your lab, the people you actually see. This is where instruments touch the ground and where you can honestly say 'we did that'." },
  { id:"city", label:"City", sub:"Municipal boundary",
    size:"~100,000–10M people", horizon:"Annual cycles, 5–10 yr strategy",
    role:"Governance", aggregates:true,
    plain:"The first level of government that can actually act on a reading — pass the rule, fund the thing, change the contract." },
  { id:"region", label:"Region", sub:"Multi-city / economic zone",
    size:"~1–50M people", horizon:"10–20 yr planning cycles",
    role:"Governance · aggregation ceiling", aggregates:true,
    plain:"The last level that still adds up into a score. Above this, nobody governs fast enough for the number to mean anything." },
  { id:"bioregion", label:"Bioregion", sub:"Watershed, ecoregion",
    size:"Defined ecologically, not administratively", horizon:"Ecological cycles",
    role:"Boundary condition", aggregates:false,
    plain:"The natural region your city sits inside — its watershed and ecosystems. Watched as a limit you have to live within, not added to your score." },
  { id:"planet", label:"Planet", sub:"Earth-system thresholds",
    size:"Global", horizon:"Generational",
    role:"Boundary + global knowledge", aggregates:false,
    plain:"The planetary ceiling, plus the global pool of shared open knowledge. A horizon to check yourself against, never a scale you roll up to." }
];

const PILLARS = [
  { id:"environmental", label:"Environmental", color:"green",
    plain:"Material and energy: what comes in, what goes out, what it costs the ecosystem." },
  { id:"social",        label:"Social", color:"blue",
    plain:"People: who takes part, who learns, who is included, who is left out." },
  { id:"economic",      label:"Economic", color:"amber",
    plain:"Value: what is made locally, what is imported, where the money stays." },
  { id:"governance",    label:"Governance", color:"purple",
    plain:"Decisions: who decides, how openly, how fast a reading becomes an action." }
];

/* ---------------------------------------------------------------------------
   DATA STATE VOCABULARY — taken verbatim in meaning from the FCI 3.0
   operator workbench (/operate/matrix-coverage): live · partial · mock ·
   placeholder. Keeping the site's own four states rather than inventing new
   ones is what lets a reading here be compared to a reading there.
--------------------------------------------------------------------------- */
const DATA_STATES = {
  live:        { label:"Live", plain:"A wired source that refreshes on its own. Nobody retypes it.", color:"var(--green-600)" },
  partial:     { label:"Partial", plain:"Some indicators in this cell are real, others are still samples.", color:"var(--blue-600)" },
  mock:        { label:"Mock", plain:"Sample values, standing in so the structure can be seen. Not a measurement.", color:"var(--amber-600)" },
  placeholder: { label:"Placeholder", plain:"No source wired yet. Methodology v0 has not defined an indicator here.", color:"var(--text-muted)" }
};

/* ---------------------------------------------------------------------------
   READING PROVENANCE — how a cell's 0–1 reading got there. This is the
   distinction the whole dashboard turns on, and the one the workshop teaches:
   a live feed, a committed static value, and somebody's honest guess are three
   different epistemic objects and must never look identical on screen.
--------------------------------------------------------------------------- */
const READING_KINDS = {
  live:     { label:"Live", short:"live", plain:"Pulled automatically from a connected API or webhook. Refreshes itself.", rigor:"Measurement" },
  static:   { label:"Static", short:"static", plain:"A real value from a file or a signed manual entry. Real, but frozen at its observation date.", rigor:"Measurement" },
  estimate: { label:"Estimate", short:"estimate", plain:"Nobody has data yet, so a person moved a slider to their best judgement. Useful for seeing the shape. Never a measurement.", rigor:"Judgement — not evidence" },
  derived:  { label:"Derived", short:"derived · model", plain:"No reading attached. The model projected this value from the cells that ARE measured, through the weight table. It fills the dark cells so you can see the shape the evidence implies — it is a projection, never a measurement.", rigor:"Model projection — not evidence" }
};

/* ---------------------------------------------------------------------------
   FEEDER — who is responsible for producing the data. From the analysis of
   [B] §5.4 (feasibility rests on proximity to records already kept) crossed
   with the FCI 3.0 source registry (which sources feed which cells).
--------------------------------------------------------------------------- */
const FEEDER_META = {
  lab: {
    short:"Hub-fed", icon:"🔧", label:"The hub — lab plus its community — produces this directly",
    plain:"Your hub already produces this in its normal week — attendance sheets, repair logs, machine hours, sensor campaigns, its own surveys. No new instrument needed, no permission to ask for. One discipline: hub records enter as Community evidence for the district the hub anchors — they are never a proxy for city-scale throughput. The district is the measurement unit; the hub is who measures.",
    accent:"var(--green-600)"
  },
  mixed: {
    short:"Mixed", icon:"⚖️", label:"The lab supplies part; the rest needs external data",
    plain:"You can contribute a real input — a sub-sample, a proxy, your own sensors densifying an official network — but the complete indicator still needs somebody else's dataset to close.",
    accent:"var(--amber-600)"
  },
  institutional: {
    short:"External", icon:"🌐", label:"Requires a statistical agency, government, or international database",
    plain:"Somebody official produces this and you do not. Your job here is not to measure — it is to find the person who owns the export and ask them for it.",
    accent:"var(--blue-600)"
  },
  fixed: {
    short:"Boundary", icon:"◇", label:"Planetary or ecological reference — travels down, never up",
    plain:"Identical for every city, produced by Earth-system science. You read it as a limit. No fab lab instruments anything at this layer.",
    accent:"var(--text-muted)"
  }
};

/* ---------------------------------------------------------------------------
   DATA SOVEREIGNTY BY SCALE — the single most consequential empirical finding
   behind this whole dashboard.
   Derived by auditing all ~95–108 indicators of the Full Stack Metrics
   Framework's Detailed Metrics sheet [B] and classifying each by who can
   actually produce it.
   The result: the Fab City network holds real data sovereignty over exactly
   one horizontal strip — Community — and almost nothing above it.
   This is why the workshop exercise is built on the Community row.
--------------------------------------------------------------------------- */
const SOVEREIGNTY = {
  headline:"Of ~95–108 indicators the framework defines, only ~18 (17%) can be measured by a fab lab with no external input — and they sit almost entirely in the Community row.",
  implication:"This is not a flaw in the framework; it is the map of where the network is currently strong and where it must go and ask. Community is where you own the data. City and Region are where you must build a relationship with whoever holds it.",
  byScale: [
    { scale:"community", total:21, lab:16, mixed:4, external:0,
      verdict:"Maximum data sovereignty. This is where the network can act alone." },
    { scale:"city",      total:21, lab:0,  mixed:2, external:19,
      verdict:"Most dependent on official statistics. The network's only native inputs are sensor densification and civic-platform participation." },
    { scale:"region",    total:21, lab:0,  mixed:3, external:18,
      verdict:"The lab does not instrument this scale. At best it contributes one data point inside a wider mapping." },
    { scale:"bioregion", total:23, lab:2,  mixed:2, external:19,
      verdict:"A context scale, not an ingestion scale. The only direct contributions are environmental education and stewardship the lab itself runs." },
    { scale:"planet",    total:22, lab:0,  mixed:0, external:22,
      verdict:"100% external, without exception. This layer travels down to the city, never up from it." }
  ]
};

/* ---------------------------------------------------------------------------
   NETWORK-OWN DATA SOURCES — the answer to the sovereignty problem above.
   These are NOT in the framework's original theoretical sheet. They come from the
   Data Points Catalog, built afterwards precisely to close that gap: real,
   already-instrumentable sources the network itself owns, which feed City,
   Region and Bioregion cells with network data instead of leaving them
   wholly dependent on official statistics.
   For a workshop participant these are the highest-value targets in the whole
   instrument: reachable this month, and they light up cells that would
   otherwise stay dark.
--------------------------------------------------------------------------- */
const NETWORK_SOURCES = [
  { name:"fablabs.io lab roster", feeds:"Economic × City", api:"fablabs.io API",
    plain:"How many labs sit inside a 50 km catchment of this city — pulled straight from the network's own registry.", effort:"low" },
  { name:"Fab Academy alumni density", feeds:"Economic / Social × City, Region, Bioregion", api:"Fab Academy registry",
    plain:"Trained capability per territory. The network knows exactly who it trained and where they are.", effort:"low" },
  { name:"Precious Plastic chapter throughput", feeds:"Economic × Community / City", api:"Precious Plastic Universe API",
    plain:"Kilograms of plastic actually processed by chapters — a real circularity number nobody else holds.", effort:"low" },
  { name:"Smart Citizen kit count and uptime", feeds:"Environmental × Community / City", api:"Smart Citizen API",
    plain:"Community sensors already deployed and reporting. Densifies the official monitoring network rather than duplicating it.", effort:"low" },
  { name:"OpenStreetMap craft-tag density", feeds:"Economic × Community / City", api:"Overpass API",
    plain:"Workshops, makers and repair businesses mapped in OSM — an open proxy for productive fabric that anyone can query.", effort:"low" },
  { name:"Community photo classification", feeds:"Environmental × Community / Bioregion", api:"AI over community-uploaded photos",
    plain:"Waste, water turbidity, vegetation — classified from photos residents take. Turns a phone into an instrument.", effort:"medium" },
  { name:"Lab-operated drone mapping", feeds:"Environmental × Community", api:"Lab mission logs (IAAC pattern)",
    plain:"The lab flies it, the lab owns the imagery. Already proven at IAAC.", effort:"medium" },
  { name:"Decidim platform health", feeds:"Governance × City", api:"Decidim API",
    plain:"Actual civic participation on the city's own deliberation platform — not electoral turnout as a stand-in.", effort:"low" },
  { name:"FAB / GOSH conference attendance", feeds:"Social × Bioregion", api:"Event attendance records",
    plain:"Who from this bioregion shows up to the network's knowledge events. A crude but real measure of connection.", effort:"low" }
];

const FEASIBILITY = {
  high:   { label:"High", plain:"You could pull this from records you already keep, this month.",
            detail:"Derived from routine operational records — workshop attendance, repair logs, meeting calendars. [B] §5.4." },
  medium: { label:"Medium", plain:"It exists, but somebody has to formalise how it gets recorded first.",
            detail:"Requires procedural formalisation before it yields reliable, comparable data. [B] §5.4." },
  low:    { label:"Low", plain:"Needs real instruments or a proper survey. Plan it, don't promise it.",
            detail:"Requires dedicated technical infrastructure or validated survey instruments (water-reuse monitoring, climate accounting, cohesion indices). Defer to later phases. [B] §5.4." }
};

/* ---------------------------------------------------------------------------
   THE 20 CELLS
   Each indicator carries: name · unit · direction · normalisation · feasibility
   `direction`: "dido" = higher raw value means more regenerative capacity
                "pito" = higher raw value means more extractive throughput
   This matters: the 0–1 reading is always oriented so that 1 = DIDO/green and
   0 = PITO/red, which means "pito"-direction indicators must be inverted when
   normalised. Stating direction per indicator is what makes that auditable.
--------------------------------------------------------------------------- */
const CELLS = {

  /* ---------- ENVIRONMENTAL ---------- */
  "environmental:community": {
    pito:0.5, dido:0.5, wSource:"site", underReview:true, dataState:"mock", feeder:"lab",
    question:"Is this neighbourhood keeping material in use instead of throwing it away?",
    note:"One of three cells the FCI 3.0 methodology explicitly flags for sharpened argument before the v0 weights harden — the 0.5/0.5 split is contested.",
    indicators:[
      { name:"Material reused or recycled locally", unit:"kg / month", direction:"dido", feasibility:"high",
        norm:"Share of total material throughput diverted locally; 0 = none diverted, 1 = diversion at the practical ceiling agreed for the lab's catchment.",
        source:"Lab intake and repair logs" },
      { name:"Products repaired", unit:"units / month", direction:"dido", feasibility:"high",
        norm:"Repairs per 1,000 catchment residents, min-max scaled against network peer labs.",
        source:"Repair-café and workshop records" },
      { name:"Waste diverted from landfill", unit:"% of stream", direction:"dido", feasibility:"medium",
        norm:"Direct percentage, used as-is (already 0–1).",
        source:"Municipal collection data cross-checked with lab records" },
      { name:"Renewable energy consumed", unit:"% of lab load", direction:"dido", feasibility:"medium",
        norm:"Direct percentage of the facility's own consumption.",
        source:"Utility bills / submetering" }
    ]
  },
  "environmental:city": {
    pito:0.7, dido:0.3, wSource:"reconstructed", dataState:"partial", feeder:"mixed",
    question:"How much material and energy does the whole city pull in, and what does it emit?",
    note:"Reconstructed from [B]'s environmental pillar (material flows, energy/climate, ecosystem impacts, pollution) at city scale. In the Barcelona pilot the Smart Citizen sensor network is the first live source targeted here.",
    indicators:[
      { name:"Domestic material consumption", unit:"tonnes / capita / yr", direction:"pito", feasibility:"medium",
        norm:"Inverted and min-max scaled against a bioregional sustainable-throughput benchmark; higher consumption drives the reading toward 0.",
        source:"Urban material flow accounting (Eurostat-compatible MFA)" },
      { name:"Territorial GHG emissions", unit:"tCO₂e / capita / yr", direction:"pito", feasibility:"medium",
        norm:"Inverted, scaled against the city's own science-based trajectory for the year.",
        source:"Municipal climate inventory" },
      { name:"Air and water quality sensing coverage", unit:"sensors / km²", direction:"dido", feasibility:"high",
        norm:"Coverage against a target density; caps at 1 once the city can resolve neighbourhood-level variation.",
        source:"Smart Citizen / municipal sensor fleet" },
      { name:"Community sensors reporting", unit:"active kits / 20 km", direction:"dido", feasibility:"high",
        norm:"Kits with a reading in the last 30 days within 20 km, scaled against a practical ceiling of 50 (proposed). Counts only kits actually reporting — the Barcelona archive audit found ~98% dormant, and counting the dormant ones flatters the indicator.",
        source:"Smart Citizen API — network-own source, snapshot pipeline" }
    ]
  },
  "environmental:region": {
    pito:0.7, dido:0.3, wSource:"reconstructed", dataState:"mock", feeder:"institutional",
    question:"Do the material flows across this whole region balance, or is the city exporting its problems next door?",
    note:"Regional material flows and cross-jurisdiction ecological pressure. Reconstructed — the FCI 3.0 methodology names the Region tier as among its thinnest.",
    indicators:[
      { name:"Regional material flow balance", unit:"import : local ratio", direction:"pito", feasibility:"low",
        norm:"Inverted ratio; 1 when regional supply meets regional demand for the tracked material classes.",
        source:"Regional statistical accounts, MFA" },
      { name:"Cross-jurisdiction emissions accounting", unit:"% of flows accounted", direction:"dido", feasibility:"medium",
        norm:"Share of inter-municipal flows that are actually measured rather than estimated.",
        source:"Regional environment agency" }
    ]
  },
  "environmental:bioregion": {
    pito:0.85, dido:0.15, wSource:"reconstructed", dataState:"mock", feeder:"mixed", boundary:true,
    question:"Is the natural region this city sits in still able to regenerate what the city takes?",
    note:"Boundary layer. Read as a limit the city's score has to live within — never aggregated upward. A region scoring well inside a bioregion in overshoot is not scoring well.",
    indicators:[
      { name:"Watershed carrying capacity utilisation", unit:"% of renewable supply", direction:"pito", feasibility:"low",
        norm:"Inverted; 1 = withdrawal well inside renewable recharge, 0 = structural overshoot.",
        source:"Basin authority / hydrological modelling" },
      { name:"Biodiversity corridor integrity", unit:"% connectivity retained", direction:"dido", feasibility:"low",
        norm:"Landscape connectivity index, used directly.",
        source:"Ecoregional assessment, remote sensing" }
    ]
  },
  "environmental:planet": {
    pito:0.9, dido:0.1, wSource:"reconstructed", dataState:"mock", feeder:"fixed", boundary:true,
    question:"Where does this city's footprint sit against the planet's hard limits?",
    note:"Planetary boundary horizon (Rockström et al. 2009; Steffen et al. 2015; Richardson et al. 2023 — six of nine boundaries now crossed). A reference frame, not a reporting unit.",
    indicators:[
      { name:"Planetary boundary status", unit:"count of 9 transgressed", direction:"pito", feasibility:"low",
        norm:"Global scientific reference, downscaled only as context. Not a city-level performance measure.",
        source:"Earth-system science literature" },
      { name:"Consumption-based material footprint", unit:"tonnes / capita / yr", direction:"pito", feasibility:"low",
        norm:"Inverted against a globally equitable per-capita share.",
        source:"Multi-regional input-output models" }
    ]
  },

  /* ---------- SOCIAL ---------- */
  "social:community": {
    pito:0.2, dido:0.8, wSource:"reconstructed", dataState:"mock", feeder:"lab",
    question:"Are more people here gaining the skills and access to make things themselves?",
    note:"The highest-feasibility cell in the whole matrix: [B] §5.4 identifies participation and training as measurable directly from records a lab already keeps.",
    indicators:[
      { name:"Participation in making activities", unit:"unique people / month", direction:"dido", feasibility:"high",
        norm:"Per 1,000 catchment residents, min-max scaled against network peers.",
        source:"Workshop attendance sheets" },
      { name:"Skills training sessions delivered", unit:"sessions / month", direction:"dido", feasibility:"high",
        norm:"Scaled against the lab's own stated programme capacity.",
        source:"Programme calendar" },
      { name:"Skills acquired and retained", unit:"% of participants certified", direction:"dido", feasibility:"medium",
        norm:"Direct percentage; requires a follow-up protocol to be meaningful.",
        source:"Post-course assessment" },
      { name:"Equity of access", unit:"% from under-represented groups", direction:"dido", feasibility:"medium",
        norm:"Participation share compared to the catchment's demographic baseline; 1 = parity or better.",
        source:"Voluntary self-reported registration data" }
    ]
  },
  "social:city": {
    pito:0.3, dido:0.7, wSource:"reconstructed", dataState:"mock", feeder:"institutional",
    question:"Can everyone in this city reach a place where they could make or repair something?",
    note:"Health and wellbeing, equity and inclusion, employment, community and culture at city scale ([B] §4, social pillar).",
    indicators:[
      { name:"Population within 2 km of a maker facility", unit:"% of residents", direction:"dido", feasibility:"medium",
        norm:"Direct percentage from spatial analysis.",
        source:"Municipal facility registry + census geography" },
      { name:"Employment in distributed manufacturing and repair", unit:"jobs / 10,000 residents", direction:"dido", feasibility:"medium",
        norm:"Min-max scaled against comparable cities.",
        source:"Labour statistics, NACE/NAICS classes" },
      { name:"Spatial equity of access", unit:"Gini of facility access", direction:"pito", feasibility:"low",
        norm:"Inverted Gini; 1 = access evenly distributed across districts.",
        source:"Spatial analysis of facility registry" }
    ]
  },
  "social:region": {
    pito:0.3, dido:0.7, wSource:"reconstructed", dataState:"mock", feeder:"institutional", thin:true,
    question:"Do skills and people actually move between the cities of this region?",
    note:"Among the thinner cells. The Region tier is named in the FCI 3.0 open gaps as under-instrumented.",
    indicators:[
      { name:"Inter-municipal skills programmes", unit:"count of active programmes", direction:"dido", feasibility:"medium",
        norm:"Scaled against the number of municipalities in the region.",
        source:"Regional development agency" },
      { name:"Workforce mobility", unit:"% commuting across municipal lines", direction:"dido", feasibility:"medium",
        norm:"Used as a proxy for functional regional integration.",
        source:"Census commuting matrices" }
    ]
  },
  "social:bioregion": {
    pito:0.4, dido:0.6, wSource:"reconstructed", dataState:"mock", feeder:"mixed", boundary:true,
    question:"Is the knowledge that belongs to this territory being recognised and kept alive?",
    note:"Boundary-layer social reading. Handle with the ethics of [B] §15: research must not be extractive, and community knowledge is not the Foundation's to publish.",
    indicators:[
      { name:"Traditional and Indigenous knowledge integration", unit:"qualitative rubric 0–4", direction:"dido", feasibility:"low",
        norm:"Participatory rubric scored with, never about, the communities concerned. Sovereignty-gated.",
        source:"Co-produced assessment with customary authorities" },
      { name:"Bioregional place attachment", unit:"survey index", direction:"dido", feasibility:"low",
        norm:"Validated survey instrument required before this yields comparable data.",
        source:"Periodic population survey" }
    ]
  },
  "social:planet": {
    pito:0.3, dido:0.7, wSource:"reconstructed", dataState:"mock", feeder:"fixed", boundary:true,
    question:"Is what this city learns being shared back so anyone else can use it?",
    note:"Full Stack Layer 7 — global knowledge exchange. This is the layer that makes a local fix reusable in another bioregion.",
    indicators:[
      { name:"Open documentation published", unit:"designs / yr with open licence", direction:"dido", feasibility:"high",
        norm:"Scaled against projects completed — i.e. what share of work is actually documented and shared.",
        source:"Repository records, lab documentation practice" },
      { name:"Reuse of local designs elsewhere", unit:"forks / downloads by other nodes", direction:"dido", feasibility:"medium",
        norm:"Min-max scaled across the network.",
        source:"Repository telemetry" }
    ]
  },

  /* ---------- ECONOMIC ---------- */
  "economic:community": {
    pito:0.3, dido:0.7, wSource:"site", underReview:true, dataState:"mock", feeder:"lab",
    question:"Does making and repairing here actually keep value in the neighbourhood?",
    note:"Flagged in FCI 3.0 methodology §3 as needing sharpened argument before the weights harden.",
    indicators:[
      { name:"Value of goods produced locally", unit:"currency / month", direction:"dido", feasibility:"medium",
        norm:"Scaled against the equivalent imported-goods cost the production displaces.",
        source:"Lab production records with unit costing" },
      { name:"Savings from repair and reuse", unit:"currency / month avoided", direction:"dido", feasibility:"high",
        norm:"Replacement cost avoided, min-max scaled against peers.",
        source:"Repair logs with replacement-cost lookup" },
      { name:"Local jobs and livelihoods created", unit:"FTE", direction:"dido", feasibility:"medium",
        norm:"Per 1,000 catchment residents.",
        source:"Lab employment and spin-out records" }
    ]
  },
  "economic:city": {
    pito:0.5, dido:0.5, wSource:"site", generation12:true, dataState:"partial", feeder:"mixed",
    question:"How much of what this city consumes can it actually produce itself?",
    note:"THE GENERATION 1+2 CELL. This single cell is what Utopies measured for ~600 French urban areas (Paris 37.58, 2018) and what Boeing measured for Hamburg (37.00, 2024). Two independent statistical systems, six years apart, same number — the public-data ceiling, a property of global supply-chain geometry rather than of either city. The other 19 cells are the surface area FCI 3.0 adds.",
    indicators:[
      { name:"Local production self-sufficiency", unit:"% of consumption met locally", direction:"dido", feasibility:"medium",
        norm:"Boeing's discipline: priority × self-sufficiency by consumption class. Direct percentage.",
        source:"NACE/COICOP economic accounts; Metroverse ECI as proxy" },
      { name:"Import dependency", unit:"% of demand imported", direction:"pito", feasibility:"medium",
        norm:"Inverted percentage — the mirror of the indicator above, kept separate for auditability.",
        source:"Regional trade and input-output accounts" },
      { name:"Economic complexity", unit:"ECI index", direction:"dido", feasibility:"high",
        norm:"Min-max scaled across the peer set; a proxy for the diversity of what a place knows how to make.",
        source:"Metroverse / Harvard Growth Lab" },
      { name:"Fab lab density in catchment", unit:"labs / 50 km catchment", direction:"dido", feasibility:"high",
        norm:"Count of registered labs within 50 km, scaled against a practical ceiling of 25 (network peer benchmark, proposed). Distributed-production capacity the network itself can verify.",
        source:"fablabs.io registry — network-own source, snapshot pipeline" }
    ]
  },
  "economic:region": {
    pito:0.5, dido:0.5, wSource:"site", generation12:true, dataState:"partial", feeder:"mixed",
    question:"Can this region supply itself, or does everything come from outside it?",
    note:"The same Generation 1+2 measurement read at regional scope. Which of City or Region carries it depends on the data scope available in that pilot.",
    indicators:[
      { name:"Regional economic diversification", unit:"ECI / diversity index", direction:"dido", feasibility:"high",
        norm:"Min-max scaled across comparable regions.",
        source:"Metroverse, national statistical institutes" },
      { name:"Supply-chain integration", unit:"% of inputs sourced in-region", direction:"dido", feasibility:"low",
        norm:"Direct percentage from input-output tables where they exist.",
        source:"Regional input-output accounts" }
    ]
  },
  "economic:bioregion": {
    pito:0.8, dido:0.2, wSource:"site", underReview:true, dataState:"mock", feeder:"fixed", boundary:true,
    question:"How much of this bioregion's economy depends on pulling material from outside it?",
    note:"Third of the three cells FCI 3.0 flags for sharpened argument. The 0.8/0.2 split is the most contested in the v0 table.",
    indicators:[
      { name:"Bioregional material dependency", unit:"% of material imported into the bioregion", direction:"pito", feasibility:"low",
        norm:"Inverted percentage.",
        source:"Bioregional accounts where they exist; otherwise documented proxy" },
      { name:"Cross-boundary trade intensity", unit:"tonnes / capita crossing the boundary", direction:"pito", feasibility:"low",
        norm:"Inverted, scaled against comparable bioregions.",
        source:"Freight and customs statistics" }
    ]
  },
  "economic:planet": {
    pito:0.75, dido:0.25, wSource:"reconstructed", dataState:"mock", feeder:"fixed", boundary:true,
    question:"What does global supply-chain structure allow any city to achieve at all?",
    note:"The structural ceiling itself, as an explicit horizon. This is the cell that explains why Paris and Hamburg both landed on ~37 without either city failing.",
    indicators:[
      { name:"Global value-chain dependency", unit:"index", direction:"pito", feasibility:"low",
        norm:"Reference frame only — establishes the ceiling against which city readings are interpreted.",
        source:"Multi-regional input-output literature" },
      { name:"Distributed manufacturing capacity worldwide", unit:"count of active nodes", direction:"dido", feasibility:"high",
        norm:"Network-level count (2,700+ fab labs) used as context.",
        source:"Fab Foundation network registry" }
    ]
  },

  /* ---------- GOVERNANCE ---------- */
  "governance:community": {
    pito:0.1, dido:0.9, wSource:"reconstructed", dataState:"mock", feeder:"lab",
    question:"Do people here meet, decide together, and write down what they learned?",
    note:"[B] argues governance is not one pillar among four but the condition for the other three: without regular meetings, clear responsibilities and documented protocols, the environmental, social and economic metrics cannot be maintained at all.",
    indicators:[
      { name:"Council or assembly meetings held", unit:"meetings / quarter", direction:"dido", feasibility:"high",
        norm:"Against the governance cadence the group itself committed to.",
        source:"Meeting calendar — a record almost every lab already keeps" },
      { name:"Meeting attendance", unit:"% of members", direction:"dido", feasibility:"high",
        norm:"Direct percentage.",
        source:"Attendance records" },
      { name:"Institutional partnerships active", unit:"count", direction:"dido", feasibility:"high",
        norm:"Min-max scaled against peer labs.",
        source:"Partnership agreements on file" },
      { name:"Knowledge documented and shared", unit:"% of projects documented", direction:"dido", feasibility:"high",
        norm:"Direct percentage of completed projects with published documentation.",
        source:"Project repository" }
    ]
  },
  "governance:city": {
    pito:0.15, dido:0.85, wSource:"reconstructed", dataState:"partial", feeder:"mixed",
    question:"Is city data open enough that anyone could check this score — and does the city act on it?",
    note:"Institutional capacity, data availability, transparency. In the Barcelona pilot the Open Data Portal is the named source. This cell is also where ρ (how fast a reading becomes an action) is most directly observable.",
    indicators:[
      { name:"Open data infrastructure", unit:"% of relevant datasets published openly", direction:"dido", feasibility:"high",
        norm:"Direct percentage against a defined list of index-relevant datasets.",
        source:"Municipal open-data portal catalogue" },
      { name:"Observation-to-action latency", unit:"days from reading to fitted response", direction:"pito", feasibility:"medium",
        norm:"Inverted and scaled against a pre-registered response budget. This is the ρ input.",
        source:"Council decision logs cross-referenced with monitoring records" },
      { name:"Institutional transparency", unit:"rubric 0–4", direction:"dido", feasibility:"medium",
        norm:"Documented rubric on publication, revision history, and machine readability.",
        source:"Structured assessment of published governance records" }
    ]
  },
  "governance:region": {
    pito:0.2, dido:0.8, wSource:"site", dataState:"mock", feeder:"mixed", thin:true,
    question:"Do the cities in this region actually share data and align their rules?",
    note:"Named in FCI 3.0 methodology §7 as one of the two thinnest cells in the matrix, alongside Governance × Bioregion.",
    indicators:[
      { name:"Inter-city policy alignment", unit:"count of harmonised instruments", direction:"dido", feasibility:"medium",
        norm:"Scaled against the number of municipalities in the region.",
        source:"Regional governance records" },
      { name:"Regional data-sharing agreements", unit:"count in force", direction:"dido", feasibility:"medium",
        norm:"Scaled against the number of index-relevant domains.",
        source:"Inter-municipal agreements register" }
    ]
  },
  "governance:bioregion": {
    pito:0.2, dido:0.8, wSource:"site", dataState:"mock", feeder:"institutional", thin:true,
    question:"Is anyone actually governing at the scale of the watershed?",
    note:"The other thinnest cell per methodology §7. It matters because the honest answer is usually 'no' — and that absence is precisely why bioregion cannot aggregate into a score.",
    indicators:[
      { name:"Bioregional governance bodies active", unit:"count (watershed councils etc.)", direction:"dido", feasibility:"medium",
        norm:"Presence and mandate strength against a documented rubric.",
        source:"Basin authority and ecoregional governance registries" },
      { name:"Cross-jurisdiction monitoring agreements", unit:"count in force", direction:"dido", feasibility:"medium",
        norm:"Scaled against the jurisdictions sharing the bioregion.",
        source:"Environmental agency agreements" }
    ]
  },
  "governance:planet": {
    pito:0.15, dido:0.85, wSource:"reconstructed", dataState:"mock", feeder:"institutional", boundary:true,
    question:"Is this city part of the global commons that shares how to fix things?",
    note:"Layer 7 plus what [B] calls planetary computation (Vivanco 2025): local readings becoming globally readable, collectively governed knowledge — measurement as participation in a planetary feedback system rather than as reporting.",
    indicators:[
      { name:"Participation in open-data commons", unit:"count of shared datasets", direction:"dido", feasibility:"high",
        norm:"Scaled against the city's own index-relevant dataset count.",
        source:"Federation node records" },
      { name:"Multilateral environmental engagement", unit:"count of active commitments", direction:"dido", feasibility:"medium",
        norm:"Documented commitments with reporting obligations actually met.",
        source:"International agreement registries" }
    ]
  }
};

/* ---------------------------------------------------------------------------
   METHODOLOGY — the formula and its terms, each with a plain-language gloss.
--------------------------------------------------------------------------- */
const METHODOLOGY = {
  formula: "FCI(t) = DIDO(t) · (1 − PITO(t)) · ρ(t)",
  formulaPlain: "What you can do, times what you don't depend on, times how fast you react. Multiplied — not added.",
  whyProduct: "The product is the whole argument. High DIDO with high PITO is performative: fab labs without metabolic shift. Low PITO with low DIDO is a depleted city, not a Fab City — neither extracting much nor generating much. And a zero anywhere zeroes the result: a city that senses everything and acts on nothing scores nothing, no matter how good its dashboards.",
  terms: {
    pito: {
      name:"PITO — Products In, Trash Out",
      plain:"Buy far, waste near. The old one-way metabolism.",
      technical:"The linear-extractive metabolic signature: imports of products, energy, food and raw materials; exports of waste, emissions and externalised pollution. Expressed as a stock variable in [0,1]; high PITO means heavy linear-extractive metabolism.",
      formula:"PITO(t) = Σ(w_c^PITO · s_c^extractive) / Σ(w_c^PITO)"
    },
    dido: {
      name:"DIDO — Data In, Data Out",
      plain:"Sense what's happening, share what you learn, make more of it close to home.",
      technical:"The regenerative-distributed metabolic signature: open data infrastructure, fab-lab activity, distributed manufacturing capacity, recycling and remanufacturing capacity, community sensing, institutional transparency, and the policy/research/innovation layer that lets a city act on what it knows.",
      formula:"DIDO(t) = Σ(w_c^DIDO · s_c^capacity) / Σ(w_c^DIDO)"
    },
    rho: {
      name:"ρ (rho) — the response coefficient",
      plain:"How fast a reading turns into something actually being done. A number nobody acts on changes nothing.",
      technical:"Action latency: the speed at which an observation at any tier produces a fitted, human-approved response at the appropriate governance tier within a pre-registered budget. ρ = 1 is perfect coupling; ρ = 0 means observations are made but never acted upon. Generations 1 and 2 have ρ implicit at 1 because their models are static; Generation 3 makes it measurable and treats it as the third axis. The natural measurement substrate already exists: PLANETAI's H₀-A protocol timestamps five stages per response cycle (detect → decide → fabricate → deploy → measure) into a public audit ledger.",
      formula:"ρ(t) ∈ [0,1] — protocol v0, tier-weighting and council-rejection handling still open",
      symbolNote:"Symbol drift, flagged: the 2026-04-28 PLANETAI decision record writes this term κ (coupling coefficient); the public surfaces — this dashboard and the exhibition console — write ρ. Same term, one symbol should be canonised."
    }
  },
  boeing: "Set every weight to zero except Economic × Region, drop the coupling term, and compute only the self-sufficiency dimension, and the formula returns ~0.37 for Hamburg and 0.3758 for Paris — exactly what Generations 1 and 2 produced. That is the respect move: Generations 1 and 2 computed one cell, with rigour, and got the right answer for that cell. FCI 3.0 exposes the 37/100 ceiling as a projection of the full index onto its single best-instrumented cell, then adds nineteen more cells and ρ. Two equivalent encodings of that recovery circulate: this dashboard reconstructs Paris/Hamburg with DIDO unknown and ρ implicit at 1; the exhibition console encodes a CEILING archetype with DIDO = 1, ρ = 1, PITO = 0.63 so the product returns 37 directly. Same claim — the formal Hamburg worked example should fix one canonical encoding.",
  boeingPlain: "The old 37/100 score wasn't wrong. It was one cell out of twenty, measured properly. This index contains that result rather than replacing it.",
  aggregation: "Aggregation stops at the Region tier. Community → City → Region nest and add up into the score. Bioregion and Planet enter as boundary-condition observations — context and limits, never scales the index rolls up to.",
  aggregationPlain: "Neighbourhood adds into city, city adds into region. Full stop. The bioregion and the planet are limits you check yourself against, not levels you climb — because no government sits at those scales that could act fast enough for the number to mean anything. That speed is ρ.",
  attribution: "Attribution concerns effects linkable with reasonable confidence to a specific intervention. Aggregation concerns the cumulative performance of larger systems. A Fab Lab can credibly report how many repairs it completed; it cannot infer from that figure that a city or bioregion has become sustainable. Keeping the two apart is what protects the framework from overstated claims. [B] §2.1",
  openGaps: [
    "Twelve of twenty cells are meaningfully populated. The Region tier and the Governance × Bioregion / × Region cells are the thinnest — either populated honestly with mock-pill discipline or named as deferred research deliverables.",
    "The 4×5 → PITO/DIDO weight table is v0. Three cells deserve sharpened argument before the canonical weights harden: Economic × Bioregion (0.8/0.2), Environmental × Community (0.5/0.5), Economic × Community (0.3/0.7).",
    "The Boeing numerical recovery is sketched, not formal. A worked Hamburg example on public NACE/COICOP data would close the loop and pre-empt the most predictable reviewer objection.",
    "The ρ measurement protocol is a v0 note. Tier-weighting and council-rejection handling are open — but the measurement substrate exists: PLANETAI's H₀-A ledger timestamps exactly the cycle ρ describes. Defining ρ over that ledger is the shortest path to v1.",
    "The response term has two symbols in circulation: κ in the locked 2026-04-28 decision record, ρ on the public surfaces (this dashboard, the exhibition console). One should be canonised in a superseding decision record.",
    "Three PITO/DIDO weight tables now exist: the FCI 3.0 site's v0 (12 cells), this dashboard's documented+reconstructed set, and the exhibition console's full 20-cell table — they agree on only 5 of 20 cells. A versioned, machine-readable weights.json (started in data/weights.json here) needs to become the single source all surfaces consume.",
    "The Full Stack Metrics Framework [Vivanco 2024] is a working paper plus a 2025 doctoral thesis, not yet peer-reviewed in its own right; a bioregional peer-matching companion paper would fix that.",
    "LOCAL SHIFT® and LOCAL FOOTPRINT® Nature are proprietary Utopies products. The published methodology and the 2018 numbers are cited; reproducibility of the simulator outputs is not claimed.",
    "A 2025 review of ~1,000 Fab Lab impact studies (Peuckert et al.) found strong quantitative evidence for learning, skills and entrepreneurship outcomes — and almost none for bioregional, place-based or knowledge-sharing layers. The upper half of this matrix is, evidentially, close to empty."
  ]
};

/* ---------------------------------------------------------------------------
   SIM — the exhibition-console layer (fci-simulator-console, July 2026).
   The console models a city as three axes (PITO, DIDO, ρ) projected onto the
   20 cells through a weight table: cell = (1−PITO)·w_pito + DIDO·w_dido.
   This dashboard adopts that projection for two disciplined uses:
   (1) model completion — fitting the axes from MEASURED cells only and
       rendering the dark cells as explicitly-marked 'derived' projections;
   (2) simulation mode — the console's own behaviour, everything mock,
       badged SIMULATION · NOT A MEASUREMENT.
   ARCHETYPES are the console's reference presets, all mock. CEILING encodes
   the Generation 1+2 recovery as a preset: DIDO=1, ρ=1, PITO=0.63 → FCI=37.
   wts below is the console's own 20-cell weight table, kept for comparison —
   it agrees with this dashboard's per-cell weights on only 5 of 20 cells,
   which is exactly why data/weights.json exists. The dashboard's per-cell
   weights (CELLS[key].pito/dido) remain the active set everywhere.
--------------------------------------------------------------------------- */
const SIM = {
  source:"FCI 3.0 exhibition console (fci-simulator-console, July 2026)",
  badge:"SIMULATION · NOT A MEASUREMENT",
  archetypes:[
    { id:"bcn",     name:"BCN",     pito:0.62, dido:0.55, rho:0.40, label:"Barcelona-like · mock ○" },
    { id:"bos",     name:"BOS",     pito:0.70, dido:0.45, rho:0.25, label:"Boston-like · mock ○" },
    { id:"scl",     name:"SCL",     pito:0.55, dido:0.35, rho:0.30, label:"Santiago-like · mock ○" },
    { id:"bali",    name:"BALI",    pito:0.60, dido:0.40, rho:0.35, label:"Bali-like · mock ○" },
    { id:"ceiling", name:"CEILING", pito:0.63, dido:1.00, rho:1.00, label:"The ceiling city (Gen 1+2, ρ=1) · mock ○" }
  ],
  /* console's weight table, [pito, dido] per scale in SCALES order —
     for the divergence table only, NOT the active weights */
  wts:{
    environmental:[[0.5,0.5],[0.7,0.3],[0.8,0.2],[0.9,0.1],[1.0,0.0]],
    social:       [[0.0,1.0],[0.1,0.9],[0.1,0.9],[0.1,0.9],[0.2,0.8]],
    economic:     [[0.3,0.7],[0.5,0.5],[0.6,0.4],[0.8,0.2],[1.0,0.0]],
    governance:   [[0.0,1.0],[0.0,1.0],[0.0,1.0],[0.0,1.0],[0.0,1.0]]
  },
  narrative:{
    /* one plain sentence generated from the fitted/simulated state */
    pito:{ hi:"a linear-extractive metabolism", mid:"a metabolism still leaning on imports", lo:"a metabolism largely fed from its own territory" },
    dido:{ hi:"with real productive and sensing capacity", mid:"with flickers of capacity", lo:"with almost no capacity of its own" },
    rho:{ hi:"— and readings become action fast.", mid:"— and the wire between seeing and doing is patchy.", lo:"— and the wire between seeing and doing is mostly missing.", none:"— and nobody has measured how fast seeing becomes doing." }
  }
};

const FULL_STACK_LAYERS = [
  { n:1, label:"Infrastructures for production", detail:"Fab Labs, makerspaces, microfactories, tools, spaces, commons", role:"Operational",
    plain:"The machines and the room they sit in." },
  { n:2, label:"Capabilities through education", detail:"Training, skills development, capability formation", role:"Operational",
    plain:"Teaching people to use them." },
  { n:3, label:"Value-generating projects", detail:"Entrepreneurship, social innovation, prototyping", role:"Operational",
    plain:"Actually making things that matter to someone." },
  { n:4, label:"Orchestrating networks & hubs", detail:"Coordination between local communities, initiatives and networks", role:"Operational",
    plain:"Getting the labs and groups to work together." },
  { n:5, label:"Place-based interventions & policy", detail:"Strategy, policy, institutional design", role:"Governance",
    plain:"Turning it into how the place is actually run." },
  { n:6, label:"Bioregional strategies", detail:"Urban systems ↔ watersheds, ecological conditions, resource limits", role:"Boundary / horizon",
    plain:"Fitting all of it inside what the land and water can take." },
  { n:7, label:"Global knowledge sharing", detail:"Open-source sharing, standards, collective learning", role:"Boundary / horizon",
    plain:"Sending what you learned back out so the next city doesn't start from zero." }
];

/* ---------------------------------------------------------------------------
   INGESTION — the four routes data can take into the index.
   Taken from the FCI 3.0 operator workbench (/operate/intake, /operate/sources).
--------------------------------------------------------------------------- */
const INGESTION_ROUTES = [
  {
    id:"api", icon:"↻", name:"Live API connector", kind:"live",
    oneLine:"A wired feed the index pulls from on a schedule. Nobody retypes anything.",
    goodFor:"Data somebody else already publishes and keeps updating — open-data portals, statistical agencies, sensor platforms.",
    youNeed:["An endpoint URL that returns JSON","The path to the value inside that JSON","Permission to call it (a key, if it's not public)"],
    effort:"Highest to set up, zero to maintain.",
    produces:"A live reading. Refreshes itself; the cell's colour moves on its own."
  },
  {
    id:"file", icon:"▦", name:"File upload", kind:"static",
    oneLine:"Drop a spreadsheet, a PDF report, a dataset. The platform reads it and proposes values.",
    goodFor:"The normal case: a report published once a year, an export someone emailed you, your own records.",
    youNeed:["A file in CSV, Excel, JSON, PDF, or GeoTIFF","Column headers that a person could understand","One row per observation"],
    effort:"Low. This is where most cities will start.",
    produces:"A static reading, stamped with its observation date and its file of origin."
  },
  {
    id:"webhook", icon:"↦", name:"Webhook subscription", kind:"live",
    oneLine:"The source pushes to you the moment it has something new, instead of you asking.",
    goodFor:"Machine logs, sensor networks, anything that emits events — fab lab machine hours, courtyard air sensors.",
    youNeed:["A source system that can POST to a URL","A generated endpoint from the platform","Agreement on the payload shape"],
    effort:"Medium to set up, zero to maintain. Best fidelity for anything continuous.",
    produces:"A live reading, updated as events arrive."
  },
  {
    id:"manual", icon:"✎", name:"Manual entry", kind:"static",
    oneLine:"You type the number in, and you sign it.",
    goodFor:"Everything no API will ever cover: repair-café logs, council attendance, machine hours, banjar records, the count you did by hand.",
    youNeed:["The cell it belongs to","The indicator and its unit","The value, the observation date, and a justification"],
    effort:"Lowest. Always available. Always provenance-logged.",
    produces:"A static reading carrying your signature and the submission timestamp."
  }
];

/* The CSV/Excel schema the mapper expects. Column names are what a person
   would write; the mapper's job is to bind them to cell + indicator. */
const CSV_SCHEMA = [
  { col:"cell", required:true, example:"environmental:community",
    plain:"Which of the twenty parts of city life this belongs to. Pillar and scale, separated by a colon." },
  { col:"indicator", required:true, example:"Products repaired",
    plain:"Exactly what was counted. Use the indicator name listed in the cell." },
  { col:"value", required:true, example:"143",
    plain:"The raw number as measured. Do not pre-convert it to 0–1 — the platform normalises." },
  { col:"unit", required:true, example:"units/month",
    plain:"The unit the number is in. Without this the value cannot be normalised or compared." },
  { col:"observation_date", required:true, example:"2026-06-30",
    plain:"When the measurement refers to (not when you typed it). ISO format, YYYY-MM-DD." },
  { col:"source", required:true, example:"Repair café log, Barcelona Sants",
    plain:"Where it came from, specific enough that somebody else could go and check." },
  { col:"scale_min", required:true, example:"0",
    plain:"The bottom of the range you are scaling against — the raw value that would count as 0. State it so your normalisation is auditable." },
  { col:"scale_max", required:true, example:"200",
    plain:"The top of that range — the raw value that would count as 1. A practical ceiling, a peer benchmark, or a science-based target." },
  { col:"team", required:false, example:"Table 4 — Boston",
    plain:"Who submitted this. Used to attribute the reading back to your table." },
  { col:"method", required:false, example:"Manual count at close of each session",
    plain:"How it was collected. Optional, but this is what makes the number auditable a year from now." },
  { col:"geography", required:false, example:"Sants-Montjuïc district",
    plain:"The exact area the number covers, if narrower than the cell's scale." },
  { col:"confidence", required:false, example:"high",
    plain:"Your own honest read: high, medium, or low. Low-confidence rows go to review rather than committing." },
  { col:"notes", required:false, example:"Two sessions cancelled in June; undercount likely",
    plain:"Anything a reader would need to know to not misread the number." },
  { col:"schema_version", required:false, example:"1.1",
    plain:"Which version of the indicator schema this file was written against (see SCHEMA_VERSION in assets/data.js). Optional, but it is what lets the pipeline warn you instead of silently misreading your file when the model evolves." }
];

const DATA_HYGIENE = [
  { rule:"One row, one observation.",
    why:"A row that packs three months into one line cannot be trended, and cannot be checked. Split it." },
  { rule:"Raw values, not pre-computed scores.",
    why:"Send 143 repairs, not 0.7. Normalisation is a documented, auditable step the platform performs — if you do it in your spreadsheet, nobody can see how." },
  { rule:"Units always, and always the same unit for the same indicator.",
    why:"kg one month and tonnes the next is the single most common way a metrics programme quietly destroys its own time series." },
  { rule:"Observation date, not upload date.",
    why:"The index reads trajectories (ΔFCI/Δt). A value stamped with the day you uploaded it is invisible to that." },
  { rule:"Name the source specifically enough to be re-checked.",
    why:"'City data' is not a source. 'Open data portal, dataset ID 4471, downloaded 2026-06-02' is." },
  { rule:"Say when you don't know.",
    why:"A cell honestly marked mock is worth more than a cell confidently filled with a guess. The whole instrument depends on that distinction holding." },
  { rule:"Don't upload personal data.",
    why:"Aggregate before it leaves your lab. Counts, not names. If a row could identify a participant, it should not be in the file." }
];

const REVIEW_PIPELINE = [
  { step:1, name:"Extract", plain:"The platform reads your file and pulls out candidate values.",
    detail:"CSV and Excel go through a schema mapper that binds your columns to cell and indicator. PDFs go through extraction that scores its confidence field by field. JSON is validated against the cell schema. GeoTIFF is registered as tiles." },
  { step:2, name:"Score confidence", plain:"It marks how sure it is about each field.",
    detail:"Per-field confidence scoring. Nothing about this step is a judgement about your data quality — it is the platform declaring its own uncertainty about what it read." },
  { step:3, name:"Split", plain:"Confident values commit on their own. The rest wait for a person.",
    detail:"High-confidence extractions auto-commit. Everything else lands in the review queue for a human to approve or edit before it becomes a reading." },
  { step:4, name:"Sovereignty gate", plain:"Some readings need their community's consent before publishing.",
    detail:"Community-tier data can be sovereignty-gated: it publishes only with local-authority consent, granted one publication at a time, renewed at least annually, withdrawable at any point. In Bali the gate follows Tri Hita Karana as three sign-offs that must all agree. The Foundation's job is to show the gate, not to route around it." },
  { step:5, name:"Commit", plain:"The value becomes a reading, and the cell changes colour.",
    detail:"Committed readings carry their provenance — source, method, observation date, and who signed off — everywhere they travel, including into the aggregate index." }
];

/* ---------------------------------------------------------------------------
   PILOT CITIES
--------------------------------------------------------------------------- */
const CITIES = [
  { id:"boston", name:"Boston", country:"Massachusetts · USA", bioregion:"North Atlantic bioregion",
    pito:0.58, dido:0.35, rho:null, status:"mock", workshopHome:true,
    note:"The FAB26 host city and the default for this workshop. Readings are sample values — the sensor fleet still needs building, and saying so is part of the method." },
  { id:"barcelona", name:"Barcelona", country:"Catalonia · Spain", coords:"41.39°N 2.16°E", bioregion:"Mediterranean bioregion",
    pito:0.62, dido:0.41, rho:null, status:"partial",
    note:"The pilot furthest along. Home institution IAAC. Four named sources: Metroverse ECI (Harvard Growth Lab) for the economy, the IAAC fab-lab catchment, the Smart Citizen sensor network, and the Barcelona Open Data Portal. Environmental × City and Economic × City are the first two cells targeted to move from mock to real." },
  { id:"santiago", name:"Santiago", country:"Chile", bioregion:"Southern Cone",
    pito:0.55, dido:0.30, rho:null, status:"mock",
    note:"Pilot city. Community-tier cells require junta de vecinos (neighbourhood council) consent; that catalogue is still pending." },
  { id:"bali", name:"Bali", country:"Indonesia", bioregion:"Indonesian Archipelago bioregion",
    pito:0.45, dido:0.28, rho:null, status:"partial",
    note:"Pilot city, and the one with the most developed sovereignty design: the Tri Hita Karana three-body gate (banjar adat, desa adat, PHDI). That gate is a design, not an agreement in force — none of the three bodies has yet agreed to operate it." },
  { id:"paris", name:"Paris", country:"France · Utopies 2018", bioregion:"—",
    pito:0.62, dido:null, rho:1, fci:0.3758, status:"reconstructed", generation:1,
    note:"Generation 1 (Florentin, Chabanel & Guimas / Utopies, 2018). One cell — Economic × Region — measured across ~600 French urban areas. No DIDO axis, ρ implicit at 1. Shown here as a reconstructed point, not a new measurement." },
  { id:"hamburg", name:"Hamburg", country:"Germany · Boeing 2024", bioregion:"—",
    pito:0.63, dido:null, rho:1, fci:0.37, status:"reconstructed", generation:2,
    note:"Generation 2 (Boeing, Springer, 2024). The same single cell, a different statistical system, six years later — and the same number. That convergence is the public-data ceiling." }
];

/* ---------------------------------------------------------------------------
   WORKSHOP — WS3, FAB26 Boston. The dashboard's role in each step.
--------------------------------------------------------------------------- */
const WORKSHOP = {
  title:"WS3 · Measuring the Fab City",
  where:"FAB26, Boston",
  stakes: [
    { n:"12", label:"years of the pledge", plain:"Since cities started promising to make what they consume." },
    { n:"2,700+", label:"fab labs", plain:"The production capacity that promise is supposed to run on." },
    { n:"56", label:"signatory cities", plain:"Places that have formally committed." },
    { n:"0", label:"rigorous causal evidence", plain:"A 2025 review of ~1,000 studies found none at the tier where the planetary stakes live." }
  ],
  whyItMatters:"Twelve years of saying cities should produce what they consume, and we still cannot prove it changes the trajectory. Not because nobody tried — because there was no instrument that connected a repair log in one neighbourhood to a planetary limit. That instrument is what the matrix is. It has twenty cells and most are dark. That is not a weakness; that is the work.",
  steps: [
    { n:1, minutes:7, title:"Dot the matrix",
      what:"Scan the twenty cells. Dot only the 3–4 you actually know something about.",
      how:"Open Workshop mode, enter your table and city, then click a cell and mark it green, yellow or dark.",
      rule:"Green means you could pull this data THIS MONTH. Yellow means it exists but you can't reach it. Dark means leave it. Over-claiming green is the classic mistake — if you can't name who would send you the file, it's yellow.",
      dashboard:"The matrix goes from grey to coloured as you dot. That picture is the point: you are seeing which parts of your city are legible and which are dark." },
    { n:2, minutes:5, title:"Pick ONE cell",
      what:"Not the easiest one. The one that matters and is reachable in 30 days.",
      how:"Decide at your table which single dotted cell you'd actually commit to.",
      rule:"If a dark cell matters more than any green one, commit instead to the smallest campaign that would create that data.",
      dashboard:"Open that cell and read its indicators — unit, method, who normally feeds it. That tells you what 'having the data' would concretely mean." },
    { n:3, minutes:5, title:"Fill the card",
      what:"One cell · one source · one name · one date — plus the first step and the real day you'll take it.",
      how:"Fill the card in the cell panel and save it. It appears in the Workshop cards tab.",
      rule:"'Email the data officer, Aug 4' is a first step. 'Explore options' is not.",
      dashboard:"Every table's card lands in one collection sheet the facilitator can read out and follow up on." }
  ],
  afterwards:"You leave with one cell you can defend and one email you'll actually send. The Foundation follows up on that first step — quoting your own words back to you."
};
