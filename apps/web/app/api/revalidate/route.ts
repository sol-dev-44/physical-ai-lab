import { RunId } from "@lab/schema";
import { revalidateTag } from "next/cache";
import { type NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { runTag } from "@/lib/data/runs";

const Body = z.object({ run_ids: z.array(RunId).min(1).max(100) });

/**
 * Called by the lab-agent sync after it publishes runs, so cached pages pick
 * up the new events. Authenticated with REVALIDATE_SECRET.
 */
export async function POST(request: NextRequest) {
  const secret = process.env.REVALIDATE_SECRET;
  if (!secret || request.headers.get("authorization") !== `Bearer ${secret}`) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  const body = Body.safeParse(await request.json().catch(() => null));
  if (!body.success) return NextResponse.json({ error: "expected { run_ids: string[] }" }, { status: 400 });
  for (const id of body.data.run_ids) revalidateTag(runTag(id), "max");
  return NextResponse.json({ revalidated: body.data.run_ids });
}
