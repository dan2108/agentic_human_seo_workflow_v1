# Agentic Human SEO Workflow

Full-lifecycle agentic SEO system with Next.js UI, FastAPI agent orchestration, and Supabase real-time persistence.

## Structure

```
apps/web/    Next.js 14 App Router (Pipeline View, Gate Review, Content Editor, Aftercare Dashboard)
apps/api/    FastAPI agent orchestration (audit, research, strategy, content, publish, aftercare)
supabase/    PostgreSQL schema migrations
```

## Quick Start

```bash
cp .env.example .env
docker-compose up -d          # Supabase local + Redis
cd apps/api && uv sync && uv run uvicorn app.main:app --reload
cd apps/web && pnpm install && pnpm dev
```

## Stack
- **Frontend:** Next.js 14, React Flow, TipTap, Recharts, Tailwind CSS
- **Backend:** FastAPI, Celery, Redis, Python 3.12, uv
- **Database:** Supabase (PostgreSQL + Realtime)
- **AI:** Claude API (claude-sonnet-4-6)
- **SEO Data:** DataForSEO, Ahrefs API, GSC API, GA4 API

## Docs
See `docs/workflows/agentic-human-seo-workflow/` for full workflow documentation, implementation plan, and architecture diagrams.
