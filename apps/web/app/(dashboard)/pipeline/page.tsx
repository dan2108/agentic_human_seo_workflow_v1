import PipelineCanvas from "@/components/pipeline/PipelineCanvas";

export default function PipelinePage() {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-gray-800 px-6 py-4">
        <div>
          <h1 className="text-lg font-semibold text-gray-100">Pipeline</h1>
          <p className="text-sm text-gray-400">Live workflow status across all active jobs</p>
        </div>
        <a
          href="/pipeline/new"
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          + New Job
        </a>
      </div>
      <div className="flex-1">
        <PipelineCanvas />
      </div>
    </div>
  );
}
