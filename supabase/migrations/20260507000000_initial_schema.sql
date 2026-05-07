-- Agentic Human SEO Workflow: Initial Schema
create extension if not exists "pgcrypto";

-- JOBS
create table if not exists public.jobs (
  id          uuid primary key default gen_random_uuid(),
  site_url    text not null,
  status      text not null default 'queued'
                check (status in ('queued','running','awaiting_human','complete','failed')),
  created_by  uuid references auth.users(id),
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

-- JOB STEPS
create table if not exists public.job_steps (
  id           uuid primary key default gen_random_uuid(),
  job_id       uuid not null references public.jobs(id) on delete cascade,
  step_id      text not null,
  status       text not null default 'queued'
                 check (status in ('queued','running','awaiting_human','complete','failed')),
  started_at   timestamptz,
  completed_at timestamptz,
  output_json  jsonb,
  unique (job_id, step_id)
);

-- GATES
create table if not exists public.gates (
  id          uuid primary key default gen_random_uuid(),
  job_id      uuid not null references public.jobs(id) on delete cascade,
  gate_id     text not null check (gate_id in ('gate1','gate2','gate3','gate4')),
  status      text not null default 'pending'
                check (status in ('pending','approved','rejected')),
  reviewer_id uuid references auth.users(id),
  decision    text check (decision in ('approved','rejected')),
  comment     text,
  decided_at  timestamptz,
  created_at  timestamptz not null default now(),
  unique (job_id, gate_id)
);

-- CONTENT DRAFTS
create table if not exists public.content_drafts (
  id           uuid primary key default gen_random_uuid(),
  job_id       uuid not null references public.jobs(id) on delete cascade,
  brief_json   jsonb not null default '{}',
  outline_json jsonb not null default '{}',
  body         text not null default '',
  status       text not null default 'draft'
                 check (status in ('draft','qa_pending','approved','published')),
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

-- AUDIT RESULTS
create table if not exists public.audit_results (
  id         uuid primary key default gen_random_uuid(),
  job_id     uuid not null references public.jobs(id) on delete cascade,
  stream     text not null,
  data_json  jsonb not null default '{}',
  created_at timestamptz not null default now(),
  unique (job_id, stream)
);

-- BASELINE SNAPSHOTS
create table if not exists public.baseline_snapshots (
  id           uuid primary key default gen_random_uuid(),
  job_id       uuid not null references public.jobs(id) on delete cascade,
  url          text not null,
  metrics_json jsonb not null default '{}',
  captured_at  timestamptz not null default now()
);

-- AFTERCARE REPORTS
create table if not exists public.aftercare_reports (
  id           uuid primary key default gen_random_uuid(),
  job_id       uuid not null references public.jobs(id) on delete cascade,
  checkpoint   text not null check (checkpoint in ('day7','day30','day90')),
  data_json    jsonb not null default '{}',
  created_at   timestamptz not null default now(),
  unique (job_id, checkpoint)
);

-- CONTENT OUTCOMES
create table if not exists public.content_outcomes (
  id            uuid primary key default gen_random_uuid(),
  job_id        uuid not null references public.jobs(id) on delete cascade,
  outcome       text not null check (outcome in ('winner','steady','underperformer','loser')),
  classified_at timestamptz not null default now(),
  unique (job_id)
);

-- MONITOR ALERTS
create table if not exists public.monitor_alerts (
  id          uuid primary key default gen_random_uuid(),
  site_url    text not null,
  alert_type  text not null,
  severity    text not null check (severity in ('info','warning','critical')),
  data_json   jsonb not null default '{}',
  resolved    boolean not null default false,
  created_at  timestamptz not null default now()
);

-- UPDATED_AT TRIGGER
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end;
$$;

create trigger jobs_updated_at before update on public.jobs
  for each row execute procedure public.set_updated_at();
create trigger drafts_updated_at before update on public.content_drafts
  for each row execute procedure public.set_updated_at();

-- ROW LEVEL SECURITY
alter table public.jobs enable row level security;
alter table public.job_steps enable row level security;
alter table public.gates enable row level security;
alter table public.content_drafts enable row level security;
alter table public.audit_results enable row level security;
alter table public.baseline_snapshots enable row level security;
alter table public.aftercare_reports enable row level security;
alter table public.content_outcomes enable row level security;
alter table public.monitor_alerts enable row level security;

create policy "users manage own jobs" on public.jobs for all using (auth.uid() = created_by);
create policy "users read own job steps" on public.job_steps for select using (job_id in (select id from public.jobs where created_by = auth.uid()));
create policy "users manage own gates" on public.gates for all using (job_id in (select id from public.jobs where created_by = auth.uid()));
create policy "users manage own drafts" on public.content_drafts for all using (job_id in (select id from public.jobs where created_by = auth.uid()));

-- REALTIME (Pipeline View subscribes to these)
alter publication supabase_realtime add table public.job_steps;
alter publication supabase_realtime add table public.gates;
alter publication supabase_realtime add table public.monitor_alerts;
