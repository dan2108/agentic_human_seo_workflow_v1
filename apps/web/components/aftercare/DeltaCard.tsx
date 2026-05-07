// DeltaCard - shows metric name, baseline value, current value, and delta arrow
export default function DeltaCard({ metric, baseline, current }: { metric: string; baseline: number; current: number }) {
  const delta = current - baseline;
  return <div>{metric}: {delta > 0 ? "+" : ""}{delta}</div>;
}
