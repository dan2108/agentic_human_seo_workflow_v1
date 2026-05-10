"use client";

import { useState, useCallback } from "react";
import BriefPanel from "@/components/editor/BriefPanel";
import TipTapEditor from "@/components/editor/TipTapEditor";
import CopilotPanel from "@/components/editor/CopilotPanel";

interface ContentEditorProps {
  draftId: string;
  initialContent: string;
  brief: Record<string, unknown>;
  outline: Record<string, unknown>;
  apiUrl: string;
}

export default function ContentEditor({ draftId, initialContent, brief, outline, apiUrl }: ContentEditorProps) {
  const [saveStatus, setSaveStatus] = useState<"saved" | "saving" | "unsaved">("saved");

  const handleAutoSave = useCallback(async (html: string) => {
    setSaveStatus("saving");
    try {
      await fetch(`${apiUrl}/content/${draftId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ body: html }),
      });
      setSaveStatus("saved");
    } catch {
      setSaveStatus("unsaved");
    }
  }, [draftId, apiUrl]);

  const briefData = brief as {
    title?: string;
    target_keyword?: string;
    word_count_target?: number;
    key_sections?: string[];
    tone?: string;
  };

  const outlineData = outline as {
    sections?: { heading: string; subheadings: string[] }[];
  };

  return (
    <div className="flex h-full overflow-hidden">
      <BriefPanel brief={briefData} outline={outlineData} />

      <div className="flex-1 flex flex-col min-w-0 bg-gray-900">
        <div className="flex items-center justify-between border-b border-gray-800 px-4 py-2">
          <h1 className="text-sm font-semibold text-gray-200 truncate">
            {briefData.title || "Content Draft"}
          </h1>
          <span className={`text-xs ${
            saveStatus === "saved" ? "text-emerald-500" :
            saveStatus === "saving" ? "text-amber-400 animate-pulse" :
            "text-red-400"
          }`}>
            {saveStatus === "saved" ? "✓ Saved" : saveStatus === "saving" ? "Saving…" : "Unsaved"}
          </span>
        </div>
        <div className="flex-1 overflow-hidden">
          <TipTapEditor
            content={initialContent}
            onAutoSave={handleAutoSave}
            targetWordCount={briefData.word_count_target}
          />
        </div>
      </div>

      <CopilotPanel draftId={draftId} apiUrl={apiUrl} />
    </div>
  );
}
