"use client";

import { use } from "react";
import { usePipelineStatus } from "@/lib/hooks/usePipelineStatus";
import PipelineCanvas from "@/components/pipeline/PipelineCanvas";

export default function PipelineJobPage({ params }: { params: Promise<{ jobId: string }> }) {
  const { jobId } = use(params);
  const stepStatuses = usePipelineStatus(jobId);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-3 border-b border-gray-800 px-6 py-4">
        <a href="/pipeline" className="text-sm text-gray-500 hover:text-gray-300">← Pipeline</a>
        <span className="text-gray-700">/</span>
        <h1 className="text-sm font-medium text-gray-200 font-mono">{jobId}</h1>
        <span className="ml-auto text-xs text-gray-500">Live</span>
        <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
      </div>
      <div className="flex-1">
        <PipelineCanvas jobId={jobId} stepStatuses={stepStatuses} />
      </div>
    </div>
  );
}
