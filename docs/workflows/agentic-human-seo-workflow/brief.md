# Workflow Brief: Agentic Human SEO Workflow

## Overview
A fully-designed agentic SEO workflow that orchestrates AI agents, hybrid human-AI steps,
and human-led decisions across the complete SEO lifecycle from initial site audit through
content publication and long-term performance monitoring. The workflow does not yet exist
as running software; the Mermaid diagram is the design blueprint.

## Why We Are Documenting This
To produce an engineering specification that a solo developer can use to build a
Next.js + FastAPI web application. The UI replaces CLI-based agent execution with a
visual, interactive interface where the internal SEO team can manage every phase.

## Triggers
- New client or site onboarding (starts Phase 0 Audit)
- Content calendar date reached (starts Track B)
- Monitoring anomaly detected (triggers targeted re-run)
- Quarterly schedule (triggers full re-audit)

## Scope Boundaries

**In scope:**
- All phases in master-agentic-human-workflow.mermaid
- Four UI screens: Pipeline View, Gate Review, Content Editor, Aftercare Dashboard
- FastAPI backend + Supabase persistence layer
- Real-time pipeline status via Supabase Realtime

**Out of scope:**
- External client portal (internal team only)
- Billing / subscription management
- Multi-tenant SaaS features

## Success Criteria
1. Internal team can initiate and monitor a full SEO pipeline run from the browser without CLI
2. All four approval gates surface in Gate Review UI with AI output visible for human decision
3. Content editor provides brief, AI outline, and live editor in one three-panel view
4. Aftercare dashboard shows Day 7 / 30 / 90 metrics with Then & Now delta visualisation
5. The system can run multiple site pipelines concurrently

## Constraints
- Solo developer - architecture must minimise operational complexity
- React / Next.js frontend (decided)
- Backend: FastAPI + Supabase (recommended - see implementation.md)
- No fixed deadline - quality and completeness over speed
