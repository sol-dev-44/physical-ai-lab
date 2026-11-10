/**
 * Fold a run's events into the numbers the site shows.
 * Pure and deterministic: the same log always gives the same summary.
 */
import type { Event } from "./event";

export type RunSummary = {
  run_id: string;
  experiment_id: string | null;
  status: "completed" | "aborted" | "failed" | "open";
  null_test: boolean;
  started_at: string | null;
  ended_at: string | null;
  requested: number;
  denied: number;
  sent: number;
  failed: number;
  observed: number;
  succeeded: number;
  /** succeeded / observed, null when nothing was observed. */
  success_rate: number | null;
  /** Per-tool breakdown, keyed by tool name. */
  tools: Record<string, { requested: number; sent: number; succeeded: number; observed: number }>;
};

export function summarizeRun(events: readonly Event[]): RunSummary {
  const s: RunSummary = {
    run_id: events[0]?.run_id ?? "",
    experiment_id: null,
    status: "open",
    null_test: false,
    started_at: null,
    ended_at: null,
    requested: 0,
    denied: 0,
    sent: 0,
    failed: 0,
    observed: 0,
    succeeded: 0,
    success_rate: null,
    tools: {},
  };
  const tool = (name: string) => (s.tools[name] ??= { requested: 0, sent: 0, succeeded: 0, observed: 0 });

  for (const e of events) {
    switch (e.type) {
      case "run.started":
        s.experiment_id = e.payload.experiment_id;
        s.null_test = e.payload.null_test ?? false;
        s.started_at = e.ts;
        break;
      case "run.ended":
        s.status = e.payload.status;
        s.ended_at = e.ts;
        break;
      case "command.requested":
        s.requested++;
        tool(e.tool).requested++;
        break;
      case "safety.checked":
        if (e.payload.decision === "deny") s.denied++;
        break;
      case "command.sent":
        s.sent++;
        tool(e.tool).sent++;
        break;
      case "command.failed":
        s.failed++;
        break;
      case "outcome.observed":
        s.observed++;
        if (e.payload.success) s.succeeded++;
        if (e.tool) {
          tool(e.tool).observed++;
          if (e.payload.success) tool(e.tool).succeeded++;
        }
        break;
      case "note":
        break;
    }
  }
  s.success_rate = s.observed ? s.succeeded / s.observed : null;
  return s;
}
