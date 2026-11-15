import type { ReactNode } from "react";
import { cn } from "@/lib/design/cn";

/**
 * A small line drawing per experiment, so cards and headers are recognisable at a glance.
 * Drawn with currentColor on a 48x48 grid; unknown experiments get a plain grid mark.
 */
export function ExperimentGlyph({ id, className }: { id: string; className?: string }) {
  const art = glyphs[id.slice(0, 6)] ?? fallback;
  return (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
      className={cn("size-12", className)}
    >
      {art}
    </svg>
  );
}

const glyphs: Record<string, ReactNode> = {
  // exp000: an IR blaster sending a signal.
  exp000: (
    <>
      <rect x="6" y="20" width="12" height="9" rx="2" />
      <path d="M22 20.5c2 2.2 2 5.8 0 8" />
      <path d="M27 17c4 4.2 4 11.8 0 16" />
      <path d="M32 13.5c6 6.2 6 16.8 0 23" />
      <circle cx="12" cy="24.5" r="1.2" fill="currentColor" stroke="none" />
    </>
  ),
  // exp001: a camera looking down at a tracked target.
  exp001: (
    <>
      <rect x="15" y="6" width="18" height="10" rx="2" />
      <circle cx="24" cy="11" r="2.5" />
      <path d="M24 16v6" strokeDasharray="1.5 2.5" />
      <rect x="9" y="26" width="30" height="16" rx="1.5" strokeDasharray="2 2.5" />
      <path d="M21 34h6M24 31v6" />
    </>
  ),
  // exp002: a two-link arm reaching for a block.
  exp002: (
    <>
      <path d="M8 42h20" />
      <rect x="13" y="37" width="10" height="5" rx="1" />
      <path d="M18 37l-2-13 14-7" />
      <circle cx="16" cy="24" r="1.8" />
      <circle cx="30" cy="17" r="1.8" />
      <path d="M30 17l5 6M33.5 21.5l3.5-1.5M33.5 21.5l1 3.5" />
      <rect x="35" y="35" width="6" height="7" rx="1" />
    </>
  ),
};

const fallback = (
  <>
    <rect x="8" y="8" width="32" height="32" rx="3" />
    <path d="M8 24h32M24 8v32" strokeDasharray="2 3" />
  </>
);
