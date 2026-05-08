import Link from "next/link";

const navItems = [
  { href: "/pipeline", label: "Pipeline", icon: "⚡" },
  { href: "/gates", label: "Gates", icon: "🚦" },
  { href: "/editor", label: "Editor", icon: "✍️" },
  { href: "/aftercare", label: "Aftercare", icon: "📈" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
      {/* Sidebar */}
      <aside className="flex w-56 flex-col border-r border-gray-800 bg-gray-950">
        <div className="flex h-14 items-center border-b border-gray-800 px-4">
          <span className="text-sm font-bold text-gray-100 tracking-tight">SEO Workflow</span>
        </div>
        <nav className="flex-1 space-y-1 p-3">
          {navItems.map(({ href, label, icon }) => (
            <Link
              key={href}
              href={href}
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-gray-400 hover:bg-gray-800 hover:text-gray-100 transition-colors"
            >
              <span>{icon}</span>
              <span>{label}</span>
            </Link>
          ))}
        </nav>
        <div className="border-t border-gray-800 p-3">
          <form action="/api/auth/signout" method="post">
            <button
              type="submit"
              className="w-full rounded-lg px-3 py-2 text-left text-sm text-gray-500 hover:text-gray-300 transition-colors"
            >
              Sign out
            </button>
          </form>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
