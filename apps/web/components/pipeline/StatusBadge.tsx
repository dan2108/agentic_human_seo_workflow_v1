export type NodeStatus = "queued" | "running" | "awaiting_human" | "complete" | "failed" | "skipped";

const styles: Record<NodeStatus, string> = {
  queued: "bg-gray-700 text-gray-300",
  running: "bg-blue-600 text-white animate-pulse",
  awaiting_human: "bg-amber-500 text-black",
  complete: "bg-emerald-600 text-white",
  failed: "bg-red-600 text-white",
  skipped: "bg-gray-600 text-gray-400",
};

export default function StatusBadge({ status }: { status: NodeStatus }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${styles[status]}`}>
      {status.replace("_", " ")}
    </span>
  );
}
