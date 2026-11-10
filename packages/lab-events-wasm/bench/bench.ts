/**
 * TypeScript (@lab/schema, zod) vs Rust compiled to WASM (@lab/events-wasm)
 * on the two jobs the replay viewer does:
 *
 *   load:  validate a whole JSONL log and fold its summary (one pass each)
 *   scrub: summary at 100 evenly spaced positions, on an already-loaded log
 *
 * Run: pnpm --filter @lab/events-wasm bench
 * Node's V8 is the engine Chrome uses, so this approximates the browser.
 */
import { isDeepStrictEqual } from "node:util";
import { Event, summarizeRun, validateLog } from "@lab/schema";
import { loadLabSync } from "../src";
import { synthLog } from "./synth";

const SIZES = [1_000, 10_000, 100_000];
const time = (fn: () => void, reps: number) => {
  const t: number[] = [];
  for (let i = 0; i < reps; i++) {
    const s = performance.now();
    fn();
    t.push(performance.now() - s);
  }
  t.sort((a, b) => a - b);
  return t[Math.floor(t.length / 2)]!;
};
const fmt = (ms: number) => (ms < 10 ? ms.toFixed(2) : ms.toFixed(0));

const t0 = performance.now();
const lab = loadLabSync();
const initMs = performance.now() - t0;

// TypeScript load: what the site does today (runs.ts): validate, parse, fold.
const tsLoad = (text: string) => {
  const lines = text.split("\n");
  const issues = validateLog(lines);
  const events = lines.filter((l) => l.trim()).map((l) => Event.parse(JSON.parse(l)));
  return { issues, summary: summarizeRun(events) };
};

console.log(`node ${process.version}, ${process.platform}/${process.arch}; WASM instantiate ${fmt(initMs)} ms\n`);
console.log("| events | log size | load: TS | load: WASM | speedup | scrub x100: TS | scrub x100: WASM | speedup |");
console.log("|---:|---:|---:|---:|---:|---:|---:|---:|");

for (const n of SIZES) {
  const text = synthLog(n);
  const reps = n >= 100_000 ? 5 : 15;

  // Same answer from both (key order aside), or the numbers mean nothing.
  const a = tsLoad(text);
  const b = lab.analyze(text);
  if (!isDeepStrictEqual(a.summary, b.summary) || a.issues.length || b.issues.length) {
    throw new Error(`TS and WASM disagree at ${n} events`);
  }

  for (let w = 0; w < 2; w++) { tsLoad(text); lab.analyze(text); } // warm up the JIT
  const loadTs = time(() => tsLoad(text), reps);
  const loadWasm = time(() => lab.analyze(text), reps);

  const events = text.split("\n").filter(Boolean).map((l) => Event.parse(JSON.parse(l)));
  const run = lab.openRun(text);
  const marks = Array.from({ length: 100 }, (_, i) => Math.round(((i + 1) / 100) * events.length));
  const scrubTs = time(() => marks.forEach((m) => summarizeRun(events.slice(0, m))), reps);
  const scrubWasm = time(() => marks.forEach((m) => run.summaryAt(m)), reps);
  run.free();

  const mb = (Buffer.byteLength(text) / 1e6).toFixed(1);
  console.log(
    `| ${n.toLocaleString("en-US")} | ${mb} MB | ${fmt(loadTs)} ms | ${fmt(loadWasm)} ms | ${(loadTs / loadWasm).toFixed(1)}x | ` +
      `${fmt(scrubTs)} ms | ${fmt(scrubWasm)} ms | ${(scrubTs / scrubWasm).toFixed(1)}x |`,
  );
}
