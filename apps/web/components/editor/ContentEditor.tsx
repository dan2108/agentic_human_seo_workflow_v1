"use client";
// ContentEditor - three-panel workspace: BriefPanel | EditorPanel | CopilotPanel
// TODO: wire TipTap editor with auto-save to Supabase on 2s inactivity
export default function ContentEditor({ draftId }: { draftId: string }) {
  return (
    <div className="grid grid-cols-[320px_1fr_320px] h-screen">
      <div>Brief Panel</div>
      <div>Editor Panel</div>
      <div>Copilot Panel</div>
    </div>
  );
}
