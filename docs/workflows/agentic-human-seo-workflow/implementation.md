# Implementation Plan: Agentic Human SEO Workflow

## Executive Summary

The Agentic Human SEO Workflow is being built from scratch by a solo developer. The
mermaid diagram is the complete design blueprint. The build produces a Next.js web
application (React Flow pipeline view, TipTap content editor, gate review screens,
Recharts aftercare dashboard) backed by a FastAPI orchestration layer and a Supabase
(PostgreSQL + Realtime) persistence and real-time layer. The system replaces CLI-based
agent execution with a visual, interactive UI that gives the internal SEO team full
visibility and control over every phase of the pipeline without technical knowledge.

Total estimated build: 14-16 weeks solo.

---

## Sprint 0: Foundations (Week 1-2)

**What changes:**
- Next.js 14 App Router project initialized with TypeScript
- Supabase project created; database schema defined and migrated
- FastAPI project initialized with async SQLAlchemy + Supabase client
- Authentication wired up (Supabase Auth with Next.js middleware)
- Base Pipeline View shell renders (empty React Flow canvas)
- CI/CD pipeline configured (GitHub Actions -> Vercel for frontend, Railway/Fly.io for FastAPI)

**Database schema (Supabase):**
```
jobs              (id, site_url, status, created_at, updated_at)
job_steps         (id, job_id, step_id, status, started_at, completed_at, output_json)
gates             (id, job_id, gate_id, status, reviewer_id, decision, comment, decided_at)
content_drafts    (id, job_id, brief_json, outline_json, body, status, created_at, updated_at)
audit_results     (id, job_id, stream, data_json, created_at)
aftercare_reports (id, job_id, checkpoint, data_json, created_at)
baseline_snapshots(id, job_id, url, metrics_json, captured_at)
monitor_alerts    (id, site_url, alert_type, severity, data_json, created_at)
```

**Tools needed:** Next.js 14, React Flow, Supabase CLI, FastAPI, SQLAlchemy, Alembic,
GitHub Actions, Vercel, Railway (or Fly.io)

**Effort estimate:** 10-12 days

**Dependencies:** None — this is the foundation everything else builds on

**Risks & mitigations:**
- Supabase Realtime channel design must handle multiple concurrent jobs —
  use per-job channels keyed on job_id
- FastAPI on Railway cold starts can be slow — keep a warm instance with health checks

**Success criteria:**
- Next.js app deploys to Vercel and loads the empty Pipeline View
- FastAPI deploys and responds to health check
- Supabase schema migrated and Realtime confirmed working in a test channel

---

## Sprint 1: Audit Pipeline + Gate 1 (Week 2-4)

**What changes:**
- Phase 0 audit agents built as FastAPI BackgroundTasks:
  - Crawl agent (Scrapy + Playwright for JS pages)
  - Technical agent (Lighthouse CI + GSC API for indexability)
  - On-page agent (meta/headings/schema extraction)
  - Content audit agent (topical inventory + thin content detection)
  - Authority agent (Ahrefs API backlink + toxic link)
  - Competitive agent (rank baseline + competitor identification)
  - Analytics agent (GA4 tracking auditor)
- Synthesis agent (Claude API claude-sonnet-4-6 with structured output schema)
- Audit results written to Supabase; Realtime pushes status to Pipeline View
- Gate 1 Review UI: synthesis report display + drag-and-drop priority reordering
  + approve/reject with comment

**Key technical decisions:**
- Each audit agent runs as an independent async task; results written to audit_results
  table as they complete (not waiting for all 7 to finish)
- Synthesis agent is triggered when all 7 streams have a completed record
- Claude API call uses prompt caching on the audit stream schemas to reduce latency

**Effort estimate:** 14-18 days (audit agents are the most complex integration work)

**Dependencies:** Sprint 0 complete

**Risks & mitigations:**
- Ahrefs API rate limits — implement exponential backoff and cache results per domain per day
- Playwright headless browser memory usage — run in a separate worker process with timeout
- Synthesis prompt must produce consistent structured output — define JSON schema and use
  Claude API structured output mode; add retries on validation failure

**Success criteria:**
- Full audit runs end-to-end on a test site; all 7 streams produce results
- Synthesis report renders correctly in Gate 1 UI
- Approve action dispatches the next phase; reject returns with comment visible

---

## Sprint 2: Research + Strategy + Track A (Week 4-6)

**What changes:**
- Research agents: DataForSEO keyword data + SERP analysis + trend detection;
  Claude API for intent classification; SME research flagged as manual task
- Strategy agents: Claude API topic cluster builder + content calendar generator
- Gate 2 UI: calendar timeline view + approve/revise controls
- Track A Technical Remediation agents:
  - Schema/sitemap generation + CMS API push
  - Image optimisation (download, compress, re-upload via CMS API)
  - Meta tag generation + push
  - Canonical/robots.txt/redirect agent (hybrid - writes proposal, human reviews in Gate 2)

**Effort estimate:** 12-14 days

**Dependencies:** Sprint 1 complete (Gate 1 must work to trigger this sprint's flows)

**Risks & mitigations:**
- DataForSEO API costs scale with query volume — cache keyword results per keyword per 7 days
- CMS API varies by client (WordPress vs Webflow vs Contentful) — build an adapter layer
  with a common interface; implement WordPress adapter first as MVP
- Intent classification at scale is slow — batch Claude API calls; use async streaming

**Success criteria:**
- Research results populate the strategy view
- Calendar renders in Gate 2 UI; approve dispatches Track B
- At least 3 of 4 Track A agents run successfully on a test site

---

## Sprint 3: Content Editor + Track B + Gate 3 (Week 6-9)

**What changes:**
- TipTap Content Editor built as a Next.js client component:
  - Left panel: brief + outline + research snippets (read-only, loaded from Supabase)
  - Centre panel: TipTap editor with custom toolbar (word count, keyword density, readability)
  - Right panel: AI co-pilot chat — streaming Claude API via FastAPI SSE endpoint
  - Auto-save to Supabase content_drafts on every 2 seconds of inactivity
- Brief Agent and Outline Agent (FastAPI) generate structured JSON from strategy data
- Editor Agent (Claude API): grammar, tone, structure review with inline suggestions
- Fact-Check Agent: cross-references claims against provided source URLs
- Meta tags / schema markup / alt text agents run automatically on draft completion
- Gate 3 UI: side-by-side content preview (left) + QA report with highlighted issues (right)
  + approve/revise with annotation support

**This is the hardest sprint** — the content editor is the most complex single UI component.

**Key technical decisions:**
- TipTap AI co-pilot extension: custom Node that wraps Claude API streaming via FastAPI
  Server-Sent Events endpoint. Writer types a slash command (/suggest, /expand, /check)
  and the extension calls the SSE endpoint, streams the response as a suggestion bubble.
  Writer accepts or rejects each suggestion individually.
- Draft auto-save uses Supabase client-side upsert with optimistic updates

**Effort estimate:** 18-22 days

**Dependencies:** Sprint 2 complete; Gate 2 must dispatch to Track B

**Risks & mitigations:**
- TipTap co-pilot streaming UX — test with 500ms debounce on suggestion triggers to avoid
  interrupting writing flow
- Fact-check agent requires source URLs — if writer does not provide sources, skip fact-check
  and flag as unverified in QA report
- Gate 3 annotation system — use a simple comment JSON stored in gates table keyed by
  TipTap node ID; display as inline markers in preview mode

**Success criteria:**
- Writer can open editor, see brief and outline, write, invoke co-pilot, and save
- QA report renders in Gate 3 with correct annotations
- Approve at Gate 3 dispatches to publish flow

---

## Sprint 4: Publish + Baseline Snapshot + Gate 4 (Week 9-11)

**What changes:**
- Publish agents: CMS push (content + meta + schema), internal linking agent,
  GSC index ping
- Social draft agent: Claude API generates LinkedIn, Twitter/X, and email newsletter
  drafts; surfaced in Pipeline View for human to copy and post
- Gate 4: one-click publish confirmation in Pipeline View (not a separate screen)
  with optional scheduled publish time picker
- Baseline Snapshot agent: fires on publish confirmation; queries GSC API + GA4 API
  + DataForSEO rank tracker; writes T-zero record to baseline_snapshots table
- Celery + Redis added to infrastructure for scheduled aftercare tasks

**Effort estimate:** 10-12 days

**Dependencies:** Sprint 3 complete

**Risks & mitigations:**
- GSC API data lag (24-48 hours for fresh data) — snapshot agent runs immediately for
  rank data; schedules a GSC re-pull at T+48 hours to capture impression/CTR baseline
- CMS push can fail silently — add webhook confirmation or polling to verify publish
  before marking gate as complete

**Success criteria:**
- Full end-to-end run from onboarding to published page with baseline snapshot captured
- Social drafts visible in Pipeline View
- Celery worker running and accepting scheduled tasks

---

## Sprint 5: Aftercare Agents + Dashboard (Week 11-14)

**What changes:**
- Day 7 check agents (Celery beat task, triggered 7 days after publish_at):
  GSC indexation check, Screaming Frog crawl, Rich Results Test API, internal link verify
- Day 30 check agents: rank trajectory, traffic vs forecast, cannibalization re-check,
  Ahrefs backlink earn tracker, SERP feature capture
- Day 90 check agents: full performance pull, Claude API ROI narrative, competitor delta
- Classification engine: rule-based outcome scoring + Claude API for edge cases
- Aftercare Dashboard built in Next.js:
  - Per-page tabs: Day 7 / Day 30 / Day 90
  - Then & Now delta cards (rank change, traffic change, CTR change)
  - Recharts line charts: traffic vs forecast, rank over time
  - Outcome badge: Winner / Steady / Underperformer / Loser
  - Action recommendations rendered from classification engine output
  - Site-wide filter and monthly digest view
- Repurpose Pipeline: generates repurpose brief + outreach brief; routes new content
  briefs back to Track B; outreach brief sent to human outreach specialist
- Refresh Pipeline: gap diagnosis + updated brief; routes to Track B and resets clock

**Effort estimate:** 16-20 days (dashboard is the most data-intensive frontend work)

**Dependencies:** Sprint 4 complete; Celery infrastructure running

**Risks & mitigations:**
- Forecast model for traffic vs actual: use a simple linear regression on early GSC data
  rather than a complex ML model — simpler to build and explain; can upgrade later
- Aftercare jobs must be idempotent — if a Celery task fails and retries, it should not
  double-insert results; use upsert with (job_id, checkpoint) as unique key

**Success criteria:**
- Day 7 report auto-generates 7 days after a test publish
- Aftercare Dashboard renders all three checkpoint tabs with correct delta values
- Outcome classification routes correctly for all four outcome types

---

## Sprint 6: Continuous Monitor + Alerting + Polish (Week 14-15)

**What changes:**
- Monitor agent cluster runs on daily Celery cron for all active site URLs
- Anomaly detection: statistical thresholds on rank drops and traffic changes
  (configurable per site — default: alert if rank drops more than 10 positions or
  traffic drops more than 20% week-over-week)
- Decay detection: pages that have not improved for 60 days flagged for refresh
- Alerts surface in Pipeline View as notification badges on affected job nodes
- Human SEO Manager receives in-app notifications (Supabase Realtime) and optional
  email digest (Resend API)
- Monitor signals feed back to Orchestrator for automated re-dispatch of fix agents
- UI polish pass: loading states, error boundaries, empty states, responsive layout,
  keyboard shortcuts for gate approve/reject

**Effort estimate:** 8-10 days

**Dependencies:** Sprint 5 complete

**Success criteria:**
- Monitor runs daily and writes alerts to monitor_alerts table
- Alerts appear in Pipeline View within 60 seconds of detection (Realtime)
- UI passes a manual accessibility check and has no console errors on production

---

## Sprint 7: Testing + Documentation + Handover (Week 15-16)

**What changes:**
- End-to-end test run: onboard a real site, run full pipeline to Day 7 checkpoint
- Performance audit: FastAPI agent response times, Supabase query performance, React Flow
  render performance with 20+ active nodes
- Security review: API key storage (Supabase Vault), Supabase RLS policies, Next.js
  middleware auth on all routes
- Internal documentation: agent configuration guide, how to add a new CMS adapter,
  how to tune anomaly detection thresholds

**Effort estimate:** 8-10 days

**Success criteria:**
- Full pipeline runs end-to-end without manual intervention except at the 4 gate points
- No API keys exposed in client-side code
- All 4 UI screens render correctly on Chrome, Firefox, and Safari

---

## KPIs & Success Metrics

| Metric | Current | Target | How Measured |
|---|---|---|---|
| Audit-to-Gate-1 time | N/A (not built) | under 4 hours | job_steps.completed_at delta |
| Gate throughput rate | N/A | over 80% first-pass approval | gates table: approved/total |
| Content production rate | N/A | per calendar | content_drafts published/week |
| Winner rate (Day 90) | N/A | over 40% | outcome_classification = winner |
| Organic traffic lift | N/A | over 15% MoM at 90 days | GA4 organic sessions delta |
| Time to index | N/A | under 48 hours | GSC indexation timestamp |
| Pipeline UI uptime | N/A | over 99.5% | Vercel / Railway uptime monitoring |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| API rate limits (Ahrefs, DataForSEO) | High | Medium | Cache per domain per day; exponential backoff |
| CMS API variability across clients | High | High | Build adapter layer; ship WordPress first; add others iteratively |
| Claude API latency in editor co-pilot | Medium | High | Stream responses; show typing indicator; 2s debounce on triggers |
| Supabase Realtime connection drops | Low | High | Client-side reconnect with exponential backoff; UI shows stale indicator |
| Solo developer burnout | Medium | High | Fixed sprint boundaries; no scope creep mid-sprint; clear MVP per sprint |
| Agent hallucination in synthesis | Medium | Medium | Structured output mode + JSON schema validation + human Gate 1 review |
| Fact-check agent misses claims | Medium | Low | Flag as limitation in Gate 3 UI; writer remains responsible for accuracy |

---

## Change Management

**Training requirements:**
- SEO Manager: 1-hour walkthrough of Pipeline View, Gate Review, and Aftercare Dashboard
- Writer/SME: 30-minute walkthrough of Content Editor and co-pilot usage
- No technical training required — the UI is the interface

**Communication plan:**
- Sprint demos after each sprint with the full internal team
- Slack channel for bug reports and feedback during beta
- Release notes doc updated after each sprint merge to main

**Rollback plan:**
- All database migrations are reversible via Alembic downgrade
- Feature flags (Supabase config table) allow individual agent clusters to be disabled
  without redeploying; falls back to manual CLI invocation for that step
- Vercel instant rollback to previous deployment if a critical UI bug is discovered

---

## Tool & Stack Summary

| Layer | Current | Proposed | Approach |
|---|---|---|---|
| Workflow execution | None (mermaid design) | FastAPI + Celery + Redis | AI-first orchestration |
| Database | None | Supabase (PostgreSQL) | Cloud-managed |
| Real-time UI updates | None | Supabase Realtime | WebSocket subscriptions |
| Frontend | None | Next.js 14 App Router | Server + client components |
| Pipeline visualisation | Static mermaid file | React Flow (live) | Interactive node graph |
| Content editor | None | TipTap + Claude API co-pilot | Hybrid human+AI |
| Charts | None | Recharts / Tremor | React-native |
| LLM | None | Claude API claude-sonnet-4-6 | Primary AI layer |
| Keyword/SERP data | None | DataForSEO | REST API |
| Backlink data | None | Ahrefs API | REST API |
| Google data | None | GSC API + GA4 API | Google client libs |
| Auth | None | Supabase Auth | Row-level security |
| Deployment (frontend) | None | Vercel | Auto-deploy from GitHub |
| Deployment (backend) | None | Railway or Fly.io | Docker container |
| Email notifications | None | Resend API | Transactional email |
