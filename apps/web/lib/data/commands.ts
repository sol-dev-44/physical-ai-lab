import "server-only";

import { sessionClient } from "@/lib/supabase/server";

export type ToolRow = { name: string; description: string; requires_confirmation: boolean; args_schema: unknown };
export type CommandRow = {
  id: string;
  tool: string;
  args: Record<string, unknown>;
  status: "pending" | "claimed" | "done" | "rejected" | "failed" | "expired";
  created_at: string;
  result: string | null;
};

/** Tools the lab-agent registered on startup. Caller must have passed requireAdmin(). */
export async function listTools(): Promise<ToolRow[]> {
  const db = await sessionClient();
  if (!db) return [];
  const { data } = await db.from("tools").select("name, description, requires_confirmation, args_schema").order("name");
  return (data ?? []) as ToolRow[];
}

export async function listRecentCommands(limit = 20): Promise<CommandRow[]> {
  const db = await sessionClient();
  if (!db) return [];
  const { data } = await db
    .from("commands")
    .select("id, tool, args, status, created_at, result")
    .order("created_at", { ascending: false })
    .limit(limit);
  return (data ?? []) as CommandRow[];
}
