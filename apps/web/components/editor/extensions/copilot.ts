// TipTap extension: AI co-pilot slash commands (/suggest /expand /check)
// TODO: implement Extension that calls FastAPI SSE endpoint on command trigger
import { Extension } from "@tiptap/react";
export const CopilotExtension = Extension.create({ name: "copilot" });
