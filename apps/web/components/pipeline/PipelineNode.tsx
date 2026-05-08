"use client";
import { memo } from "react";
import { Handle, Position } from "reactflow";
import StatusBadge, { type NodeStatus } from "./StatusBadge";

interface PipelineNodeData {
  label: string;
  subtitle?: string;
  status: NodeStatus;
  automationType?: "ai" | "human" | "hybrid";
}

const automationIcon: Record<string, string> = {
  ai: "🤖",
  human: "👤",
  hybrid: "🤝",
};

function PipelineNode({ data }: { data: PipelineNodeData }) {
  const borderColor =
    data.status === "running" ? "border-blue-500" :
    data.status === "complete" ? "border-emerald-500" :
    data.status === "failed" ? "border-red-500" :
    "border-gray-700";

  return (
    <div className={`min-w-[200px] rounded-xl border-2 bg-gray-900 px-4 py-3 shadow-lg ${borderColor}`}>
      <Handle type="target" position={Position.Top} className="!bg-gray-600" />
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-gray-100">{data.label}</p>
          {data.subtitle && (
            <p className="mt-0.5 text-xs text-gray-400">{data.subtitle}</p>
          )}
        </div>
        {data.automationType && (
          <span className="text-lg" title={data.automationType}>
            {automationIcon[data.automationType]}
          </span>
        )}
      </div>
      <div className="mt-2">
        <StatusBadge status={data.status} />
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-gray-600" />
    </div>
  );
}

export default memo(PipelineNode);
