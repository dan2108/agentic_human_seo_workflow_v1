"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api/client";

interface LinkSuggestion {
  anchor: string;
  url: string;
  context?: string;
}

interface PublishResult {
  published_url?: string;
  status?: string;
}

interface LinkingData {
  suggestions?: LinkSuggestion[];
  count?: number;
}

interface DistributionData {
  linkedin?: string;
  twitter?: string;
  email?: string;
}

interface PublishData {
  publish_result?: PublishResult;
  linking?: LinkingData;
  distribution?: DistributionData;
}

interface PublishGateProps {
  gateId: string;
  jobId: string;
  publishData: PublishData;
  currentStatus: string;
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  function handleCopy() {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }
  return (
    <button
      onClick={handleCopy}
      className="text-xs text-gray-400 hover:text-gray-200 transition-colors"
    >
      {copied ? "✓ Copied" : "Copy"}
    </button>
  );
}

export default function PublishGate({ gateId, jobId, publishData, currentStatus }: PublishGateProps) {
  const router = useRouter();
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState<"approve" | "reject" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isDecided = currentStatus === "approved" || currentStatus === "rejected";
  const fullGateId = jobId ? `${gateId}:${jobId}` : gateId;

  const result = publishData.publish_result;
  const linking = publishData.linking;
  const dist = publishData.distribution;

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
    <div className="max-w-4xl mx-auto space-y-5">

      {/* Published URL */}
      {result?.published_url && (
        <div className="rounded-xl border border-gray-700 bg-gray-900 p-5">
          <h2 className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-3">Published Page</h2>
          <div className="flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-emerald-400 flex-shrink-0" />
            <a
              href={result.published_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 text-sm font-mono truncate flex-1"
            >
              {result.published_url}
            </a>
            <CopyButton text={result.published_url} />
          </div>
        </div>
      )}

      {/* Internal Linking */}
      {linking?.suggestions && linking.suggestions.length > 0 && (
        <div className="rounded-xl border border-gray-700 bg-gray-900 p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-bold uppercase tracking-wide text-gray-500">Internal Link Suggestions</h2>
            <span className="text-xs text-gray-500">{linking.count ?? linking.suggestions.length} links</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left text-gray-500 font-medium py-1.5 pr-4">Anchor Text</th>
                  <th className="text-left text-gray-500 font-medium py-1.5 pr-4">URL</th>
                  <th className="text-left text-gray-500 font-medium py-1.5">Context</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {linking.suggestions.map((s, i) => (
                  <tr key={i}>
                    <td className="py-2 pr-4 text-blue-400 font-medium">{s.anchor}</td>
                    <td className="py-2 pr-4 text-gray-400 font-mono truncate max-w-[200px]">{s.url}</td>
                    <td className="py-2 text-gray-500 italic">{s.context ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Distribution Copy */}
      {dist && (dist.linkedin || dist.twitter || dist.email) && (
        <div className="rounded-xl border border-gray-700 bg-gray-900 p-5">
          <h2 className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-4">Distribution Copy</h2>
          <div className="space-y-4">
            {dist.linkedin && (
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-medium text-blue-400">LinkedIn</span>
                  <CopyButton text={dist.linkedin} />
                </div>
                <p className="text-xs text-gray-300 bg-gray-800 rounded-lg p-3 whitespace-pre-wrap leading-relaxed">
                  {dist.linkedin}
                </p>
              </div>
            )}
            {dist.twitter && (
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-medium text-sky-400">Twitter / X</span>
                  <CopyButton text={dist.twitter} />
                </div>
                <p className="text-xs text-gray-300 bg-gray-800 rounded-lg p-3 whitespace-pre-wrap leading-relaxed">
                  {dist.twitter}
                </p>
              </div>
            )}
            {dist.email && (
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-medium text-amber-400">Email Newsletter</span>
                  <CopyButton text={dist.email} />
                </div>
                <p className="text-xs text-gray-300 bg-gray-800 rounded-lg p-3 whitespace-pre-wrap leading-relaxed">
                  {dist.email}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Approve / Reject */}
      {!isDecided && (
        <div className="rounded-xl border border-gray-700 bg-gray-900 p-5 space-y-3">
          <h2 className="text-sm font-semibold text-gray-200">Gate 4 — Launch Approval</h2>
          <p className="text-xs text-gray-400">
            Confirm the published page is live, linking suggestions are accepted, and distribution copy is ready to post.
          </p>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add a note (optional)..."
            rows={2}
            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-blue-500 focus:outline-none resize-none"
          />
          {error && (
            <p className="text-sm text-red-400 bg-red-950/30 rounded px-3 py-2">{error}</p>
          )}
          <div className="flex gap-2">
            <button
              onClick={() => handleDecision("approve")}
              disabled={submitting !== null}
              className="flex-1 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50 transition-colors"
            >
              {submitting === "approve" ? "Approving…" : "✓ Confirm Launch"}
            </button>
            <button
              onClick={() => handleDecision("reject")}
              disabled={submitting !== null}
              className="rounded-lg border border-red-700 px-4 py-2 text-sm font-medium text-red-400 hover:bg-red-950/30 disabled:opacity-50 transition-colors"
            >
              {submitting === "reject" ? "…" : "✗ Rollback"}
            </button>
          </div>
        </div>
      )}

      {isDecided && (
        <div className={`rounded-lg border p-4 text-center text-sm font-medium ${
          currentStatus === "approved"
            ? "border-emerald-700 bg-emerald-950/30 text-emerald-400"
            : "border-red-700 bg-red-950/30 text-red-400"
        }`}>
          {currentStatus === "approved" ? "✓ Launch Confirmed — aftercare scheduled" : "✗ Launch Rolled Back"}
        </div>
      )}
    </div>
  );
}
