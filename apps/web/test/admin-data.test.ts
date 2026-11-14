/**
 * Admin reads must not turn a failed Supabase query into an empty list: "No runs synced yet"
 * or "Start the lab-agent" would send the admin chasing the wrong problem.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";

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
vi.mock("@/lib/supabase/public", () => ({ publicClient: () => null }));
vi.mock("@/lib/supabase/server", () => ({
  sessionClient: async () => (configured ? { from: () => query() } : null),
}));

const { listTools, listRecentCommands } = await import("../lib/data/commands");
const { listRunsForAdmin } = await import("../lib/data/runs");

const reads = { listTools, listRecentCommands, listRunsForAdmin };

beforeEach(() => {
  configured = true;
  result = { data: [], error: null };
});

describe.each(Object.entries(reads))("%s", (_name, read) => {
  it("returns the rows", async () => {
    result = { data: [{ x: 1 }], error: null };
    await expect(read()).resolves.toEqual([{ x: 1 }]);
  });

  it("throws when the query fails instead of returning an empty list", async () => {
    result = { data: null, error: { message: "permission denied" } };
    await expect(read()).rejects.toThrow(/permission denied/);
  });

  it("returns an empty list when Supabase is not configured", async () => {
    configured = false;
    await expect(read()).resolves.toEqual([]);
  });
});
