import type { ReactNode } from "react";
import { cn } from "@/lib/design/cn";

/** Small mono label above a heading. */
export function Eyebrow({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <p className={cn("font-mono text-xs font-medium tracking-[0.14em] text-accent uppercase", className)}>{children}</p>
  );
}
