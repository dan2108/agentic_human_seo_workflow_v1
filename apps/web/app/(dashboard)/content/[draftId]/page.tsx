import { notFound } from "next/navigation";
import ContentEditor from "@/components/editor/ContentEditor";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
const NEXT_PUBLIC_API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface DraftResponse {
  id: string;
  job_id: string;
  status: string;
  body: string;
  brief: Record<string, unknown>;
  outline: Record<string, unknown>;
  updated_at: string;
}

interface Props { params: Promise<{ draftId: string }> }

export default async function ContentPage({ params }: Props) {
  const { draftId } = await params;

  const res = await fetch(`${API_URL}/content/${draftId}`, { cache: "no-store" });
  if (!res.ok) notFound();
  const draft: DraftResponse = await res.json();

  return (
    <div className="flex flex-col h-full">
      <ContentEditor
        draftId={draftId}
        initialContent={draft.body ?? ""}
        brief={draft.brief ?? {}}
        outline={draft.outline ?? {}}
        apiUrl={NEXT_PUBLIC_API_URL}
      />
    </div>
  );
}
