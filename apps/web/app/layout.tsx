import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SEO Workflow",
  description: "Agentic Human SEO Workflow Management",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
