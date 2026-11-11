"use server";

import { RunId, ToolName } from "@lab/schema";
import { revalidatePath, revalidateTag } from "next/cache";
import { z } from "zod";
import { requireAdmin } from "@/lib/auth";
import { runTag } from "@/lib/data/runs";
import { sessionClient } from "@/lib/supabase/server";

export type ActionResult = { ok: boolean; message: string };

const CommandInput = z.object({
  tool: ToolName,
  args: z.string().transform((s, ctx) => {
    try {
      const v: unknown = JSON.parse(s || "{}");
      if (v && typeof v === "object" && !Array.isArray(v)) return v as Record<string, unknown>;
    } catch {}
    ctx.addIssue({ code: "custom", message: "args must be a JSON object" });
    return z.NEVER;
  }),
  confirmed: z.boolean(),
});

/**
 * Queue a command for the lab-agent. The website never talks to hardware:
 * it inserts a row, the agent at home claims it, runs the safety gate, and
 * logs every step. The confirmation flag is advisory; the agent re-checks.
 */
export async function requestCommand(_prev: ActionResult | null, formData: FormData): Promise<ActionResult> {
  await requireAdmin();
  const input = CommandInput.safeParse({
    tool: formData.get("tool"),
    args: formData.get("args") ?? "{}",
    confirmed: formData.get("confirmed") === "on",
  });
  if (!input.success) return { ok: false, message: input.error.issues.map((i) => i.message).join("; ") };

  const db = await sessionClient();
  if (!db) return { ok: false, message: "Supabase not configured" };
  const { data: tool } = await db.from("tools").select("requires_confirmation").eq("name", input.data.tool).maybeSingle();
  if (!tool) return { ok: false, message: `Unknown tool ${input.data.tool}. Is the lab-agent running?` };
  if (tool.requires_confirmation && !input.data.confirmed) {
    return { ok: false, message: `${input.data.tool} requires confirmation` };
  }

  // requested_by is not sent: the column defaults to auth.uid(), the role may only insert
  // (tool, args, confirmed), and the commands_queue policy checks requested_by = auth.uid().
  const { error } = await db.from("commands").insert({
    tool: input.data.tool,
    args: input.data.args,
    confirmed: input.data.confirmed,
  });
  if (error) return { ok: false, message: error.message };
  revalidatePath("/admin");
  return { ok: true, message: `Queued ${input.data.tool}` };
}

export async function setRunPublished(formData: FormData): Promise<void> {
  await requireAdmin();
  const runId = RunId.parse(formData.get("run_id"));
  const published = formData.get("published") === "true";
  const db = await sessionClient();
  if (!db) return;
  await db.from("runs").update({ published }).eq("run_id", runId);
  revalidateTag(runTag(runId), { expire: 0 });
  revalidatePath("/admin");
}
