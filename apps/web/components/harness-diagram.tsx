import type { ReactNode } from "react";
import { cn } from "@/lib/design/cn";

/**
 * The harness as a flow: who asks, the gate that decides, the device, and the log every
 * step lands in. HTML rather than SVG so it reflows on phones and uses the colour tokens.
 */
export function HarnessDiagram() {
  return (
    <div className="rounded-card border border-line bg-surface p-5 shadow-card sm:p-6">
      <div className="grid items-stretch gap-3 lg:grid-cols-[1fr_auto_1fr_auto_1.6fr_auto_1fr]">
        <Node title="Request" lines={["CLI, admin page", "or a policy"]} />
        <Arrow />
        <Node title="Tool registry" lines={["typed tools", "argument schemas"]} />
        <Arrow />
        <Node
          title="Safety gate"
          tone="accent"
          lines={[
            "STOP file · allowlist",
            "argument and duration caps",
            "confirmation · rate limits",
            "interlocks: fresh pose, arena fence",
          ]}
        />
        <Arrow />
        <Node title="Device" lines={["IR blaster today", "the arm next"]} />
      </div>

      <div className="my-4 flex items-center gap-3 text-xs text-subtle">
        <span className="h-px flex-1 bg-line" />
        <span className="font-mono">every step, refusals included</span>
        <span aria-hidden>↓</span>
        <span className="h-px flex-1 bg-line" />
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <Node title="Event log" tone="ink" lines={["append-only JSONL", "one contract: TS, Python, Rust"]} />
        <Node title="Camera" lines={["tracks, never stores frames", "feeds interlocks and the judge"]} />
        <Node title="Results" lines={["summaries computed from logs", "replays, evals, this site"]} />
      </div>
    </div>
  );
}

function Node({ title, lines, tone = "plain" }: { title: string; lines: ReactNode[]; tone?: "plain" | "accent" | "ink" }) {
  return (
    <div
      className={cn(
        "rounded-control border p-4",
        tone === "accent" && "border-accent bg-accent-soft",
        tone === "ink" && "border-line-strong bg-surface-2",
        tone === "plain" && "border-line bg-bg",
      )}
    >
      <p className={cn("text-sm font-semibold", tone === "accent" && "text-accent")}>{title}</p>
      <ul className="mt-1.5 space-y-0.5 text-xs text-muted">
        {lines.map((l, i) => (
          <li key={i}>{l}</li>
        ))}
      </ul>
    </div>
  );
}

function Arrow() {
  return (
    <div aria-hidden className="flex items-center justify-center text-subtle">
      <span className="lg:hidden">↓</span>
      <span className="hidden lg:inline">→</span>
    </div>
  );
}
