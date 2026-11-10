/**
 * The lab event library (crates/lab-events) running as WebAssembly.
 *
 * Same validator and summary fold as `labctl` and the contract tests, so the
 * browser replay viewer cannot drift from the Rust tooling. Results come back
 * typed with the zod contract's types.
 *
 *   const lab = await loadLab();
 *   const run = lab.openRun(text);   // parse + validate once
 *   run.summaryAt(10);               // fold the first 10 events
 *   run.free();                      // release WASM memory when done
 */
import { Event, type LogIssue, type RunSummary } from "@lab/schema";
import { Run, analyze, check_event, initSync } from "../generated/bindings.js";
import wasmBase64 from "../generated/wasm-base64.js";

export type { LogIssue, RunSummary };

export type LabRun = {
  /** Number of lines that are valid events (invalid lines are reported in `issues`). */
  readonly length: number;
  /** True when the whole log passes every contract and log rule. */
  readonly valid: boolean;
  readonly issues: LogIssue[];
  /** The i-th valid event. */
  event(i: number): Event | undefined;
  /** Summary of the first `n` valid events. */
  summaryAt(n: number): RunSummary;
  /** Release the WASM memory held for this log. */
  free(): void;
};

export type Lab = {
  openRun(text: string): LabRun;
  /** Check one event (a JSON string) against the contract: null if valid, else the reason. */
  checkEvent(json: string): string | null;
  /** Validate and summarize a whole log in one call. */
  analyze(text: string): { issues: LogIssue[]; summary: RunSummary };
};

function decode(base64: string): Uint8Array {
  const bin = atob(base64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

let lab: Lab | undefined;

function wrap(run: Run): LabRun {
  return {
    length: run.len(),
    valid: run.valid(),
    issues: JSON.parse(run.issues()) as LogIssue[],
    event(i) {
      const line = run.event(i);
      // Already validated by the Rust contract; zod re-checks the shape cheaply.
      return line === undefined ? undefined : Event.parse(JSON.parse(line));
    },
    summaryAt: (n) => JSON.parse(run.summary_at(n)) as RunSummary,
    free: () => run.free(),
  };
}

/** Instantiate the module once (synchronous compile of ~350 KB; well under 50 ms). */
export function loadLabSync(): Lab {
  if (!lab) {
    initSync({ module: decode(wasmBase64) });
    lab = {
      openRun: (text) => wrap(new Run(text)),
      checkEvent: (json) => check_event(json) ?? null,
      analyze: (text) => JSON.parse(analyze(text)) as { issues: LogIssue[]; summary: RunSummary },
    };
  }
  return lab;
}

/** Async form for UI code: yields to the event loop before compiling. */
export async function loadLab(): Promise<Lab> {
  await Promise.resolve();
  return loadLabSync();
}
