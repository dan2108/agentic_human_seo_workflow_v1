// PipelineNode - individual step node in the React Flow graph
// status: queued | running | awaiting_human | complete | failed
export type NodeStatus = "queued" | "running" | "awaiting_human" | "complete" | "failed";
export default function PipelineNode({ label, status }: { label: string; status: NodeStatus }) {
  return <div>{label}</div>;
}
