import "server-only";

import { Event, type RunSummary, summarizeRun } from "@lab/schema";
import { cacheLife, cacheTag } from "next/cache";
import { publicClient } from "@/lib/supabase/public";
import { sessionClient } from "@/lib/supabase/server";

export const runTag = (runId: string) => `run:${runId}`;

export type PublishedRun = { runId: string; events: Event[]; summary: RunSummary };

/**
 * Events for a published run, validated against the contract and folded into
 * a summary. Cached until the sync calls /api/revalidate for this run.
 */
export async function getPublishedRun(runId: string): Promise<PublishedRun | null> {
  "use cache";
  cacheTag(runTag(runId));
  cacheLife("max");

  const db = publicClient();
  if (!db) return null;
  const { data, error } = await db
    .from("events")
    .select("raw")
    .eq("run_id", runId)
    .order("seq", { ascending: true });
  if (error || !data?.length) return null;

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
  const { data } = await db
    .from("runs")
    .select("run_id, experiment_id, status, started_at, published")
    .order("started_at", { ascending: false })
    .limit(limit);
  return (data ?? []) as RunRow[];
}
