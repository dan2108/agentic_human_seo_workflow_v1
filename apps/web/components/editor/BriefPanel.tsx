interface BriefData {
  title?: string;
  target_keyword?: string;
  word_count_target?: number;
  key_sections?: string[];
  tone?: string;
}

interface OutlineData {
  sections?: { heading: string; subheadings: string[] }[];
}

export default function BriefPanel({ brief, outline }: { brief: BriefData; outline: OutlineData }) {
  return (
    <aside className="w-72 shrink-0 border-r border-gray-800 bg-gray-950 overflow-y-auto p-4 space-y-5">
      <div>
        <h2 className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-2">Brief</h2>
        {brief.title && (
          <p className="text-sm font-semibold text-gray-100 mb-1">{brief.title}</p>
        )}
        {brief.target_keyword && (
          <div className="flex items-center gap-1.5 mb-1">
            <span className="text-xs text-gray-500">Target:</span>
            <span className="text-xs bg-blue-900/50 text-blue-300 rounded px-1.5 py-0.5">{brief.target_keyword}</span>
          </div>
        )}
        {brief.word_count_target && (
          <div className="text-xs text-gray-500">Target words: {brief.word_count_target.toLocaleString()}</div>
        )}
        {brief.tone && (
          <div className="text-xs text-gray-500 mt-0.5">Tone: {brief.tone}</div>
        )}
      </div>

      {brief.key_sections && brief.key_sections.length > 0 && (
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-2">Key Sections</h3>
          <ul className="space-y-1">
            {brief.key_sections.map((s, i) => (
              <li key={i} className="text-xs text-gray-300 flex gap-1.5">
                <span className="text-gray-600">{i + 1}.</span>{s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {outline.sections && outline.sections.length > 0 && (
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-2">Outline</h3>
          <div className="space-y-2">
            {outline.sections.map((section, i) => (
              <div key={i}>
                <p className="text-xs font-semibold text-gray-200">{section.heading}</p>
                {section.subheadings.map((sub, j) => (
                  <p key={j} className="text-xs text-gray-400 pl-3 mt-0.5">↳ {sub}</p>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </aside>
  );
}
