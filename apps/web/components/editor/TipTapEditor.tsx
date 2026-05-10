"use client";

import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Placeholder from "@tiptap/extension-placeholder";
import { useEffect, useCallback, useRef } from "react";

interface TipTapEditorProps {
  content: string;
  onChange?: (html: string) => void;
  onAutoSave?: (html: string) => void;
  targetWordCount?: number;
}

function countWords(text: string): number {
  return text.trim() ? text.trim().split(/\s+/).length : 0;
}

export default function TipTapEditor({ content, onChange, onAutoSave, targetWordCount }: TipTapEditorProps) {
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder: "Start writing your content here…" }),
    ],
    content,
    editorProps: {
      attributes: {
        class: "prose prose-invert max-w-none min-h-[400px] px-6 py-4 focus:outline-none text-gray-100",
      },
    },
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      onChange?.(html);
      if (onAutoSave) {
        if (saveTimer.current) clearTimeout(saveTimer.current);
        saveTimer.current = setTimeout(() => onAutoSave(html), 2000);
      }
    },
  });

  useEffect(() => {
    return () => {
      if (saveTimer.current) clearTimeout(saveTimer.current);
    };
  }, []);

  const wordCount = editor ? countWords(editor.getText()) : 0;
  const progress = targetWordCount ? Math.min(100, Math.round((wordCount / targetWordCount) * 100)) : null;

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-4 border-b border-gray-800 px-4 py-2 text-xs text-gray-500">
        <span>{wordCount.toLocaleString()} words</span>
        {targetWordCount && (
          <>
            <span>/ {targetWordCount.toLocaleString()} target</span>
            <div className="flex-1 max-w-32 h-1 rounded bg-gray-800 overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
            <span className={progress && progress >= 100 ? "text-emerald-400" : ""}>{progress}%</span>
          </>
        )}
        <div className="flex gap-2 ml-auto">
          <button
            onClick={() => editor?.chain().focus().toggleBold().run()}
            className={`px-2 py-0.5 rounded font-bold ${editor?.isActive("bold") ? "bg-gray-700 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >B</button>
          <button
            onClick={() => editor?.chain().focus().toggleItalic().run()}
            className={`px-2 py-0.5 rounded italic ${editor?.isActive("italic") ? "bg-gray-700 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >I</button>
          <button
            onClick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()}
            className={`px-2 py-0.5 rounded text-xs ${editor?.isActive("heading", { level: 2 }) ? "bg-gray-700 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >H2</button>
          <button
            onClick={() => editor?.chain().focus().toggleHeading({ level: 3 }).run()}
            className={`px-2 py-0.5 rounded text-xs ${editor?.isActive("heading", { level: 3 }) ? "bg-gray-700 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >H3</button>
          <button
            onClick={() => editor?.chain().focus().toggleBulletList().run()}
            className={`px-2 py-0.5 rounded text-xs ${editor?.isActive("bulletList") ? "bg-gray-700 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >• List</button>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto">
        <EditorContent editor={editor} className="h-full" />
      </div>
    </div>
  );
}
