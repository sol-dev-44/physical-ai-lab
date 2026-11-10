import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { EVENT_TYPES, Event, validateLog } from "../src";

const dir = fileURLToPath(new URL("../fixtures/", import.meta.url));
const files = (sub: string) => readdirSync(join(dir, sub)).filter((f) => !f.startsWith("."));
const read = (sub: string, f: string) => readFileSync(join(dir, sub, f), "utf8");

describe("single events", () => {
  it.each(files("valid"))("accepts valid/%s", (f) => {
    const r = Event.safeParse(JSON.parse(read("valid", f)));
    expect(r.error?.issues ?? []).toEqual([]);
  });
  it.each(files("invalid"))("rejects invalid/%s", (f) => {
    expect(Event.safeParse(JSON.parse(read("invalid", f))).success).toBe(false);
  });
  it("has a valid fixture for every event type", () => {
    const covered = new Set(files("valid").map((f) => JSON.parse(read("valid", f)).type));
    expect([...covered].sort()).toEqual([...EVENT_TYPES].sort());
  });
});

describe("logs", () => {
  const lines = (sub: string, f: string) => read(`logs/${sub}`, f).split("\n");
  it.each(files("logs/valid"))("accepts logs/valid/%s", (f) => {
    expect(validateLog(lines("valid", f))).toEqual([]);
  });
  it.each(files("logs/invalid"))("rejects logs/invalid/%s", (f) => {
    expect(validateLog(lines("invalid", f)).length).toBeGreaterThan(0);
  });
});
