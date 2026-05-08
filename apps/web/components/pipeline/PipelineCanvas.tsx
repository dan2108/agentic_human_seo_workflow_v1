"use client";

import { useCallback, useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  BackgroundVariant,
  type Node,
  type Edge,
} from "reactflow";
import "reactflow/dist/style.css";
import PipelineNode from "./PipelineNode";
import GateNode from "./GateNode";
import { type NodeStatus } from "./StatusBadge";

const nodeTypes = {
  pipeline: PipelineNode,
  gate: GateNode,
};

function buildNodes(stepStatuses: Record<string, string> = {}): Node[] {
  const s = (id: string): NodeStatus =>
    (stepStatuses[id] as NodeStatus) ?? "queued";

  const cx = 280;
  const rowH = 130;
  const y = (row: number) => row * rowH;

  return [
    {
      id: "pre-check",
      type: "pipeline",
      position: { x: cx, y: y(0) },
      data: { label: "Pre-check", subtitle: "URL · robots.txt · redirects", status: s("pre-check"), automationType: "ai" },
    },
    {
      id: "site-audit",
      type: "pipeline",
      position: { x: cx, y: y(1) },
      data: { label: "Site Audit", subtitle: "Crawl · CWV · schema", status: s("site-audit"), automationType: "ai" },
    },
    {
      id: "gate-1",
      type: "gate",
      position: { x: cx + 10, y: y(2) },
      data: { label: "Audit Approval", gateId: "gate-1", status: s("gate-1") || "pending" },
    },
    {
      id: "keyword-research",
      type: "pipeline",
      position: { x: cx, y: y(3) },
      data: { label: "Keyword Research", subtitle: "Clustering · intent · gaps", status: s("keyword-research"), automationType: "ai" },
    },
    {
      id: "strategy",
      type: "pipeline",
      position: { x: cx, y: y(4) },
      data: { label: "Strategy Synthesis", subtitle: "ROI narrative · priorities", status: s("strategy"), automationType: "hybrid" },
    },
    {
      id: "gate-2",
      type: "gate",
      position: { x: cx + 10, y: y(5) },
      data: { label: "Strategy Approval", gateId: "gate-2", status: s("gate-2") || "pending" },
    },
    {
      id: "content-brief",
      type: "pipeline",
      position: { x: cx, y: y(6) },
      data: { label: "Content Briefing", subtitle: "Structure · angle · KW targeting", status: s("content-brief"), automationType: "ai" },
    },
    {
      id: "content-write",
      type: "pipeline",
      position: { x: cx, y: y(7) },
      data: { label: "Content Writing", subtitle: "Draft → edit → polish", status: s("content-write"), automationType: "human" },
    },
    {
      id: "gate-3",
      type: "gate",
      position: { x: cx + 10, y: y(8) },
      data: { label: "Content Approval", gateId: "gate-3", status: s("gate-3") || "pending" },
    },
    {
      id: "publish",
      type: "pipeline",
      position: { x: cx, y: y(9) },
      data: { label: "Publishing", subtitle: "CMS push · sitemap · links", status: s("publish"), automationType: "ai" },
    },
    {
      id: "gate-4",
      type: "gate",
      position: { x: cx + 10, y: y(10) },
      data: { label: "Launch Approval", gateId: "gate-4", status: s("gate-4") || "pending" },
    },
    {
      id: "aftercare",
      type: "pipeline",
      position: { x: cx, y: y(11) },
      data: { label: "Aftercare", subtitle: "Day 7 · 30 · 90 checks", status: s("aftercare"), automationType: "hybrid" },
    },
    {
      id: "monitor",
      type: "pipeline",
      position: { x: cx, y: y(12) },
      data: { label: "Monitor", subtitle: "Continuous rank tracking", status: s("monitor"), automationType: "ai" },
    },
  ];
}

const staticEdges: Edge[] = [
  { id: "e1", source: "pre-check", target: "site-audit", animated: false },
  { id: "e2", source: "site-audit", target: "gate-1", animated: false },
  { id: "e3", source: "gate-1", target: "keyword-research", animated: false },
  { id: "e4", source: "keyword-research", target: "strategy", animated: false },
  { id: "e5", source: "strategy", target: "gate-2", animated: false },
  { id: "e6", source: "gate-2", target: "content-brief", animated: false },
  { id: "e7", source: "content-brief", target: "content-write", animated: false },
  { id: "e8", source: "content-write", target: "gate-3", animated: false },
  { id: "e9", source: "gate-3", target: "publish", animated: false },
  { id: "e10", source: "publish", target: "gate-4", animated: false },
  { id: "e11", source: "gate-4", target: "aftercare", animated: false },
  { id: "e12", source: "aftercare", target: "monitor", animated: false },
];

interface PipelineCanvasProps {
  jobId?: string;
  stepStatuses?: Record<string, string>;
}

export default function PipelineCanvas({ jobId: _jobId, stepStatuses = {} }: PipelineCanvasProps) {
  const nodes = useMemo(() => buildNodes(stepStatuses), [stepStatuses]);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    console.log("node clicked:", node.id);
  }, []);

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={staticEdges}
        nodeTypes={nodeTypes}
        onNodeClick={onNodeClick}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        className="bg-gray-950"
        defaultEdgeOptions={{
          style: { stroke: "#4b5563", strokeWidth: 2 },
        }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="#374151"
        />
        <Controls className="!bg-gray-800 !border-gray-700 !text-gray-300" />
        <MiniMap
          className="!bg-gray-900 !border-gray-700"
          nodeColor={(node) => {
            const status = node.data?.status;
            if (status === "complete") return "#10b981";
            if (status === "running") return "#3b82f6";
            if (status === "awaiting_human" || status === "approved") return "#f59e0b";
            if (status === "failed") return "#ef4444";
            return "#374151";
          }}
        />
      </ReactFlow>
    </div>
  );
}
