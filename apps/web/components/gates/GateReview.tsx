// GateReview - base wrapper for all 4 gate review screens
export default function GateReview({ children }: { children: React.ReactNode }) {
  return <div className="min-h-screen bg-gray-950 p-8">{children}</div>;
}
