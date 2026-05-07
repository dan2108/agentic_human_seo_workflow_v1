// Gate Review - approve or reject AI output at each of the 4 gates
// TODO: load gate data by gateId, render appropriate gate component
export default function GateReviewPage({ params }: { params: { gateId: string } }) {
  return <div>Gate {params.gateId}</div>;
}
