// GateNode - approval gate node; pulses amber when awaiting_human
export default function GateNode({ label, gateId, status }: { label: string; gateId: string; status: string }) {
  return <div>{label}</div>;
}
