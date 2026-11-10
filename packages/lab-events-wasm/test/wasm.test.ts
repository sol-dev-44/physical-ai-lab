import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { Event, summarizeRun, validateLog } from "@lab/schema";
import { describe, expect, it } from "vitest";
import { loadLabSync } from "../src";
import { generatedDir, sourceHash } from "../scripts/inputs";

const fixtures = fileURLToPath(new URL("../../schema/fixtures/", import.meta.url));
const files = (sub: string) => readdirSync(join(fixtures, sub)).filter((f) => !f.startsWith("."));
const read = (sub: string, f: string) => readFileSync(join(fixtures, sub, f), "utf8");
const lab = loadLabSync();

describe("build", () => {
  it("generated/ is built from the current Rust sources (run: pnpm --filter @lab/events-wasm wasm)", () => {
    expect(readFileSync(join(generatedDir, "SOURCE_HASH"), "utf8").trim()).toBe(sourceHash());
  });
});

describe("agrees with the zod contract", () => {
  it.each(files("valid"))("accepts valid/%s", (f) => {
    expect(lab.checkEvent(read("valid", f))).toBeNull();
  });
  it.each(files("invalid"))("rejects invalid/%s", (f) => {
    expect(Event.safeParse(JSON.parse(read("invalid", f))).success).toBe(false);
    expect(lab.checkEvent(read("invalid", f))).not.toBeNull();
  });
  it.each(files("logs/valid"))("accepts logs/valid/%s", (f) => {
    const text = read("logs/valid", f);
    expect(lab.analyze(text).issues).toEqual(validateLog(text.split("\n")));
  });
  it.each(files("logs/invalid"))("rejects logs/invalid/%s (same lines as TypeScript)", (f) => {
    const text = read("logs/invalid", f);
    const lines = (issues: { line: number }[]) => [...new Set(issues.map((i) => i.line))].sort();
    expect(lines(lab.analyze(text).issues)).toEqual(lines(validateLog(text.split("\n"))));
  });
  it.each(files("summaries"))("summary matches summaries/%s", (f) => {
    const text = read("logs/valid", f.replace(".json", ".jsonl"));
    expect(lab.analyze(text).summary).toEqual(JSON.parse(read("summaries", f)));
  });
});

describe("replay API", () => {
  const text = read("logs/valid", "full_run.jsonl");
  const events = text.split("\n").filter(Boolean).map((l) => Event.parse(JSON.parse(l)));

  it("summaryAt(n) equals the TypeScript fold of the first n events", () => {
    const run = lab.openRun(text);
    expect(run.length).toBe(events.length);
    for (let n = 0; n <= events.length; n++) {
      expect(run.summaryAt(n)).toEqual(summarizeRun(events.slice(0, n)));
    }
    run.free();
  });
  it("event(i) returns the parsed event and undefined past the end", () => {
    const run = lab.openRun(text);
    expect(run.event(0)).toEqual(events[0]);
    expect(run.event(events.length)).toBeUndefined();
    run.free();
  });
});
