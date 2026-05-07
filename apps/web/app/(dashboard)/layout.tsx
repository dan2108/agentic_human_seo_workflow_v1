// TODO: add sidebar nav with links to Pipeline, Gates, Editor, Aftercare
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <main>{children}</main>
    </div>
  );
}
