import { type NextRequest, NextResponse } from "next/server";
import { sessionClient } from "@/lib/supabase/server";

export async function POST(request: NextRequest) {
  const supabase = await sessionClient();
  await supabase?.auth.signOut();
  return NextResponse.redirect(new URL("/admin/login", request.nextUrl.origin), { status: 303 });
}
