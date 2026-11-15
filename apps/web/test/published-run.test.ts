/**
 * A failed Supabase read must not be cached for the "max" lifetime as "not published yet":
 * a short outage would hide the run until the next sync revalidates it.
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { cacheLife } from "next/cache";
import { beforeEach, expect, it, vi } from "vitest";

type Result = { data: unknown; error: { message: string } | null };
let result: Result;
let configured = true;

// Any chain of query-builder calls resolves to `result`.
function query(): unknown {
  const target = () => undefined;
  return new Proxy(target, {
    get: (_t, prop) => (prop === "then" ? (ok: (r: Result) => void) => ok(result) : () => query()),
  });
}

vi.mock("server-only", () => ({}));
vi.mock("next/cache", () => ({ cacheLife: vi.fn(), cacheTag: vi.fn() }));
vi.mock("@/lib/supabase/public", () => ({ publicClient: () => (configured ? { from: () => query() } : null) }));
vi.mock("@/lib/supabase/server", () => ({ sessionClient: async () => null }));

const { getPublishedRun } = await import("../lib/data/runs");

const fixture = path.join(__dirname, "../../../packages/schema/fixtures/logs/valid/full_run.jsonl");
const rows = readFileSync(fixture, "utf8")
  .split("\n")
  .filter((l) => l.trim())
  .map((l) => ({ raw: JSON.parse(l) }));

beforeEach(() => {
  configured = true;
  result = { data: [], error: null };
  vi.mocked(cacheLife).mockClear();
  vi.spyOn(console, "error").mockImplementation(() => {});
});

it("returns the run and caches it for the max lifetime", async () => {
  result = { data: rows, error: null };
  const run = await getPublishedRun("r1");
  expect(run).toMatchObject({ runId: "r1", events: { length: rows.length } });
  expect(cacheLife).toHaveBeenCalledExactlyOnceWith("max");
});

it("returns null for a run with no published events", async () => {
  await expect(getPublishedRun("r1")).resolves.toBeNull();
  expect(cacheLife).toHaveBeenCalledExactlyOnceWith("max");
});

it("reports a failed read as unavailable and caches it only briefly", async () => {
  result = { data: null, error: { message: "upstream timeout" } };
  await expect(getPublishedRun("r1")).resolves.toBe("unavailable");
  expect(cacheLife).toHaveBeenCalledExactlyOnceWith("minutes");
});

it("returns null when Supabase is not configured", async () => {
  configured = false;
  await expect(getPublishedRun("r1")).resolves.toBeNull();
});
