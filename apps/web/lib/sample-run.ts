import "server-only";

import { readFile } from "node:fs/promises";
import path from "node:path";
import { Event } from "@lab/schema";
import { cacheLife } from "next/cache";

// A contract fixture, not a real run. Read at build time; pages using it stay static.
const SAMPLE = path.join(/*turbopackIgnore: true*/ process.cwd(), "../../packages/schema/fixtures/logs/valid/full_run.jsonl");

export async function getSampleLog(): Promise<string> {
  "use cache";
  cacheLife("max");
  return readFile(SAMPLE, "utf8");
}

export type LogLine = {
  seq: number;
  time: string;
  type: string;
  tool: string | null;
  detail: string;
  tone: "neutral" | "ok" | "danger" | "accent";
};

function describe(e: Event): Pick<LogLine, "detail" | "tone"> {
  const p = (e.payload ?? {}) as Record<string, unknown>;
  switch (e.type) {
    case "safety.checked":
      return p.decision === "deny"
        ? { detail: `denied · ${String(p.rule ?? "")}`, tone: "danger" }
        : { detail: "allowed", tone: "ok" };
    case "command.sent":
      return { detail: p.latency_ms ? `${String(p.latency_ms)} ms` : "", tone: "accent" };
    case "command.failed":
      return { detail: String(p.error ?? "failed"), tone: "danger" };
    case "outcome.observed":
      return { detail: p.success ? "success" : "no effect", tone: p.success ? "ok" : "danger" };
    case "note":
      return { detail: String(p.text ?? ""), tone: "neutral" };
    case "run.ended":
      return { detail: String(p.status ?? ""), tone: "neutral" };
    default:
      return { detail: "", tone: "neutral" };
  }
}

/** The sample run as display rows for the home page. */
export async function getSampleLines(): Promise<LogLine[]> {
  const text = await getSampleLog();
  return text
    .split("\n")
    .filter((l) => l.trim())
    .map((l) => Event.parse(JSON.parse(l)))
    .map((e) => ({
      seq: e.seq,
      time: e.ts.slice(11, 19),
      type: e.type,
      tool: "tool" in e && e.tool ? e.tool : null,
      ...describe(e),
    }));
}
