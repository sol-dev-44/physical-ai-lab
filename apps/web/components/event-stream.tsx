"use client";

import { m } from "motion/react";
import Link from "next/link";
import { cn } from "@/lib/design/cn";
import { easeOutQuint } from "@/lib/design/motion";
import type { LogLine } from "@/lib/sample-run";

const toneClass: Record<LogLine["tone"], string> = {
  neutral: "text-muted",
  ok: "text-ok",
  danger: "text-danger",
  accent: "text-accent",
};

/** The sample run, printed line by line like the harness writes it. Decorative; the data is real fixture data. */
export function EventStream({ lines }: { lines: LogLine[] }) {
  return (
    <figure className="overflow-hidden rounded-card border border-line bg-surface shadow-lift">
      <div className="flex items-center justify-between border-b border-line bg-surface-2 px-4 py-2.5">
        <div className="flex items-center gap-1.5" aria-hidden>
          <span className="size-2.5 rounded-full bg-line-strong" />
          <span className="size-2.5 rounded-full bg-line-strong" />
          <span className="size-2.5 rounded-full bg-line-strong" />
        </div>
        <span className="font-mono text-[0.6875rem] text-subtle">events/exp000 · sample.jsonl</span>
      </div>
      <ol className="space-y-1 p-4 font-mono text-[0.75rem] leading-relaxed sm:p-5" aria-label="Sample run log">
        {lines.map((l, i) => (
          <m.li
            key={l.seq}
            className="grid grid-cols-[4.25rem_1fr] gap-x-3 sm:grid-cols-[4.5rem_9.5rem_1fr]"
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.25 + i * 0.09, duration: 0.4, ease: easeOutQuint }}
          >
            <span className="text-subtle tabular-nums">{l.time}</span>
            <span className="truncate text-fg">{l.type}</span>
            <span className={cn("col-start-2 truncate sm:col-start-auto", toneClass[l.tone])}>
              {[l.tool, l.detail].filter(Boolean).join(" · ")}
            </span>
          </m.li>
        ))}
      </ol>
      <figcaption className="flex flex-wrap items-center justify-between gap-2 border-t border-line px-4 py-3 text-xs text-muted sm:px-5">
        <span>A sample run from the contract fixtures: one denial, one device timeout.</span>
        <Link href="/harness/replay" className="font-medium text-accent hover:underline">
          Step through it →
        </Link>
      </figcaption>
    </figure>
  );
}
