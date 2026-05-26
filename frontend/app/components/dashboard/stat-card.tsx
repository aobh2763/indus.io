import { Card, CardContent } from "../ui/card";
import { cn } from "../../../lib/utils";
import { Skeleton } from "../ui/skeleton";
import type { ReactNode } from "react";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  trend?: string;
  description?: string;
  color?: "emerald" | "blue" | "purple" | "rose" | "amber" | "cyan";
  isLoading?: boolean;
}

const colorMap = {
  emerald: {
    iconBg: "bg-emerald-500/10",
    iconText: "text-emerald-500",
    glow: "hover:shadow-emerald-500/5",
    ring: "hover:border-emerald-500/20",
  },
  blue: {
    iconBg: "bg-blue-500/10",
    iconText: "text-blue-500",
    glow: "hover:shadow-blue-500/5",
    ring: "hover:border-blue-500/20",
  },
  purple: {
    iconBg: "bg-purple-500/10",
    iconText: "text-purple-500",
    glow: "hover:shadow-purple-500/5",
    ring: "hover:border-purple-500/20",
  },
  rose: {
    iconBg: "bg-rose-500/10",
    iconText: "text-rose-500",
    glow: "hover:shadow-rose-500/5",
    ring: "hover:border-rose-500/20",
  },
  amber: {
    iconBg: "bg-amber-500/10",
    iconText: "text-amber-500",
    glow: "hover:shadow-amber-500/5",
    ring: "hover:border-amber-500/20",
  },
  cyan: {
    iconBg: "bg-cyan-500/10",
    iconText: "text-cyan-500",
    glow: "hover:shadow-cyan-500/5",
    ring: "hover:border-cyan-500/20",
  },
};

export function StatCard({ title, value, icon, trend, description, color = "emerald", isLoading }: StatCardProps) {
  const colors = colorMap[color];

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-9 w-9 rounded-lg" />
        </div>
        <Skeleton className="h-8 w-16 mt-3" />
        <Skeleton className="h-3 w-32 mt-2" />
      </Card>
    );
  }

  return (
    <Card
      className={cn(
        "p-6 transition-all duration-300 hover:-translate-y-0.5",
        colors.glow,
        colors.ring,
        "hover:shadow-xl"
      )}
    >
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-400 tracking-tight">{title}</p>
        <div className={cn("flex items-center justify-center h-9 w-9 rounded-lg", colors.iconBg)}>
          <span className={colors.iconText}>{icon}</span>
        </div>
      </div>
      <div className="mt-3">
        <p className="text-3xl font-bold text-white tabular-nums tracking-tight">{value}</p>
      </div>
      {(trend || description) && (
        <p className="text-xs text-gray-500 mt-2 flex items-center gap-1.5">
          {trend && (
            <span
              className={cn(
                "font-semibold",
                trend.startsWith("+") || trend.startsWith("↑")
                  ? "text-emerald-400"
                  : trend.startsWith("-") || trend.startsWith("↓")
                    ? "text-rose-400"
                    : "text-gray-400"
              )}
            >
              {trend}
            </span>
          )}
          {trend && description && <span className="text-gray-600">·</span>}
          {description && <span>{description}</span>}
        </p>
      )}
    </Card>
  );
}
