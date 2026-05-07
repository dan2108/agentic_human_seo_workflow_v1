// Shared TypeScript types for the SEO Workflow application

export type JobStatus = "queued" | "running" | "awaiting_human" | "complete" | "failed";
export type GateStatus = "pending" | "approved" | "rejected";
export type Outcome = "winner" | "steady" | "underperformer" | "loser";
export type Checkpoint = "day7" | "day30" | "day90";

export interface Job {
  id: string;
  site_url: string;
  status: JobStatus;
  created_at: string;
  updated_at: string;
}

export interface JobStep {
  id: string;
  job_id: string;
  step_id: string;
  status: JobStatus;
  started_at: string | null;
  completed_at: string | null;
  output_json: Record<string, unknown> | null;
}

export interface Gate {
  id: string;
  job_id: string;
  gate_id: "gate1" | "gate2" | "gate3" | "gate4";
  status: GateStatus;
  reviewer_id: string | null;
  decision: "approved" | "rejected" | null;
  comment: string | null;
  decided_at: string | null;
}

export interface ContentDraft {
  id: string;
  job_id: string;
  brief_json: Record<string, unknown>;
  outline_json: Record<string, unknown>;
  body: string;
  status: "draft" | "qa_pending" | "approved" | "published";
  created_at: string;
  updated_at: string;
}

export interface AftercareReport {
  id: string;
  job_id: string;
  checkpoint: Checkpoint;
  data_json: Record<string, unknown>;
  created_at: string;
}

export interface BaselineSnapshot {
  id: string;
  job_id: string;
  url: string;
  metrics_json: {
    rank: number;
    impressions: number;
    clicks: number;
    ctr: number;
    position: number;
  };
  captured_at: string;
}
