"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api/client";

interface Suggestion {
  type: string;
  text: string;
  severity: "low" | "medium" | "high";
}

interface Claim {
  claim: string;
  verified: boolean;
  source?: string;
}

interface QAData {
  editor_review?: { suggestions: Suggestion[]; score: number };
  fact_check?: { claims: Claim[]; verified: number; issues: number };
  voice_check?: { score: number; feedback: string };
  plagiarism?: { duplicate_count: number; checked_chars: number };
}

interface ContentGateProps {
  gateId: string;
  jobId: string;
  qaData: QAData;
  currentStatus: string;
  contentPreview?: string;
}

const SEVERITY_COLORS: Record<string, string> = {
  high: "border-red-800 bg-red-950/30 text-red-300",
  medium: "border-amber-800 bg-amber-950/30 text-amber-300",
  low: "border-gray-700 bg-gray-800 text-gray-300",
};

function ScoreBadge({ score, label }: { score: number; label: string }) {
  const color = score >= 80 ? "text-emerald-400" : score >= 60 ? "text-amber-400" : "text-red-400";
  return (
    <div className="flex items-center gap-2">
      <span className={`text-2xl font-bold tabular-nums ${color}`}>{score}</span>
      <span className="text-xs text-gray-500">/100 {label}</span>
    </div>
  );
}

export default function ContentGate({ gateId, jobId, qaData, currentStatus, contentPreview }: ContentGateProps) {
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

  const editorData = qaData.editor_review;
  const factData = qaData.fact_check;
  const voiceData = qaData.voice_check;
  const plagData = qaData.plagiarism;

  return (
    <div className="flex gap-6 h-full max-w-6xl mx-auto">
      {contentPreview && (
        <div className="flex-1 min-w-0 rounded-xl border border-gray-700 bg-gray-900 overflow-y-auto p-5">
          <h2 className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-3">Content Preview</h2>
          <div
            className="prose prose-invert prose-sm max-w-none text-gray-300"
            dangerouslySetInnerHTML={{ __html: contentPreview }}
          />
        </div>
      )}

      <div className="w-96 shrink-0 flex flex-col gap-4 overflow-y-auto">
        <div className="rounded-xl border border-gray-700 bg-gray-900 p-4 space-y-3">
          <h2 className="text-xs font-bold uppercase tracking-wide text-gray-500">QA Scores</h2>
          {editorData && <ScoreBadge score={editorData.score} label="Editor Quality" />}
          {voiceData && <ScoreBadge score={voiceData.score} label="Brand Voice" />}
          {plagData && (
            <div className={`text-sm ${plagData.duplicate_count === 0 ? "text-emerald-400" : "text-red-400"}`}>
              {plagData.duplicate_count === 0 ? "✓ No plagiarism detected" : `⚠ ${plagData.duplicate_count} duplicate sources found`}
            </div>
          )}
          {factData && (
            <div className="text-xs text-gray-400">
              Facts: {factData.verified} verified, {factData.issues} issues
            </div>
          )}
        </div>

        {editorData && editorData.suggestions.length > 0 && (
          <div className="rounded-xl border border-gray-700 bg-gray-900 p-4">
            <h3 className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-2">Editor Suggestions</h3>
            <div className="space-y-2">
              {editorData.suggestions.map((s, i) => (
                <div key={i} className={`rounded-lg border px-3 py-2 text-xs ${SEVERITY_COLORS[s.severity] ?? SEVERITY_COLORS.low}`}>
                  <span className="font-medium capitalize">[{s.type}]</span> {s.text}
                </div>
              ))}
            </div>
          </div>
        )}

        {voiceData && (
          <div className="rounded-xl border border-gray-700 bg-gray-900 p-4">
            <h3 className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-2">Voice Feedback</h3>
            <p className="text-xs text-gray-300">{voiceData.feedback}</p>
          </div>
        )}

        {factData && factData.claims.length > 0 && (
          <div className="rounded-xl border border-gray-700 bg-gray-900 p-4">
            <h3 className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-2">Fact Check</h3>
            <div className="space-y-1">
              {factData.claims.map((c, i) => (
                <div key={i} className="text-xs flex gap-2">
                  <span className={c.verified ? "text-emerald-400" : "text-red-400"}>{c.verified ? "✓" : "✗"}</span>
                  <span className="text-gray-300 flex-1">{c.claim}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {!isDecided && (
          <div className="rounded-xl border border-gray-700 bg-gray-900 p-4 space-y-3">
            <h2 className="text-sm font-semibold text-gray-200">Gate 3 — Content Approval</h2>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Add a revision note (optional)..."
              rows={3}
              className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-blue-500 focus:outline-none resize-none"
            />
            {error && <p className="text-sm text-red-400 bg-red-950/30 rounded px-3 py-2">{error}</p>}
            <div className="flex gap-2">
              <button
                onClick={() => handleDecision("approve")}
                disabled={submitting !== null}
                className="flex-1 rounded-lg bg-emerald-600 px-3 py-2 text-xs font-medium text-white hover:bg-emerald-500 disabled:opacity-50 transition-colors"
              >
                {submitting === "approve" ? "Approving…" : "✓ Approve — publish"}
              </button>
              <button
                onClick={() => handleDecision("reject")}
                disabled={submitting !== null}
                className="rounded-lg border border-red-700 px-3 py-2 text-xs font-medium text-red-400 hover:bg-red-950/30 disabled:opacity-50 transition-colors"
              >
                {submitting === "reject" ? "…" : "✗ Revise"}
              </button>
            </div>
          </div>
        )}

        {isDecided && (
          <div className={`rounded-lg border p-4 text-center text-sm ${
            currentStatus === "approved"
              ? "border-emerald-700 bg-emerald-950/30 text-emerald-400"
              : "border-red-700 bg-red-950/30 text-red-400"
          }`}>
            {currentStatus === "approved" ? "✓ Content Approved" : "✗ Content Rejected — revise draft"}
          </div>
        )}
      </div>
    </div>
  );
}
