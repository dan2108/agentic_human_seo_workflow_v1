// Content Editor - three-panel TipTap workspace with AI co-pilot
// TODO: load draft by draftId, render BriefPanel + EditorPanel + CopilotPanel
export default function EditorPage({ params }: { params: { draftId: string } }) {
  return <div>Editor {params.draftId}</div>;
}
