"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api/client";

interface CalendarEntry {
  week: number;
  topic: string;
  keyword: string;
  content_type: "pillar" | "supporting" | "listicle";
  estimated_traffic: number;
}

interface TopicCluster {
  topic: string;
  keywords: string[];
  pillar: boolean;
}

interface StrategyData {
  calendar?: { entries: CalendarEntry[] };
  clusters?: { clusters: TopicCluster[] };
  intent?: { classifications: { keyword: string; intent: string }[] };
}

interface StrategyGateProps {
  gateId: string;
  jobId: string;
  strategy: StrategyData;
  currentStatus: string;
}

const CONTENT_TYPE_COLORS: Record<string, string> = {
  pillar: "bg-purple-900/50 border-purple-700 text-purple-200",
  supporting: "bg-blue-900/50 border-blue-700 text-blue-200",
  listicle: "bg-teal-900/50 border-teal-700 text-teal-200",
};

function CalendarTimeline({ entries }: { entries: CalendarEntry[] }) {
  const sorted = [...entries].sort((a, b) => a.week - b.week);
  const weeks = Array.from(new Set(sorted.map((e) => e.week)));

  return (
    <div className="space-y-3">
      <h2 className="text-xs font-bold uppercase tracking-wide text-gray-400">Content Calendar</h2>
      <div className="grid grid-cols-1 gap-2">
        {weeks.map((week) => {
          const weekEntries = sorted.filter((e) => e.week === week);
          return (
            <div key={week} className="flex gap-3 items-start">
              <div className="w-14 shrink-0 text-right">
                <span className="text-xs font-mono text-gray-500">Wk {week}</span>
              </div>
              <div className="flex-1 flex flex-wrap gap-2">
                {weekEntries.map((entry, i) => (
                  <div
                    key={i}
                    className={`rounded-lg border px-3 py-2 text-xs ${CONTENT_TYPE_COLORS[entry.content_type] ?? "bg-gray-800 border-gray-700 text-gray-200"}`}
                  >
                    <div className="font-medium">{entry.topic}</div>
                    <div className="text-gray-400 mt-0.5">{entry.keyword}</div>
                    <div className="text-gray-500 mt-0.5">~{entry.estimated_traffic.toLocaleString()} visits</div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ClusterMap({ clusters }: { clusters: TopicCluster[] }) {
  if (!clusters.length) return null;
  return (
    <div className="space-y-3">
      <h2 className="text-xs font-bold uppercase tracking-wide text-gray-400">Topic Clusters</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {clusters.map((cluster, i) => (
          <div key={i} className="rounded-lg border border-gray-700 bg-gray-800 p-3">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-semibold text-sm text-gray-100">{cluster.topic}</span>
              {cluster.pillar && (
                <span className="text-xs bg-purple-800 text-purple-200 rounded px-1.5 py-0.5">Pillar</span>
              )}
            </div>
            <div className="flex flex-wrap gap-1">
              {cluster.keywords.map((kw, j) => (
                <span key={j} className="text-xs bg-gray-700 text-gray-300 rounded px-1.5 py-0.5">{kw}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function StrategyGate({ gateId, jobId, strategy, currentStatus }: StrategyGateProps) {
  const router = useRouter();
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState<"approve" | "reject" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isDecided = currentStatus === "approved" || currentStatus === "rejected";
  const fullGateId = jobId ? `${gateId}:${jobId}` : gateId;

  const entries = strategy.calendar?.entries ?? [];
  const clusters = strategy.clusters?.clusters ?? [];

  async function handleDecision(action: "approve" | "reject") {
    setSubmitting(action);
    setError(null);
    try {
      if (action === "approve") {
        await api.gates.approve(fullGateId, comment || undefined);
      } else {
        await api.gates.reject(fullGateId, comment || undefined);
      }
      router.push("/pipeline");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit decision");
    } finally {
      setSubmitting(null);
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      {clusters.length > 0 && <ClusterMap clusters={clusters} />}

      {entries.length > 0 ? (
        <div className="rounded-xl border border-gray-700 bg-gray-900 p-5">
          <CalendarTimeline entries={entries} />
        </div>
      ) : (
        <div className="rounded-xl border border-gray-700 bg-gray-900 p-5 text-center text-gray-500 text-sm">
          No calendar entries generated yet.
        </div>
      )}

      {!isDecided && (
        <div className="rounded-xl border border-gray-700 bg-gray-900 p-5 space-y-4">
          <h2 className="text-sm font-semibold text-gray-200">Gate 2 — Strategy Approval</h2>
          <p className="text-xs text-gray-400">
            Review the topic clusters and content calendar above. Approve to begin Track A technical
            fixes and content creation, or reject to revise the research phase.
          </p>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add a revision note (optional)..."
            rows={3}
            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-blue-500 focus:outline-none resize-none"
          />
          {error && <p className="text-sm text-red-400 bg-red-950/30 rounded px-3 py-2">{error}</p>}
          <div className="flex gap-3">
            <button
              onClick={() => handleDecision("approve")}
              disabled={submitting !== null}
              className="flex-1 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50 transition-colors"
            >
              {submitting === "approve" ? "Approving…" : "✓ Approve — begin Track A + Content"}
            </button>
            <button
              onClick={() => handleDecision("reject")}
              disabled={submitting !== null}
              className="rounded-lg border border-red-700 px-4 py-2 text-sm font-medium text-red-400 hover:bg-red-950/30 disabled:opacity-50 transition-colors"
            >
              {submitting === "reject" ? "Rejecting…" : "✗ Revise"}
            </button>
          </div>
        </div>
      )}

      {isDecided && (
        <div className={`rounded-lg border p-4 text-center ${
          currentStatus === "approved"
            ? "border-emerald-700 bg-emerald-950/30 text-emerald-400"
            : "border-red-700 bg-red-950/30 text-red-400"
        }`}>
          {currentStatus === "approved" ? "✓ Strategy Approved" : "✗ Strategy Rejected — revise research"}
        </div>
      )}
    </div>
  );
}
