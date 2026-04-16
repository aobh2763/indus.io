import { Link } from "react-router";

export default function Navbar() {
  return (
    <header className="fixed left-0 right-0 top-4 z-50 mx-auto w-full max-w-4xl rounded-full border border-gray-800 bg-gray-900/70 px-6 backdrop-blur-md shadow-xl">
      <nav className="flex h-14 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-sm font-semibold tracking-tight text-white ml-2">
          <img src="/favicon.ico" alt="indus.io logo" className="h-5 w-5 rounded-sm" />
          <span>indus.io</span>
        </Link>
        <div className="flex items-center gap-3">
          <Link
            to="/pipeline-builder"
            className="rounded-lg border border-gray-700 px-4 py-2 text-xs font-medium text-gray-200 transition hover:border-gray-600 hover:bg-gray-800"
          >
            Pipeline
          </Link>
          <Link
            to="/projects-management"
            className="rounded-lg border border-gray-700 px-4 py-2 text-xs font-medium text-gray-200 transition hover:border-gray-600 hover:bg-gray-800"
          >
            Projects Management
          </Link>
        </div>
      </nav>
    </header>
  );
}
