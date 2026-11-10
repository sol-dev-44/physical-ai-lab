"use client";

import { useRef, useState } from "react";
import type { RunSummary } from "@lab/schema";
import { type EngineName, type OpenRun, getEngine } from "@/lib/replay/engines";

type Loaded = { name: string; text: string; run: OpenRun; engine: EngineName; ms: number };
type Timing = Record<EngineName, number>;

const pct = (n: number | null) => (n === null ? "n/a" : `${Math.round(n * 100)}%`);
const ms = (n: number) => (n < 10 ? n.toFixed(2) : n.toFixed(0));

async function open(engine: EngineName, text: string) {
  const e = await getEngine(engine);
  const t = performance.now();
  const run = e.open(text);
  return { run, ms: performance.now() - t };
}

/** Load a JSONL run log and step through it. Everything runs in the browser; nothing is uploaded. */
export function ReplayViewer({ sample }: { sample: string }) {
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const [pos, setPos] = useState(0);
  const [engine, setEngine] = useState<EngineName>("ts");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timing, setTiming] = useState<Timing | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  async function load(name: string, text: string, using: EngineName = engine) {
    setBusy(true);
    setError(null);
    setTiming(null);
    try {
      const { run, ms } = await open(using, text);
      loaded?.run.free();
      setLoaded({ name, text, run, engine: using, ms });
      setPos(run.length);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function switchEngine(next: EngineName) {
    setEngine(next);
    if (loaded) await load(loaded.name, loaded.text, next);
  }

  async function compare() {
    if (!loaded) return;
    setBusy(true);
    const t: Partial<Timing> = {};
    for (const name of ["ts", "wasm"] as const) {
      const { run, ms } = await open(name, loaded.text);
      const s = performance.now();
      run.summaryAt(run.length);
      t[name] = ms + (performance.now() - s);
      run.free();
    }
    setTiming(t as Timing);
    setBusy(false);
  }

  const run = loaded?.run;
  const event = run && pos > 0 ? run.event(pos - 1) : undefined;
  const summary = run ? run.summaryAt(pos) : null;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <input
          ref={fileRef}
          type="file"
          accept=".jsonl,application/x-ndjson,text/plain"
          className="hidden"
          onChange={async (e) => {
            const f = e.target.files?.[0];
            if (f) await load(f.name, await f.text());
            e.target.value = "";
          }}
        />
        <button type="button" className="rounded border border-line px-3 py-1 hover:border-fg" onClick={() => fileRef.current?.click()} disabled={busy}>
          Open a .jsonl log
        </button>
        <button type="button" className="rounded border border-line px-3 py-1 hover:border-fg" onClick={() => load("sample (contract fixture)", sample)} disabled={busy}>
          Try the sample
        </button>
        <fieldset className="ml-auto flex items-center gap-3" disabled={busy}>
          <legend className="sr-only">Engine</legend>
          {(["ts", "wasm"] as const).map((name) => (
            <label key={name} className="flex items-center gap-1">
              <input type="radio" name="engine" checked={engine === name} onChange={() => switchEngine(name)} />
              {name === "ts" ? "TypeScript" : "Rust (WASM)"}
            </label>
          ))}
        </fieldset>
      </div>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      {run && loaded ? (
        <>
          <p className="text-sm text-muted">
            <span className="font-mono">{loaded.name}</span>: {run.length} events, {run.valid ? "valid" : `${run.issues.length} issue(s)`}. Parsed in {ms(loaded.ms)} ms
            ({loaded.engine === "ts" ? "TypeScript" : "Rust/WASM"}).{" "}
            <button type="button" className="underline" onClick={compare} disabled={busy}>
              Time both engines
            </button>
            {timing ? (
              <span className="font-mono">
                {" "}
                TS {ms(timing.ts)} ms, WASM {ms(timing.wasm)} ms
              </span>
            ) : null}
          </p>

          {run.issues.length ? (
            <ul className="rounded border border-line p-3 font-mono text-xs">
              {run.issues.slice(0, 20).map((i, k) => (
                <li key={k}>
                  {i.line ? `line ${i.line}: ` : ""}
                  {i.message}
                </li>
              ))}
              {run.issues.length > 20 ? <li>… {run.issues.length - 20} more</li> : null}
            </ul>
          ) : null}

          <div className="flex items-center gap-3">
            <button type="button" className="rounded border border-line px-2" onClick={() => setPos((p) => Math.max(0, p - 1))} aria-label="Previous event">
              ‹
            </button>
            <input
              type="range"
              min={0}
              max={run.length}
              value={pos}
              onChange={(e) => setPos(Number(e.target.value))}
              className="flex-1"
              aria-label="Position in run"
            />
            <button type="button" className="rounded border border-line px-2" onClick={() => setPos((p) => Math.min(run.length, p + 1))} aria-label="Next event">
              ›
            </button>
            <span className="w-24 text-right font-mono text-sm">
              {pos}/{run.length}
            </span>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <section className="rounded border border-line p-4">
              <h3 className="mb-2 text-sm font-semibold">Event {pos > 0 ? pos - 1 : "-"}</h3>
              {event ? (
                <>
                  <p className="font-mono text-sm">
                    {event.type}
                    {"tool" in event && event.tool ? ` ${event.tool}` : ""}
                  </p>
                  <p className="mb-2 text-xs text-muted">
                    {event.ts} · {event.actor}
                  </p>
                  <pre className="overflow-x-auto text-xs">{JSON.stringify(event.payload, null, 2)}</pre>
                </>
              ) : (
                <p className="text-sm text-muted">Start of run.</p>
              )}
            </section>
            {summary ? <SummaryTable s={summary} /> : null}
          </div>
        </>
      ) : (
        <p className="text-sm text-muted">Open a log written by the lab-agent, or try the sample.</p>
      )}
    </div>
  );
}

function SummaryTable({ s }: { s: RunSummary }) {
  const rows: [string, string | number][] = [
    ["Status", s.status + (s.null_test ? " (null test)" : "")],
    ["Requested", s.requested],
    ["Denied by safety gate", s.denied],
    ["Sent", s.sent],
    ["Failed", s.failed],
    ["Observed", s.observed],
    ["Success rate", pct(s.success_rate)],
  ];
  return (
    <section className="rounded border border-line p-4">
      <h3 className="mb-2 text-sm font-semibold">Summary so far</h3>
      <table className="w-full text-sm">
        <tbody>
          {rows.map(([k, v]) => (
            <tr key={k} className="border-t border-line first:border-0">
              <td className="py-1 text-muted">{k}</td>
              <td className="py-1 text-right font-mono">{v}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
