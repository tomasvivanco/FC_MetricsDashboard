# 07 · Professionalisation roadmap

What separates this working research build from an instrument a city government, a funder or a peer
reviewer would treat as production-grade — and which capability handles each gap.

**Read the constraint first.** The dashboard is deliberately a single HTML file with no build step, no
dependencies and no framework. That is not laziness; it is what makes it openable in five years, readable
without tooling, and handable to a city as one offline file. **Most items below can be done without
breaking that.** The two that cannot are marked ⚠ — treat them as a considered architectural decision,
not a default.

Priority key: **P1** blocks credibility · **P2** blocks adoption · **P3** compounding quality

---

## A · Evidence and method — the credibility layer

*Nothing else matters if the numbers do not hold. These are research tasks, not engineering.*

| # | Gap | Why it blocks | Capability |
|---|---|---|---|
| **P1** | **Boeing recovery is sketched, not formal.** No worked example on public data. | The single most predictable reviewer objection. Until it is closed, the lineage claim is an assertion. | Academic research writing · analysis of NACE/COICOP data |
| **P1** | **ρ has no measurement protocol at v1.** Tier-weighting and council-rejection handling open. | Without ρ the index is a snapshot, and the metabolism *is* the contribution. No city can have a complete FCI number. | Academic research writing · methodology design |
| **P1** | **Three contested weight cells** — Economic × Bioregion, Environmental × Community, Economic × Community. | Flagged upstream. Reviewers will find them. Either sharpen the argument or document why they stand. | Academic research writing |
| **P2** | **Fourteen of twenty weights are reconstructed.** | They are honestly marked, but a research instrument wants canon. Needs Foundation sign-off or a published table. | Coordination with the Foundation |
| **P2** | **No peer review.** Working paper plus a doctoral thesis, not reviewed in its own right. | Determines whether cities can cite it in policy documents. | Academic research writing · journal submission |
| **P3** | **No inter-rater reliability test.** Two labs scoring the same cell may diverge silently. | Comparability across cities is the whole premise of a network index. | Research design · a small multi-lab study |

**Suggested sequence:** the Hamburg worked example first (highest ratio of credibility to effort), then
the ρ protocol, then the three weight cells as a single methods note.

---

## B · Data and engineering — the trust layer

| # | Gap | Why it blocks | Capability |
|---|---|---|---|
| **P1** | **Live connectors do not refresh.** Fetch-on-demand only; browser CORS blocks many endpoints. | "Live" that needs a human click is not live. Undermines the reading-kind distinction that is the instrument's soul. | ⚠ Serverless scheduled fetch (Cloudflare Worker / GitHub Action writing a JSON snapshot into the repo — keeps the frontend dependency-free) |
| **P1** | **No sovereignty gate.** Documented, not enforced. No accounts, no roles. | **Hard prerequisite** before any real community data is published. Bali's three-body flow is a design, not an agreement in force. | Access-control design · governance work with custodian communities |
| **P2** | **Nine network-own sources unwired.** fablabs.io, Smart Citizen, Precious Plastic et al. | The only honest route to lighting City/Region cells. Six are low-effort API calls against registries the network already runs. | API integration — **highest leverage engineering task available** |
| **P2** | **No automated tests in CI.** Verification is manual jsdom runs. | A contributor can silently break the matrix, the normalisation, or the validator. | GitHub Actions · headless test harness |
| **P2** | **No schema versioning.** Changing an indicator `name`/`unit`/`direction` breaks existing submissions with no migration path. | Submissions bind to those strings. This will bite the first time the model evolves. | Data modelling · versioned schema + migration notes |
| **P3** | **localStorage only.** Readings live in one browser; nothing syncs, nothing is shared. | Fine for a workshop, wrong for an operator. | ⚠ Backend, or the snapshot-in-repo pattern above |
| **P3** | **No provenance ledger.** Readings carry source and date but there is no append-only history. | The upstream design promises "every deploy on a public ledger". Git already gives most of this if readings are committed. | Data architecture |

**The pattern worth adopting:** a scheduled GitHub Action that fetches each wired source, normalises it,
and commits a JSON snapshot into the repo. Live data, full git history as the provenance ledger, and the
frontend stays a static file with zero dependencies. It resolves P1-connectors, P3-persistence and
P3-ledger in one move.

---

## C · Interface and accessibility — the adoption layer

*Where the `design:*` skills apply directly. Run these against the live page.*

| # | Gap | Why it blocks | Capability |
|---|---|---|---|
| **P1** | **No accessibility audit.** Contrast of tinted cells, keyboard navigation of the matrix, screen-reader semantics of the 20-cell grid, focus order in the reading panel — none verified. | A public-sector instrument in the EU or US may be legally required to meet WCAG 2.1 AA. Also: the cross-hatch that distinguishes estimates must not be the *only* cue. | `design:accessibility-review` |
| **P2** | **No design system documentation.** Colours, spacing and type are inline CSS variables with no documented scale. | Any contributor styles by imitation and it drifts within three commits. | `design:design-system` |
| **P2** | **UX copy never audited as a system.** Written well, but error messages, empty states and button labels have not been reviewed together. | Consistency of voice is what makes an instrument feel authoritative. | `design:ux-copy` |
| **P2** | **No usability testing with real operators.** Design decisions rest on reasoning, not observation. | The reading-kinds distinction is the core bet. It has never been tested on someone who did not build it. | `design:user-research` → `design:research-synthesis` |
| **P3** | **No structured design critique** of hierarchy and information density in the matrix. | Twenty cells with five data points each is a lot; it has not been stress-tested for legibility. | `design:design-critique` |
| **P3** | **Mobile layout unverified.** Matrix scrolls horizontally; never tested at 375 px. | Workshop participants will open it on phones. | `design:accessibility-review` · manual testing |
| **P3** | **No print / PDF export.** A city officer will want to take a page into a meeting. | | `pdf` skill · CSS print stylesheet |

**Do the accessibility audit first.** It is the one item here with a legal dimension, and it will surface
contrast problems in the PITO/DIDO gradient that are cheaper to fix now than after cities adopt it.

---

## D · Communication and adoption — the reach layer

| # | Gap | Capability |
|---|---|---|
| **P2** | No explainer for non-technical decision-makers — a mayor's office needs two pages, not a dashboard. | `docx` · `pdf` · academic/professional writing |
| **P2** | No onboarding path for a new pilot city. What does week one actually look like? | Process design · `docx` |
| **P3** | No launch narrative for the network — announcement, positioning against prior generations. | `marketing:draft-content` · `marketing:campaign-plan` |
| **P3** | Workshop deck and dashboard are maintained separately and can drift. | `pptx` — generate deck figures from `assets/data.js` |
| **P3** | No visual identity beyond inherited FCI 3.0 paper tone. | `design:design-system` |
| **P3** | Not discoverable — no meta tags, no Open Graph card, no search presence. | `marketing:seo-audit` |

---

## E · Governance and operations

| # | Gap | Why it matters |
|---|---|---|
| **P1** | **No licence file.** The repo is public with no stated terms. | Nobody can legally reuse or contribute with confidence. Pick one deliberately — likely CC-BY for docs, MIT or AGPL for code. |
| **P2** | **No CONTRIBUTING.md or PR template.** | Submissions and code changes arrive unstructured. |
| **P2** | **No issue templates** for the two flows that matter: "propose an indicator change" and "submit city data". | |
| **P2** | **No decision log.** `HANDOVER.md` records *what* was decided; nothing records *when and why* going forward. | ADRs are cheap and prevent re-litigating settled questions. |
| **P3** | **No release tagging.** `META.version` is hand-maintained. | Cities need to cite a version. |
| **P3** | **Single maintainer.** One person holds all context. | `HANDOVER.md` mitigates this; a second reviewer would resolve it. |

**Do the licence this week.** It is fifteen minutes and it is currently blocking anyone from contributing
in good faith.

---

## The honest shortlist

If only five things get done, these five, in order:

1. **Add a LICENSE.** Fifteen minutes. Unblocks everyone else.
2. **Run `design:accessibility-review` on the live page.** Legal dimension, and it will find real contrast
   problems in the gradient.
3. **Wire three network-own connectors via a scheduled GitHub Action** committing JSON snapshots. Solves
   live data, persistence and the provenance ledger together, without breaking the no-build constraint.
4. **Write the worked Hamburg example.** Closes the most predictable reviewer objection and secures the
   lineage argument that gives the instrument its standing.
5. **Test the reading-kinds distinction on five people who did not build it.** It is the core design bet
   and it has never met a stranger.

Everything else compounds. These five change what the instrument *is*.

---

## A note on scope discipline

The temptation with an instrument like this is to add cells, add pillars, add scales. Resist it.

**Twenty cells with honest provenance beats forty with guesses.** The framework's own finding — that only
17% of indicators are lab-measurable — is an argument for depth over breadth. The instrument's value is
that it says clearly what it does not know. Every feature that blurs that line costs more than it adds.
