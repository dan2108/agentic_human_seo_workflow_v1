// OutcomeBadge - Winner | Steady | Underperformer | Loser with colour coding
type Outcome = "winner" | "steady" | "underperformer" | "loser";
export default function OutcomeBadge({ outcome }: { outcome: Outcome }) {
  return <span>{outcome}</span>;
}
