import * as React from "react";
import { cn } from "../../lib/utils";

interface ScrollAreaProps extends React.HTMLAttributes<HTMLDivElement> {
  maxHeight?: string;
}

function ScrollArea({ className, maxHeight = "300px", children, ...props }: ScrollAreaProps) {
  return (
    <div
      className={cn("overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent", className)}
      style={{ maxHeight }}
      {...props}
    >
      {children}
    </div>
  );
}

export { ScrollArea };
