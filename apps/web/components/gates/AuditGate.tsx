"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api/client";

interface SynthesisReport {
  executive_summary?: string;
  critical_issues?: string[];
  high_priority?: string[];
  medium_priority?: string[];
  low_priority?: string[];
  quick_wins?: string[];
}

interface AuditGateProps {
  gateId: string;
  jobId: string;
  synthesis: SynthesisReport;
  currentStatus: string;
}

function PrioritySection({ title, items, color }: { title: string; items: string[]; color: string }) {
  if (!items || items.length === 0) return null;
  return (
    <div className={`rounded-lg border ${color} p-4`}>
      <h3 className="text-sm font-semibold mb-2">{title}</h3>
      <ul className="space-y-1">
        {items.map((item, i) => (
          <li key={i} className="text-sm text-gray-300 flex gap-2">
            <span className="text-gray-500 shrink-0">{i + 1}.</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function AuditGate({ gateId, jobId, synthesis, currentStatus }: AuditGateProps) {
  const router = useRouter();
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState<"approve" | "reject" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isDecided = currentStatus === "approved" || currentStatus === "rejected";
  const fullGateId = jobId ? `${gateId}:${jobId}` : gateId;

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
    <div className="flex flex-col gap-6 max-w-3xl mx-auto">
      {synthesis.executive_summary && (
        <div className="rounded-xl bg-gray-800 border border-gray-700 p-5">
          <h2 className="text-xs font-bold uppercase tracking-wide text-gray-400 mb-2">Executive Summary</h2>
          <p className="text-gray-100 leading-relaxed">{synthesis.executive_summary}</p>
        </div>
      )}

      <PrioritySection title="Critical Issues" items={synthesis.critical_issues ?? []} color="border-red-800 bg-red-950/30" />
      <PrioritySection title="High Priority" items={synthesis.high_priority ?? []} color="border-amber-800 bg-amber-950/30" />
      <PrioritySection title="Quick Wins" items={synthesis.quick_wins ?? []} color="border-emerald-800 bg-emerald-950/30" />
      <PrioritySection title="Medium Priority" items={synthesis.medium_priority ?? []} color="border-blue-800 bg-blue-950/30" />
      <PrioritySection title="Low Priority" items={synthesis.low_priority ?? []} color="border-gray-700 bg-gray-900" />

      {!isDecided && (
        <div className="rounded-xl border border-gray-700 bg-gray-900 p-5 space-y-4">
          <h2 className="text-sm font-semibold text-gray-200">Gate {gateId.replace("gate", "")} Decision</h2>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add a note or revision request (optional)..."
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
              {submitting === "approve" ? "Approving…" : "✓ Approve — proceed to next phase"}
            </button>
            <button
              onClick={() => handleDecision("reject")}
              disabled={submitting !== null}
              className="rounded-lg border border-red-700 px-4 py-2 text-sm font-medium text-red-400 hover:bg-red-950/30 disabled:opacity-50 transition-colors"
            >
              {submitting === "reject" ? "Rejecting…" : "✗ Reject"}
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
          {currentStatus === "approved" ? "✓ Gate Approved" : "✗ Gate Rejected"}
        </div>
      )}
    </div>
  );
}
