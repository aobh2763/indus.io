import { Button } from "./ui/button";
import { Factory } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router";
import { useAuthStore } from "~/features/auth/auth.store";

export default function Navbar() {
  const { logout } = useAuthStore();
  const { pathname } = useLocation();
  const [currentPage, setCurrentPage] = useState('dashboard');

  useEffect(() => {
    if (pathname === '/') {
      setCurrentPage('dashboard');
    } else if (pathname === '/projects-management') {
      setCurrentPage('projects');
    } else if (pathname === '/pipeline-builder') {
      setCurrentPage('pipeline');
    }
  }, [pathname]);

  return (
    <header className={`${currentPage === 'pipeline' ? 'fixed w-full' : 'sticky'} top-0 z-50 border-b border-neutral-800 bg-black/80 backdrop-blur-md`}>
      < div className="max-w-[1600px] mx-auto flex items-center justify-between h-12 px-5">
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2 text-sm font-semibold text-white tracking-tight">
            <Factory className="h-4 w-4 text-white" />
            indus.io
          </Link>
          <span className="text-neutral-700">/</span>
          <span className="text-sm text-neutral-400">
            {currentPage === 'dashboard' ?
              <>Dashboard</> :
              currentPage === 'projects' ? <>Projects</> : <>Pipeline Builder</>
            }
          </span>
        </div>
        <div className="flex items-center gap-2">
          {currentPage !== 'pipeline' ?
            <Link to={currentPage === 'projects' ? '/' : '/projects-management'} className="flex items-center gap-1.5 px-2.5 py-1 text-xs text-neutral-400 hover:text-white border border-neutral-800 rounded-md hover:border-neutral-700 transition-colors">
              {currentPage === 'dashboard' ? <>Projects</> : <>Dashboard</>}
            </Link>
            :
            <>
              <Link to='/' className="flex items-center gap-1.5 px-2.5 py-1 text-xs text-neutral-400 hover:text-white border border-neutral-800 rounded-md hover:border-neutral-700 transition-colors">
                Dashboard
              </Link>
              <Link to='/projects-management' className="flex items-center gap-1.5 px-2.5 py-1 text-xs text-neutral-400 hover:text-white border border-neutral-800 rounded-md hover:border-neutral-700 transition-colors">
                Projects
              </Link>
            </>
          }
          <Button
            size='sm'
            onClick={logout}
            variant="outline"
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs text-neutral-400 hover:text-white border border-neutral-800 rounded-md hover:border-neutral-700 transition-colors"
          >
            Logout
          </Button>
        </div>
      </div>
    </header >
  );
}
