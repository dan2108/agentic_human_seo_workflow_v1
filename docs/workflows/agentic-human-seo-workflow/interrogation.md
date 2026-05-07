# Interrogation Log: Agentic Human SEO Workflow

**Source document:** `agentic_human_seo_workflow_v1/master-agentic-human-workflow.mermaid`
**Session date:** 2026-05-07
**Method:** Mermaid diagram analysis + structured Q&A

---

## Phase 0 - Discovery

As-is workflow derived directly from `master-agentic-human-workflow.mermaid`.
No prior interrogation directory existed. The diagram provided a complete current-state
design covering all actors, steps, decisions, and automation classifications.

Key entities extracted from diagram:
- **Actors:** AI System, SEO Orchestrator, Aftercare Orchestrator, Human SEO Manager, Human Writer/SME, Human Outreach Specialist
- **Triggers:** Site onboarding, content calendar, monitoring anomaly, quarterly schedule
- **Phases:** Input > Audit > Orchestration > Research > Strategy > Technical + Content > QA > Publish > Aftercare (Day 7/30/90) > Continuous Monitor
- **Gates:** 4 human approval gates (Audit Plan, Strategy & Calendar, Human Final Read, Content Publish)
- **Automation breakdown:** ~65% AI-only, ~25% Hybrid, ~10% Human-led

---

## Phase 1 - Scope & Objectives (Round 1)

**Q: Who is the primary audience?**
A: Internal team only.

**Q: What does the UI/UX need to do?**
A: All four capabilities - visualise the pipeline with live status, surface approval gates
for human sign-off, provide a content creation workspace, and show an aftercare
performance dashboard. Key addition: the UI should replace CLI execution entirely,
letting the team see each phase of the workflow running from the browser.

**Q: What tech stack?**
A: React / Next.js (decided).

**Q: What is the primary goal?**
A: Build guide - engineering spec for the dev team.

---

## Phase 2 - Stakeholder & Actor Mapping (Round 1)

**Q: How is the workflow currently being run?**
A: Not built yet. The mermaid diagram is the design. Everything needs to be built from scratch.

**Q: Which UI screens are needed?**
A: All four - Pipeline View (live status), Gate Review (approve/reject AI output),
Content Editor (writer + AI co-pilot workspace), Aftercare Dashboard (Day 7/30/90 metrics).

**Q: What is the backend layer?**
A: Not decided - recommendation requested.

**Q: What is the timeline and team size?**
A: Solo developer, weeks not months.

---

## Phase 3 - Current State

Fully derived from mermaid diagram. See `workflow.yaml` steps array and
`diagrams/flowchart-as-is.md` for visual representation.

Automation classification extracted from node styles:
- aiStyle = fully automated
- hybridStyle = AI-generated, human-reviewed
- humanStyle = human-led, no agentic substitute
- gateStyle = human approval required
- brainStyle = AI orchestrator

---

## Phase 4 - Pain Points

As the system is not yet built, pain points are design-level risks:

1. **No persistence layer defined** - pipeline state lost between runs without a database
2. **No real-time feedback mechanism** - UI cannot show live agent progress without WebSockets or polling
3. **Undefined gate data contracts** - AI output format must be standardised before gate UI can be built
4. **Aftercare scheduling** - Day 7/30/90 cadence requires a scheduler designed in from the start
5. **Content editor co-pilot integration** - AI brief/outline must be API-accessible within the editor view
6. **Multiple concurrent pipelines** - job isolation and state management become complex at scale

---

## Phase 5 - Automation Scoring

Derived from mermaid node styles:
- aiStyle nodes: automation_score impact=5, feasibility=5 (fully automated)
- hybridStyle nodes: automation_score impact=4, feasibility=3 (AI-augmented, human review)
- humanStyle nodes: automation_score impact=2, feasibility=1 (intentionally manual)
- gateStyle nodes: automation_score impact=5, feasibility=1 (gates must stay human)

Quick wins (high impact x high feasibility):
- Synthesis Agent (5x5)
- Baseline Snapshot (5x5)
- Day 7 Health Check (5x5)
- Continuous Monitor (5x5)
- SEO Orchestrator Dispatch (5x5)

Strategic investments (high impact, lower feasibility):
- Full Phase 0 Audit build-out (5x4) - API integrations complex
- Track B Content Editor (5x3) - rich editor + co-pilot integration is the hardest single piece
- Research Phase (5x4) - multiple API sources to wire up

---

## Phase 6 - Future State

The to-be state adds a React/Next.js UI layer on top of the workflow:
- **Pipeline View:** React Flow graph with live Supabase Realtime status subscriptions
- **Gate Review UI:** Per-gate screens with AI output display and approve/revise controls
- **Content Editor:** TipTap three-panel workspace with Claude API co-pilot
- **Aftercare Dashboard:** Recharts/Tremor delta charts per Day 7/30/90 checkpoint

No steps in the workflow are removed or replaced - the UI is a control and visibility layer,
not a redesign of the underlying agentic logic.

---

## Phase 7 - Tool Recommendations

**Frontend:**
- Next.js 14 App Router - server components for data-heavy views, client components for interactive UI
- React Flow - purpose-built for interactive node graphs with live status overlays
- TipTap - extensible headless editor, ideal for AI co-pilot extension integration
- Recharts or Tremor - React-native charts for aftercare dashboard

**Backend:**
- FastAPI (Python) - natural fit for AI/LLM agent orchestration; async; clean REST + WebSocket API
- Chosen over Node.js because Python is the dominant language for AI agent libraries

**Database:**
- Supabase (PostgreSQL + Realtime) - eliminates need for separate Redis pub/sub
- Built-in auth, row-level security, and Realtime subscriptions power live pipeline status
- Single service reduces solo developer operational overhead significantly

**Task Queue:**
- FastAPI BackgroundTasks for short jobs (under 30 seconds)
- Celery + Redis for long-running agent chains (audit, Day 30/90 aftercare)

**AI/LLM:**
- Claude API (claude-sonnet-4-6) as primary LLM for synthesis, intent classification, co-pilot
- Structured output mode for all data-extraction tasks

**SEO Data APIs:**
- DataForSEO - keyword data, SERP analysis, rank tracking
- Ahrefs API - backlink profile and authority data
- GSC API + GA4 API - Google-native performance data
- Screaming Frog API - crawl and technical audit data

---

## Phase 8 - Implementation Plan

See `implementation.md` for full phased plan with effort estimates and sprint structure.
