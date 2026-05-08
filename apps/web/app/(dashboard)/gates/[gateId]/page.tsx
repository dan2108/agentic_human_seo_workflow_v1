import { notFound } from "next/navigation";
import AuditGate from "@/components/gates/AuditGate";
import { api } from "@/lib/api/client";

interface Props { params: Promise<{ gateId: string }> }

export default async function GatePage({ params }: Props) {
  const { gateId } = await params;

  let gate;
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
        <AuditGate
          gateId={gateName}
          jobId={gateId.split(":")[1] ?? ""}
          synthesis={gate.synthesis ?? {}}
          currentStatus={gate.status}
        />
      </div>
    </div>
  );
}
