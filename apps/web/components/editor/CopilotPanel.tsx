"use client";

import { useState, useRef } from "react";

interface CopilotPanelProps {
  draftId: string;
  apiUrl: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function CopilotPanel({ draftId, apiUrl }: CopilotPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  async function sendPrompt() {
    if (!input.trim() || streaming) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setStreaming(true);

    abortRef.current = new AbortController();
    const url = `${apiUrl}/content/${draftId}/copilot?prompt=${encodeURIComponent(userMsg)}`;

    try {
      const resp = await fetch(url, { signal: abortRef.current.signal });
      if (!resp.ok || !resp.body) throw new Error("Stream failed");

      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = line.slice(6);
          if (payload === "[DONE]") break;
          try {
            const { text } = JSON.parse(payload);
            setMessages((prev) => {
              const next = [...prev];
              next[next.length - 1] = {
                ...next[next.length - 1],
                content: next[next.length - 1].content + text,
              };
              return next;
            });
          } catch {}
        }
      }
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setMessages((prev) => [...prev, { role: "assistant", content: "Error: failed to get response." }]);
      }
    } finally {
      setStreaming(false);
    }
  }

  return (
    <aside className="w-80 shrink-0 border-l border-gray-800 bg-gray-950 flex flex-col">
      <div className="px-4 py-3 border-b border-gray-800">
        <h2 className="text-xs font-bold uppercase tracking-wide text-gray-500">AI Copilot</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <p className="text-xs text-gray-600 text-center mt-8">
            Ask the copilot to improve a section, suggest transitions, or check keyword density.
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`text-xs rounded-lg px-3 py-2 ${
            msg.role === "user"
              ? "bg-blue-900/40 text-blue-100 self-end ml-4"
              : "bg-gray-800 text-gray-200 mr-4"
          }`}>
            {msg.content || (streaming && i === messages.length - 1 ? (
              <span className="animate-pulse text-gray-500">Thinking…</span>
            ) : null)}
          </div>
        ))}
      </div>

      <div className="p-3 border-t border-gray-800 flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendPrompt(); } }}
          placeholder="Ask copilot…"
          rows={2}
          disabled={streaming}
          className="flex-1 rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-xs text-gray-100 placeholder-gray-500 focus:border-blue-500 focus:outline-none resize-none disabled:opacity-50"
        />
        <button
          onClick={sendPrompt}
          disabled={streaming || !input.trim()}
          className="rounded-lg bg-blue-600 px-3 py-2 text-xs font-medium text-white hover:bg-blue-500 disabled:opacity-50 transition-colors"
        >
          Send
        </button>
      </div>
    </aside>
  );
}
