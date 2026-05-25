import { Link, useLocation } from "react-router";
import { Factory } from "lucide-react";

export default function Navbar() {
  const location = useLocation();
  // Dashboard has its own header — hide navbar there
  if (location.pathname === "/") return null;

  return (
    <header className="sticky top-0 z-50 border-b border-neutral-800 bg-black/80 backdrop-blur-md">
      <nav className="max-w-[1600px] mx-auto flex items-center justify-between h-12 px-5">
        <Link to="/" className="flex items-center gap-2 text-sm font-semibold text-white tracking-tight">
          <Factory className="h-4 w-4" />
          indus.io
        </Link>
        <div className="flex items-center gap-1">
          {[
            { to: "/", label: "Dashboard" },
            { to: "/pipeline-builder", label: "Pipeline" },
            { to: "/projects-management", label: "Projects" },
          ].map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
                location.pathname === link.to
                  ? "text-white bg-neutral-800"
                  : "text-neutral-400 hover:text-white hover:bg-neutral-900"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}
