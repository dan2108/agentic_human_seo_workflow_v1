import { notFound } from "next/navigation";
import AuditGate from "@/components/gates/AuditGate";
import StrategyGate from "@/components/gates/StrategyGate";
import ContentGate from "@/components/gates/ContentGate";
import PublishGate from "@/components/gates/PublishGate";
import { api } from "@/lib/api/client";

interface Props { params: Promise<{ gateId: string }> }

type GateData = {
  id: string;
  gate_id: string;
  status: string;
  decision: string | null;
  comment: string | null;
  synthesis: Record<string, unknown>;
};

export default async function GatePage({ params }: Props) {
  const { gateId } = await params;

  let gate: GateData;
  try {
    gate = await api.gates.get(gateId);
  } catch {
    notFound();
  }

  const gateLabels: Record<string, string> = {
    gate1: "Audit Review",
    gate2: "Strategy Review",
    gate3: "Content Review",
    gate4: "Launch Review",
  };

  const gateName = gateId.split(":")[0];
  const jobId = gateId.split(":")[1] ?? "";

  function renderGate() {
    switch (gateName) {
      case "gate2":
        return (
          <StrategyGate
            gateId={gateName}
            jobId={jobId}
            strategy={gate.synthesis ?? {}}
            currentStatus={gate.status}
          />
        );
      case "gate3":
        return (
          <ContentGate
            gateId={gateName}
            jobId={jobId}
            qaData={gate.synthesis ?? {}}
            currentStatus={gate.status}
          />
        );
      case "gate4":
        return (
          <PublishGate
            gateId={gateName}
            jobId={jobId}
            publishData={gate.synthesis ?? {}}
            currentStatus={gate.status}
          />
        );
      default:
        return (
          <AuditGate
            gateId={gateName}
            jobId={jobId}
            synthesis={gate.synthesis ?? {}}
            currentStatus={gate.status}
          />
        );
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-3 border-b border-gray-800 px-6 py-4">
        <a href="/pipeline" className="text-sm text-gray-500 hover:text-gray-300">← Pipeline</a>
        <span className="text-gray-700">/</span>
        <span className="text-sm text-amber-400 font-medium">
          🚦 {gateLabels[gateName] ?? gateId}
        </span>
        <span className={`ml-auto text-xs px-2 py-0.5 rounded-full font-medium ${
          gate.status === "approved" ? "bg-emerald-900 text-emerald-400" :
          gate.status === "rejected" ? "bg-red-900 text-red-400" :
          "bg-amber-900 text-amber-300"
        }`}>
          {gate.status}
        </span>
      </div>
      <div className="flex-1 overflow-auto p-6">
        {renderGate()}
      </div>
    </div>
  );
}
