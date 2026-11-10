"use server";

import { redirect } from "next/navigation";
import { adminEmails } from "@/lib/supabase/env";
import { sessionClient } from "@/lib/supabase/server";
import { site } from "@/lib/site";

export async function sendMagicLink(formData: FormData) {
  const email = String(formData.get("email") ?? "").trim().toLowerCase();
  // Same response whether or not the email is allowed, so the form can't be used to probe.
  if (email && adminEmails().has(email)) {
    const supabase = await sessionClient();
    if (!supabase) redirect("/admin/login?error=not-configured");
    await supabase.auth.signInWithOtp({
      email,
      // Never create accounts from this form. The admin user is created once in the Supabase dashboard.
      options: { shouldCreateUser: false, emailRedirectTo: `${site.url}/auth/callback?next=/admin` },
    });
  }
  redirect("/admin/login?sent=1");
}
