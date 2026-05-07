# Narrative: Agentic Human SEO Workflow

## Overview

The Agentic Human SEO Workflow is a full-lifecycle SEO system that orchestrates AI agents,
hybrid human-AI collaboration, and human-led decisions across every stage of the SEO
process — from initial site audit through content publication and long-term performance
monitoring. The workflow is currently a design blueprint (captured in
`master-agentic-human-workflow.mermaid`); the build goal is a Next.js web application
backed by FastAPI and Supabase that gives the internal SEO team a visual, interactive
interface to manage every phase without touching a CLI.

---

## Actors & Stakeholders

### AI Agent System
Handles all fully-automated steps: site crawling, technical auditing, keyword data
collection, SERP analysis, schema/sitemap fixes, image optimisation, meta tag generation,
QA checks (plagiarism, brand voice, schema validation), CMS publishing, index pinging,
baseline snapshots, Day 7/30/90 aftercare checks, and continuous monitoring. The AI system
is the workhorse — it operates continuously in the background and surfaces results to the
UI in real time via Supabase Realtime.

### SEO Orchestrator
A FastAPI service that acts as the central brain. After Gate 1 approval, it fans out work
to the Research and Technical Remediation tracks in parallel. It receives signals from the
Continuous Monitor (anomalies, decay, new gaps) and routes them to the appropriate agent
cluster. It also feeds strategic adjustment signals from the Monthly Aftercare Digest back
into the research and strategy pipeline.

### Aftercare Orchestrator
A separate FastAPI service that manages the post-publish cadence. Triggered by the
`content_published` event, it schedules Day 7, Day 30, and Day 90 checks using Celery
beat tasks. Each checkpoint feeds into the Then & Now comparison layer and ultimately
drives the outcome classification (Winner / Steady / Underperformer / Loser).

### Human SEO Manager
The primary operator of the workflow. Responsible for four approval gates, initial backlog
prioritization, editorial angle definition, and strategic reviews at Day 90. The manager
uses the Pipeline View as their primary workspace — it shows live job status across all
active pipelines and alerts them when a gate requires action.

### Human Writer / SME
Operates entirely within the Content Editor screen. The writer receives a pre-populated
brief, AI-generated outline, and research snippets in the left panel; writes in a TipTap
rich text editor in the centre; and can invoke the AI co-pilot (Claude API) via a chat
panel on the right for suggestions, expansions, or style checks. The writer is never
replaced by AI — this is the one step in the workflow where human judgment, first-person
experience, and brand voice are non-negotiable.

### Human Outreach Specialist
Handles all link building, PR, and external outreach generated as recommendations from the
Repurpose Pipeline. There is no agentic substitute for this role; the workflow can generate
outreach briefs, but human relationship-building is the only effective execution path.

---

## Current Process Flow (As-Is)

The workflow begins when a new site is onboarded. The human SEO manager provides the site
URL, tool access credentials, business goal, ICP definition, and brand voice guide. This
triggers Phase 0: a 7-stream parallel audit covering Crawl, Technical, On-Page, Content,
Authority, Competitive, and Analytics dimensions.

Approximately 65% of audit steps are fully automated (AI agents querying APIs and
structured data sources). The remaining 35% are hybrid — the AI agent produces a result
that a human must review (toxic link assessments, content quality scoring, competitor
identification). All audit streams feed into a Synthesis Agent (Claude API) that produces
a unified findings report with priority scores.

The human SEO manager then reviews the synthesis report and adjusts the AI-suggested
priority ordering before Gate 1: the formal approval of the audit plan. Rejection returns
to backlog prioritization; approval dispatches the SEO Orchestrator.

The Orchestrator fans out two parallel workstreams. Track A (Technical Remediation) runs
immediately: agents push schema and sitemap fixes, optimise images, correct meta tags, and
handle canonicals, robots.txt, and redirects. Track B (Content Generation) waits for Gate
2. Meanwhile, the Research phase runs: keyword data, SERP analysis, trend detection, and
intent classification are all automated; only SME interviews are manual. Research output
feeds the Strategy phase — topic cluster building and content calendar generation are AI
tasks, but the editorial angle and POV are defined by the human manager.

Gate 2 approves the strategy and calendar. Track B then begins: a Brief Agent and Outline
Agent prepare the writer's workspace, the human writer produces the content (with AI
co-pilot assistance), an Editor Agent and Fact-Check Agent review the draft, and then AI
agents apply meta tags, schema markup, and alt text automatically.

Both tracks converge at AI Quality Checks (schema, voice, plagiarism) and then Gate 3
(Human Final Read). A pass at Gate 3 routes to Gate 4 (publish timing confirmation) and
then publication: CMS push, internal linking, index ping, and social/email distribution
drafts are all automated. Human posts social/email manually.

Publication fires the `content_published` event, which simultaneously triggers the
Baseline Snapshot Agent (T-zero capture) and the Continuous Monitor (begins ongoing
site-wide tracking).

---

## Aftercare System

The aftercare system is the most distinctive section of the workflow. Three timed
checkpoints — Day 7, Day 30, and Day 90 — each run a targeted set of checks and compare
results against the T-zero baseline (the Then & Now layer).

**Day 7** focuses on technical health: was the page indexed? Are there crawl errors? Do
rich results appear? Early CTR and impression data from GSC are collected. A triage engine
attempts auto-fixes for known error types; unfixable issues are flagged in the Aftercare
Dashboard.

**Day 30** focuses on trajectory: is rank moving in the right direction? Is traffic on
track against the forecast? Are any cannibalization issues emerging? Backlink acquisition
is tracked. SERP feature capture records whether the page appears in Featured Snippets,
People Also Ask, or other rich features.

**Day 90** is the maturity assessment: full performance pull, conversion attribution,
topical authority lift measurement, competitor move detection, ROI calculation, and a
human strategic review. The classification engine then routes the page to one of four
outcome states:

- **Winner:** Triggers the Repurpose Pipeline — spin-offs, FAQ extensions, cluster
  expansion, outreach briefs, and internal link retrofitting.
- **Steady:** Tracked in Continuous Monitor. No immediate action.
- **Underperformer:** Triggers the Refresh Pipeline — gap diagnosis, SERP re-analysis,
  an updated brief, and a human rewrite decision. Resets the aftercare clock.
- **Loser:** Routes to deprecation — 301 redirect, content merge, or noindex application.

The Monthly Aftercare Digest aggregates Day 30 and Day 90 signals across all active pages
and routes strategic adjustment recommendations back to the SEO Orchestrator.

---

## Pain Points & Design Risks

Since the system is not yet built, the pain points are architectural risks rather than
operational frustrations:

1. **No persistence layer:** Pipeline state will be lost between agent runs without a
   database. Supabase solves this with a PostgreSQL backend and built-in Realtime.

2. **No real-time feedback mechanism:** The UI cannot show live agent progress without
   a pub/sub layer. Supabase Realtime subscriptions allow the Pipeline View to update
   as each agent writes its status to the jobs table.

3. **Undefined gate data contracts:** The Gate Review UI must display AI output in a
   structured, reviewable format. Output schemas must be defined for each gate before
   the UI can be built.

4. **Aftercare scheduling:** The Day 7/30/90 cadence requires a scheduler. Celery beat
   tasks are recommended, triggered by the publish event and persisted in Supabase.

5. **Content editor co-pilot integration:** The AI brief and outline must be
   API-accessible within the TipTap editor. This requires a custom TipTap extension
   and a streaming Claude API endpoint.

6. **Concurrent pipeline isolation:** Running multiple site pipelines simultaneously
   requires careful job isolation in the FastAPI task queue and per-job Supabase
   Realtime channels.

---

## Future-State Design (To-Be)

The to-be state adds a Next.js application as the control and visibility layer over the
existing workflow logic. No steps are removed or replaced — the UI wraps everything.

### Pipeline View
An interactive React Flow diagram showing all active workflow jobs as a live node graph.
Each phase node displays its current status (queued, running, awaiting_human, complete,
failed) via Supabase Realtime subscriptions. Gate nodes pulse amber when human action is
required. Clicking any node opens a detail panel showing agent logs, timing, and output
previews.

### Gate Review Screen
A full-screen UI surfaced for each of the four approval gates:
- **Gate 1 (Audit Plan):** Displays the synthesis report with drag-and-drop priority
  reordering. Approve or reject with a mandatory comment on rejection.
- **Gate 2 (Strategy & Calendar):** Shows the content calendar in a visual timeline view.
  Approve or request revisions.
- **Gate 3 (Human Final Read):** Side-by-side view — content preview on the left, QA
  report with flagged issues on the right. Approve or return with annotations.
- **Gate 4 (Publish):** One-click publish confirmation with scheduled publish time option.

### Content Editor
A three-panel workspace:
- **Left panel:** Brief, AI-generated outline, research snippets, and keyword targets —
  all read-only reference material for the writer.
- **Centre panel:** TipTap rich text editor. Auto-saves to Supabase on every change.
  Word count, readability score, and target keyword density shown in the toolbar.
- **Right panel:** AI co-pilot chat (Claude API streaming). Writer can ask for
  suggestions, rewrites, section expansions, or style checks. Co-pilot responses appear
  inline as suggestions — writer accepts or rejects each one.

### Aftercare Dashboard
A per-page performance dashboard with three tabbed views (Day 7, Day 30, Day 90).
Each tab shows:
- Metrics vs baseline (Then & Now delta — rank change, traffic change, CTR change)
- Traffic vs forecast chart (Recharts line chart)
- Outcome classification badge (Winner / Steady / Underperformer / Loser)
- Action recommendations from the classification engine

A site-wide filter and a monthly digest view aggregate all pages with a summary of
outcome distribution and strategic recommendations.

---

## Tool Recommendations

| Layer | Tool | Rationale |
|---|---|---|
| Frontend | Next.js 14 App Router | Server components for data-heavy views; client components for interactive UI |
| Pipeline diagram | React Flow | Purpose-built for interactive node graphs with live status overlays |
| Rich text editor | TipTap | Extensible, headless — ideal for AI co-pilot extension |
| Charts | Recharts / Tremor | React-native, covers all aftercare metric visualisations |
| Backend | FastAPI (Python) | Natural fit for AI agent orchestration; async; clean REST + WebSocket API |
| Database | Supabase | PostgreSQL + Realtime; eliminates separate Redis for pub/sub |
| Task queue | Celery + Redis | Long-running aftercare jobs; FastAPI BackgroundTasks for short ones |
| LLM | Claude API (claude-sonnet-4-6) | Primary LLM for synthesis, intent, co-pilot, ROI narrative |
| SEO data | DataForSEO | Keyword data, SERP, rank tracking — single API for most data needs |
| Backlinks | Ahrefs API | Authority and backlink profile data |
| Google data | GSC API + GA4 API | Primary performance data source |

---

## Implementation Roadmap Summary

See `implementation.md` for full phased plan.

**Sprint 0 (Week 1-2):** Project scaffolding, Supabase schema, FastAPI boilerplate,
Next.js app setup, auth, base Pipeline View shell.

**Sprint 1 (Week 2-4):** Phase 0 Audit agents + Synthesis agent + Gate 1 UI.

**Sprint 2 (Week 4-6):** Research + Strategy agents + Gate 2 UI + Track A Tech Fix agents.

**Sprint 3 (Week 6-9):** Track B Content pipeline + TipTap Content Editor + Gate 3 UI.

**Sprint 4 (Week 9-11):** Publish agents + Gate 4 UI + Baseline Snapshot agent.

**Sprint 5 (Week 11-14):** Aftercare agents (Day 7/30/90) + Aftercare Dashboard.

**Sprint 6 (Week 14-15):** Continuous Monitor + anomaly alerting + Pipeline View polish.

**Sprint 7 (Week 15-16):** End-to-end testing, performance tuning, documentation.
