"use client";
import { memo } from "react";
import { Handle, Position } from "reactflow";
import Link from "next/link";

interface GateNodeData {
  label: string;
  gateId: string;
  status: "pending" | "awaiting_human" | "approved" | "rejected";
}

function GateNode({ data }: { data: GateNodeData }) {
  const isWaiting = data.status === "awaiting_human";
  const isApproved = data.status === "approved";
  const isRejected = data.status === "rejected";

  const borderClass = isWaiting
    ? "border-amber-400 shadow-amber-500/30"
    : isApproved
    ? "border-emerald-500"
    : isRejected
    ? "border-red-500"
    : "border-gray-600";

  return (
    <div
      className={`min-w-[180px] rounded-lg border-2 bg-gray-800 px-4 py-3 shadow-lg transition-shadow ${borderClass} ${isWaiting ? "shadow-lg animate-pulse" : ""}`}
    >
      <Handle type="target" position={Position.Top} className="!bg-gray-600" />
      <div className="flex items-center gap-2">
        <span className="text-amber-400 text-lg">🚦</span>
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-amber-300">Gate</p>
          <p className="text-sm font-semibold text-gray-100">{data.label}</p>
        </div>
      </div>
      {isWaiting && (
        <Link
          href={`/gates/${data.gateId}`}
          className="mt-2 block text-center rounded-md bg-amber-500 px-2 py-1 text-xs font-medium text-black hover:bg-amber-400 transition-colors"
        >
          Review now →
        </Link>
      )}
      {isApproved && (
        <p className="mt-1 text-xs text-emerald-400 font-medium">✓ Approved</p>
      )}
      {isRejected && (
        <p className="mt-1 text-xs text-red-400 font-medium">✗ Rejected</p>
      )}
      <Handle type="source" position={Position.Bottom} className="!bg-gray-600" />
    </div>
  );
}

export default memo(GateNode);
