import type { EmailOtpType } from "@supabase/supabase-js";
import { type NextRequest, NextResponse } from "next/server";
import { sessionClient } from "@/lib/supabase/server";

/** Magic-link landing. Exchanges the code (PKCE) or token hash for a session cookie. */
export async function GET(request: NextRequest) {
  const { searchParams, origin } = request.nextUrl;
  const next = searchParams.get("next")?.startsWith("/admin") ? searchParams.get("next")! : "/admin";
  const supabase = await sessionClient();
  if (!supabase) return NextResponse.redirect(new URL("/admin/login?error=not-configured", origin));

  const code = searchParams.get("code");
  const tokenHash = searchParams.get("token_hash");
  const type = searchParams.get("type") as EmailOtpType | null;
  const { error } = code
    ? await supabase.auth.exchangeCodeForSession(code)
    : tokenHash && type
      ? await supabase.auth.verifyOtp({ token_hash: tokenHash, type })
      : { error: new Error("missing code") };

  return NextResponse.redirect(new URL(error ? "/admin/login?error=link" : next, origin));
}
