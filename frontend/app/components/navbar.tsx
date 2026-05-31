import { Factory, Camera } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router";
import { ProjectNotificationBell } from "~/components/projects/project-notification-bell";
import { useAuthStore } from "~/features/auth/auth.store";

export default function Navbar() {
  const { pathname } = useLocation();
  const { user, logout } = useAuthStore();
  const [currentPage, setCurrentPage] = useState("dashboard");

  useEffect(() => {
    if (pathname === "/") setCurrentPage("dashboard");
    else if (pathname === "/projects-management") setCurrentPage("projects");
    else if (pathname === "/pipeline-builder") setCurrentPage("pipeline");
    else if (pathname === "/kpis" || pathname.startsWith("/kpi/")) setCurrentPage("kpis");
    else if (pathname === "/scanner") setCurrentPage("scanner");
  }, [pathname]);

  const isPipeline = currentPage === "pipeline";
  const isKpis = currentPage === "kpis";
  const initials = user?.name?.split(" ").map((n: string) => n[0]).join("").slice(0, 2).toUpperCase();

  return (
    <header
      className={`${isPipeline ? "fixed w-full" : "sticky"} top-0 z-50 border-b border-neutral-800/60 bg-black/75 backdrop-blur-xl`}
    >
      <div className="max-w-[1600px] mx-auto flex items-center justify-between h-12 px-5">

        {/* Left: brand + breadcrumb */}
        <div className="flex items-center gap-2.5">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="flex items-center justify-center w-[26px] h-[26px] rounded-[6px]">
              <Factory className="h-3.5 w-3.5" />
            </div>
            <span className="text-[13px] font-medium text-white tracking-tight">
              indus.io
            </span>
          </Link>

          <div className="w-px h-3.5 bg-neutral-700" />

          <span className="text-[13px] text-neutral-400">
            {currentPage === "dashboard" ? "Dashboard"
              : currentPage === "projects" ? "Projects"
                : currentPage === "kpis" ? "KPIs"
                  : currentPage === "scanner" ? "AI Scanner"
                    : "Pipeline builder"}
          </span>
        </div>

        {/* Right: nav + user */}
        <div className="flex items-center gap-1.5">
          <NavLink to="/scanner">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <Camera className="h-3.5 w-3.5" /> Scanner
            </span>
          </NavLink>
          {!isPipeline && !isKpis ? (
            <>
              <NavLink to={currentPage === "projects" ? "/" : "/projects-management"}>
                {currentPage === "dashboard" ? "Projects" : "Dashboard"}
              </NavLink>
              <NavLink to="/kpis">KPIs</NavLink>
            </>
          ) : (
            <>
              <NavLink to="/">Dashboard</NavLink>
              <NavLink to="/projects-management">Projects</NavLink>
              {!isKpis && <NavLink to="/kpis">KPIs</NavLink>}
            </>
          )}

          <div className="w-px h-4 bg-neutral-800 mx-1" />

          {user && <ProjectNotificationBell />}

          {/* User pill */}
          <button className="flex items-center gap-2 pl-1.5 pr-3 py-1 text-[12px] text-neutral-400 hover:text-white hover:border-neutral-700 rounded-[7px] hover:bg-neutral-900 transition-colors">
            <span className="flex items-center justify-center w-5 h-5 rounded-full bg-neutral-800 text-neutral-300 text-[10px] font-medium">
              {initials}
            </span>
            {user?.name}
          </button>

          {/* Logout */}
          <button
            onClick={logout}
            className="flex items-center gap-1.5 px-2.5 py-1 text-[12px] text-neutral-500 hover:text-red-400 border border-neutral-800 hover:border-red-900 hover:bg-red-950/40 rounded-[7px] transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <Link
      to={to}
      className="flex items-center gap-1.5 px-2.5 py-1 text-[12px] text-neutral-400 hover:text-white border border-neutral-800 hover:border-neutral-700 hover:bg-neutral-900 rounded-[7px] transition-colors"
    >
      {children}
    </Link>
  );
}
