import { X, ArrowLeft } from "lucide-react";
import { useEffect } from "react";

interface SlideOverPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onBack?: () => void;
  canGoBack?: boolean;
  title: React.ReactNode;
  children: React.ReactNode;
  width?: string;
}

export function SlideOverPanel({ isOpen, onClose, onBack, canGoBack, title, children, width = "max-w-md" }: SlideOverPanelProps) {
  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Prevent background scroll
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] overflow-hidden">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      
      {/* Panel */}
      <div className="fixed inset-y-0 right-0 flex max-w-full pl-10 animate-in slide-in-from-right duration-300">
        <div className={`w-screen ${width}`}>
          <div className="flex h-full flex-col bg-neutral-950 border-l border-neutral-800 shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-800 shrink-0">
              <div className="flex items-center gap-3">
                {canGoBack && onBack && (
                  <button
                    onClick={onBack}
                    className="flex items-center gap-1.5 rounded-md text-sm font-medium text-neutral-400 hover:text-white hover:bg-neutral-800 px-2 py-1.5 -ml-2 transition-colors cursor-pointer"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    Back
                  </button>
                )}
                <div className="text-lg font-semibold text-white tracking-tight flex items-center gap-2 ml-1">{title}</div>
              </div>
              <button
                onClick={onClose}
                className="rounded-md text-neutral-400 hover:text-white hover:bg-neutral-800 p-1.5 transition-colors cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            {/* Content */}
            <div className="relative flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-neutral-800 scrollbar-track-transparent">
              {children}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
