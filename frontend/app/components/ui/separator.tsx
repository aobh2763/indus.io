import * as React from "react";
import { cn } from "../../../lib/utils";

function Separator({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("shrink-0 bg-gray-800 h-[1px] w-full", className)}
      role="separator"
      {...props}
    />
  );
}

export { Separator };
