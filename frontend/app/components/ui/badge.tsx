import * as React from "react";
import { cn } from "../../../lib/utils";

type BadgeVariant = "default" | "secondary" | "destructive" | "outline" | "success" | "warning";

const variantClasses: Record<BadgeVariant, string> = {
  default: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  secondary: "bg-gray-500/15 text-gray-300 border-gray-500/30",
  destructive: "bg-red-500/15 text-red-400 border-red-500/30",
  outline: "bg-transparent text-gray-300 border-gray-700",
  success: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  warning: "bg-amber-500/15 text-amber-400 border-amber-500/30",
};

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: BadgeVariant;
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}

export { Badge, type BadgeVariant };
