import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "ai-node": "#0c4a6e",
        "hybrid-node": "#713f12",
        "human-node": "#14532d",
        "gate-node": "#450a0a",
        "ui-node": "#4a044e",
      },
    },
  },
  plugins: [],
};

export default config;
