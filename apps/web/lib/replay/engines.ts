/**
 * Two interchangeable engines for the replay viewer. Both validate a JSONL log
 * against the event contract and fold summaries; the viewer can switch between
 * them to compare speed on the visitor's own machine.
 *
 * - "ts":   @lab/schema (zod), the contract's authoring source. Default, because
 *           it measured faster in V8 (see content/log/2026-11-10-wasm-replay-viewer.mdx).
 * - "wasm": crates/lab-events compiled to WebAssembly, the code labctl runs.
 *           Loaded only when selected.
 */
import { Event, type LogIssue, type RunSummary, summarizeRun, validateLog } from "@lab/schema";

export type EngineName = "ts" | "wasm";

export type OpenRun = {
  length: number;
  valid: boolean;
  issues: LogIssue[];
  event(i: number): Event | undefined;
  summaryAt(n: number): RunSummary;
  free(): void;
};

export type Engine = { name: EngineName; label: string; open(text: string): OpenRun };

export const tsEngine: Engine = {
  name: "ts",
  label: "TypeScript (zod)",
  open(text) {
    const lines = text.split("\n");
    const issues = validateLog(lines);
    const events: Event[] = [];
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const r = Event.safeParse(JSON.parse(line));
        if (r.success) events.push(r.data);
      } catch {
        // Not JSON: already reported by validateLog.
      }
    }
    return {
      length: events.length,
      valid: issues.length === 0,
      issues,
      event: (i) => events[i],
      summaryAt: (n) => summarizeRun(events.slice(0, Math.max(0, n))),
      free: () => {},
    };
  },
};

let wasm: Promise<Engine> | undefined;

/** Load the Rust/WASM engine on first use (~350 KB, inlined in its chunk). */
export function loadWasmEngine(): Promise<Engine> {
  wasm ??= import("@lab/events-wasm")
    .then((m) => m.loadLab())
    .then((lab) => ({ name: "wasm" as const, label: "Rust (WASM)", open: (text: string) => lab.openRun(text) }));
  return wasm;
}

export async function getEngine(name: EngineName): Promise<Engine> {
  return name === "ts" ? tsEngine : loadWasmEngine();
}
