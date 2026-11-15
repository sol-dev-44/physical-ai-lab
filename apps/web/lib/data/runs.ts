import "server-only";

import { Event, type RunSummary, summarizeRun } from "@lab/schema";
import { cacheLife, cacheTag } from "next/cache";
import { publicClient } from "@/lib/supabase/public";
import { sessionClient } from "@/lib/supabase/server";
import { rowsOrThrow } from "./rows";

export const runTag = (runId: string) => `run:${runId}`;

export type PublishedRun = { runId: string; events: Event[]; summary: RunSummary };

/** `null`: not published yet (or no Supabase). `"unavailable"`: the read failed. */
export type PublishedRunResult = PublishedRun | null | "unavailable";

/**
 * Events for a published run, validated against the contract and folded into
 * a summary. Cached until the sync calls /api/revalidate for this run.
 */
export async function getPublishedRun(runId: string): Promise<PublishedRunResult> {
  "use cache";
  cacheTag(runTag(runId));

  const db = publicClient();
  if (!db) {
    cacheLife("max");
    return null;
  }
  const { data, error } = await db
    .from("events")
    .select("raw")
    .eq("run_id", runId)
    .order("seq", { ascending: true });
  if (error) {
    // Cache the failure briefly, not for the "max" lifetime: otherwise a short Supabase
    // outage (at build or at runtime) shows "not published yet" until the next sync.
    cacheLife("minutes");
    console.error(`Could not load run ${runId}: ${error.message}`);
    return "unavailable";
  }
  cacheLife("max");
  if (!data?.length) return null;

  const events = data.map((row) => Event.parse(row.raw));
  return { runId, events, summary: summarizeRun(events) };
}

export type RunRow = {
  run_id: string;
  experiment_id: string;
  status: string;
  started_at: string | null;
  published: boolean;
};

/** All runs, including unpublished. Caller must have passed requireAdmin(). */
export async function listRunsForAdmin(limit = 50): Promise<RunRow[]> {
  const db = await sessionClient();
  if (!db) return [];
  const res = await db
    .from("runs")
    .select("run_id, experiment_id, status, started_at, published")
    .order("started_at", { ascending: false })
    .limit(limit);
  return rowsOrThrow<RunRow>("runs", res);
}
