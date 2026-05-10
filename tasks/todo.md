# STAR — Verify Gate Dispatch Wiring (2026-05-10)

## Situation
- New: content_orchestrator.py, publish_orchestrator.py, gates.py rewrite, test_gates.py extension, 3 new settings
- pytest from `cd apps/api` failed: ModuleNotFoundError structlog — venv not active
- cd polluted cwd; rerun from repo root with absolute paths

## Task
1. Locate apps/api venv
2. Run pytest with right interpreter
3. 8/8 tests pass

## Action
1. Return to repo root
2. Find venv (.venv, uv env)
3. Run pytest via that interpreter
4. Fix failures

## Result
8/8 green; each test_approve_gate{N}_dispatches_* passes.

---

# STAR — Wire Gate → Orchestrator Handoff (2026-05-10)

## Situation
- gates.py:approve_gate updates DB but does not dispatch next phase
- Research + Aftercare orchestrators exist but never invoked from gate approval
- No Content or Publish orchestrators yet — only standalone agents
- Pipeline stalls at Gate 1 even with Sprints 2-4 code present

## Task
1. Gate 1 approve → ResearchOrchestrator.dispatch in background
2. Gate 2 approve → content pipeline (brief → outline)
3. Gate 3 approve → publish pipeline (cms → linking → distribution → index_ping → snapshot)
4. Gate 4 approve → AftercareOrchestrator.schedule (Celery)
5. Use FastAPI BackgroundTasks (existing pattern in jobs.py)
6. Dispatch failure does NOT roll back gate approval

## Action
1. Read apps/api/app/routers/jobs.py for BackgroundTasks pattern
2. Read seo_orchestrator constructor for settings injection
3. Create apps/api/app/orchestrators/content_orchestrator.py (brief + outline)
4. Create apps/api/app/orchestrators/publish_orchestrator.py (cms+linking+distribution+index_ping+snapshot)
5. Modify gates.py approve_gate: BackgroundTasks param, fetch job for site_url, dispatch per gate_name
6. Add unit test in test_gates.py asserting BackgroundTasks.add_task called with right orchestrator

## Result
pytest apps/api/tests/test_gates.py green; approve_gate response immediate; gate1 dispatch logged; new orchestrator files lint-clean.

---

# STAR — Codebase Audit (2026-05-10)

## Situation
- Branch: build/agentic-seo-workflow on Windows monorepo
- 3 commits landed (Sprint 0 scaffold + pipeline UI shell + Sprint 1 audit agents/AuditGate)
- Active build per .agentops/build-state.json; many modified/untracked files in apps/api and apps/web indicate Sprint 2-4 work in flight
- User invoked /agentops:build asking for codebase audit + next steps (not a fresh build kickoff)

## Task — Success criteria
1. Identify in-progress build's current phase
2. Inventory shipped vs in-flight vs not-started work
3. Map progress against tasks/todo.md sprints S0-S7
4. Recommend 3-5 prioritized next steps with concrete file paths

## Action — Concrete steps
1. Read .agentops/build-state.json for phase context
2. Read docs/build/agentic-seo-workflow/ artifacts (brief, requirements, plan)
3. Inventory apps/api/app/agents/** (research/content/qa/publish/aftercare)
4. Inventory apps/api/app/orchestrators/** for orchestrator coverage
5. Inventory apps/web/components/gates/** and app/(dashboard)/** for UI gates
6. Cross-reference modified/untracked file list with sprint structure
7. Produce written status report

## Result — Verification
Status report covering: (a) committed/complete, (b) modified-uncommitted/in-flight, (c) remaining sprints, (d) prioritized next moves with file paths the user can act on.

---

## Sprint 0 — Foundations (Week 1-2)
- [ ] S0-T01 [M] Init git repo + feature branch `build/agentic-seo-workflow`
- [ ] S0-T02 [M] pnpm install: Next.js deps (reactflow, tiptap, recharts, supabase-js)
- [ ] S0-T03 [M] uv sync: FastAPI deps (fastapi, anthropic, celery, supabase, structlog)
- [ ] S0-T04 [S] Supabase local: `supabase start` + run migration 20260507000000_initial_schema.sql
- [ ] S0-T05 [M] FastAPI: wire all routers in main.py + confirm /health returns 200 (test exists in test_jobs.py)
- [ ] S0-T06 [M] Next.js: Supabase Auth login flow (apps/web/app/(auth)/login/page.tsx)
- [ ] S0-T07 [M] Next.js: middleware.ts session refresh on all dashboard routes
- [ ] S0-T08 [L] Pipeline View shell: React Flow canvas in PipelineCanvas.tsx with static node layout matching mermaid diagram
- [ ] S0-T09 [M] Supabase Realtime: usePipelineStatus hook subscribes to job_steps channel, updates node colours
- [ ] S0-T10 [S] Docker Compose: verify all services start (`docker-compose up -d`)
**Done condition:** `pnpm dev` loads Pipeline View; FastAPI /health returns 200; Supabase local running with migrated schema.
---
## Sprint 1 — Phase 0 Audit Agents + Gate 1 UI (Week 2-4)
- [ ] S1-T01 [M] CrawlAgent: Scrapy + Playwright spider, writes to audit_results (stream=crawl)
- [ ] S1-T02 [M] TechnicalAgent: Lighthouse CI CWV + GSC indexability check
- [ ] S1-T03 [M] OnPageAgent: meta/headings/schema extraction via BeautifulSoup
- [ ] S1-T04 [M] ContentAuditAgent: topical inventory + thin content detection (Claude API)
- [ ] S1-T05 [M] AuthorityAgent: Ahrefs API backlink profile + toxic link list
- [ ] S1-T06 [M] CompetitiveAgent: DataForSEO rank baseline + top competitor identification
- [ ] S1-T07 [S] AnalyticsAgent: GA4 tracking tag auditor
- [ ] S1-T08 [L] SynthesisAgent: Claude API aggregates all 7 streams into priority report (structured output)
- [ ] S1-T09 [M] SEOOrchestrator.dispatch: triggers all 7 audit agents as FastAPI BackgroundTasks, updates job_steps
- [ ] S1-T10 [L] AuditGate component: renders synthesis report + priority reordering + approve/reject with comment
- [ ] S1-T11 [M] Gate 1 API: POST /gates/gate1/approve dispatches orchestrator
**Done condition:** POST /jobs/ triggers full audit run; AuditGate UI renders synthesis report; approve dispatches next phase.
---
## Sprint 2 — Research + Strategy + Gate 2 + Track A (Week 4-6)
- [ ] S2-T01 [M] KeywordAgent: DataForSEO keyword volume + difficulty data
- [ ] S2-T02 [M] SerpAgent: DataForSEO SERP analysis + SERP feature detection
- [ ] S2-T03 [M] IntentAgent: Claude API classifies intent for each target keyword (batch)
- [ ] S2-T04 [M] ClusterAgent: Claude API builds topic clusters from keyword + intent data
- [ ] S2-T05 [M] CalendarAgent: Claude API generates content calendar from clusters
- [ ] S2-T06 [L] StrategyGate component: calendar timeline view + approve/revise controls
- [ ] S2-T07 [M] SchemaAgent: generate JSON-LD schema markup + push via CMS adapter
- [ ] S2-T08 [M] ImageAgent: download, compress (Pillow), re-upload via CMS adapter
- [ ] S2-T09 [M] MetaAgent: generate optimised meta titles/descriptions, push via CMS
- [ ] S2-T10 [M] WordPressAdapter: implement publish() and update_meta() against WP REST API
**Done condition:** Research runs end-to-end; StrategyGate UI renders calendar; Track A technical fixes apply to a test WP site.
---
## Sprint 3 — Content Editor + Track B Pipeline + Gate 3 (Week 6-9)
- [ ] S3-T01 [M] BriefAgent: Claude API generates structured brief JSON from strategy data
- [ ] S3-T02 [M] OutlineAgent: Claude API generates H2/H3 outline from brief
- [ ] S3-T03 [L] ContentEditor component: three-panel layout (BriefPanel + EditorPanel + CopilotPanel)
- [ ] S3-T04 [L] TipTap editor: StarterKit + word count toolbar + keyword density indicator
- [ ] S3-T05 [L] CopilotPanel: streaming SSE from FastAPI /content/{id}/copilot endpoint (Claude API)
- [ ] S3-T06 [M] Auto-save: PATCH /content/{id} on 2s inactivity, optimistic update in UI
- [ ] S3-T07 [M] EditorAgent: Claude API grammar/tone/structure review with inline suggestions
- [ ] S3-T08 [M] FactCheckAgent: cross-reference claims against provided source URLs
- [ ] S3-T09 [M] VoiceCheckAgent: Claude API brand voice alignment score (0-100)
- [ ] S3-T10 [M] PlagiarismAgent: Copyscape API integration
- [ ] S3-T11 [L] ContentGate component: side-by-side content preview + QA annotations + approve/revise
**Done condition:** Writer opens editor with pre-populated brief and outline; co-pilot streams suggestions; Gate 3 shows QA report alongside content.
---
## Sprint 4 — Publish + Gate 4 + Baseline Snapshot (Week 9-11)
- [ ] S4-T01 [M] CmsAgent: orchestrate full publish sequence (content + meta + schema via WordPressAdapter)
- [ ] S4-T02 [M] LinkingAgent: detect internal link opportunities + inject via CMS adapter
- [ ] S4-T03 [S] IndexPingAgent: GSC Indexing API request on published URL
- [ ] S4-T04 [M] DistributionAgent: Claude API drafts LinkedIn + Twitter/X + email newsletter copy
- [ ] S4-T05 [S] PublishGate component: one-click confirm with optional scheduled publish datetime
- [ ] S4-T06 [M] SnapshotAgent: GSC API + DataForSEO rank snapshot immediately on publish; writes to baseline_snapshots
- [ ] S4-T07 [M] GSCAdapter: implement get_impressions() and request_indexing()
- [ ] S4-T08 [M] Celery infrastructure: Celery + Redis running; day7/30/90 tasks enqueue with ETA offset from published_at
- [ ] S4-T09 [S] AftercareOrchestrator.schedule: enqueue all three Celery tasks on publish event
**Done condition:** Full end-to-end run from job creation to published page; baseline snapshot captured; Celery tasks enqueued with correct ETAs.
---
## Sprint 5 — Aftercare Agents + Dashboard (Week 11-14)
- [ ] S5-T01 [M] Day7Agent: GSC indexation check + Screaming Frog crawl + Rich Results Test
- [ ] S5-T02 [M] Day30Agent: rank trajectory + traffic vs forecast + Ahrefs backlink earn tracker
- [ ] S5-T03 [M] Day90Agent: full performance pull + Claude API ROI narrative + competitor delta
- [ ] S5-T04 [M] Classification engine in Day90Agent: rule-based outcome + LLM edge case handling
- [ ] S5-T05 [L] AftercareDashboard: Day7Tab + Day30Tab + Day90Tab with DeltaCard + OutcomeBadge
- [ ] S5-T06 [M] DeltaCard: rank/traffic/CTR delta vs baseline_snapshots; colour-coded arrows
- [ ] S5-T07 [M] Recharts line charts: traffic vs forecast + rank over time per checkpoint
- [ ] S5-T08 [M] Repurpose Pipeline: generate repurpose brief + outreach brief on Winner classification
- [ ] S5-T09 [M] Refresh Pipeline: gap diagnosis + updated brief on Underperformer classification
**Done condition:** Day 7 report auto-generates 7 days after a test publish; AftercareDashboard renders all three tabs; outcome routes correctly.
---
## Sprint 6 — Continuous Monitor + Alerts + UI Polish (Week 14-15)
- [ ] S6-T01 [M] MonitorAgent: daily Celery cron queries GSC + DataForSEO for all active sites
- [ ] S6-T02 [M] Anomaly detection: rank drop >10 positions or traffic drop >20% WoW triggers alert
- [ ] S6-T03 [M] Decay detection: flag pages with no improvement in 60 days
- [ ] S6-T04 [M] Alerts: write to monitor_alerts; Supabase Realtime pushes to Pipeline View notification badge
- [ ] S6-T05 [S] Email digest: Resend API sends daily alert summary to SEO manager
- [ ] S6-T06 [M] Pipeline View: loading states, error boundaries, empty states, gate pulse animation
- [ ] S6-T07 [S] Keyboard shortcuts: approve gate (Cmd+Enter), reject (Cmd+R), navigate between gates (Tab)
- [ ] S6-T08 [M] Responsive layout: all four screens usable at 1280px minimum width
**Done condition:** Monitor runs daily; alerts appear in Pipeline View within 60s; UI has no console errors on production build.
---
## Sprint 7 — Testing + Security + Documentation (Week 15-16)
- [ ] S7-T01 [L] End-to-end test: onboard a real site, run full pipeline to Day 7 checkpoint
- [ ] S7-T02 [M] pytest coverage: target 70%+ on routers and agents
- [ ] S7-T03 [M] Security: API keys stored in Supabase Vault; no secrets in client bundle
- [ ] S7-T04 [M] Supabase RLS: verify row-level security policies with test users
- [ ] S7-T05 [M] Performance: React Flow renders 30 nodes without jank; FastAPI agent endpoints <5s p95
- [ ] S7-T06 [S] pyproject.toml ruff + mypy clean on apps/api
- [ ] S7-T07 [S] TypeScript strict mode clean on apps/web
- [ ] S7-T08 [S] Update README.md with final quick-start instructions
**Done condition:** Full pipeline runs without manual intervention except at 4 gate points; no API keys in client JS; test suite green.
---
---
## Sprint 4 Frontend — STAR
- [ ] PublishGate.tsx component
- [ ] gate4 routing in [gateId]/page.tsx
- [ ] TypeScript check (npx tsc --noEmit)
