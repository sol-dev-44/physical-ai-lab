import "server-only";

import { redirect } from "next/navigation";
import { connection } from "next/server";
import { adminEmails } from "./supabase/env";
import { sessionClient } from "./supabase/server";

export type Admin = { id: string; email: string };

/**
 * Data access layer for the admin area. Every admin page, Server Action and
 * Route Handler calls this. proxy.ts only does an optimistic redirect; this
 * is the real check, and Postgres RLS (public.is_admin()) is the last one.
 */
export async function requireAdmin(): Promise<Admin> {
  await connection(); // always per request, never prerendered
  const supabase = await sessionClient();
  if (!supabase) redirect("/admin/login?error=not-configured");
  const { data, error } = await supabase.auth.getUser();
  const email = data.user?.email?.toLowerCase();
  if (error || !data.user || !email) redirect("/admin/login");
  if (!adminEmails().has(email)) redirect("/admin/login?error=not-allowed");
  return { id: data.user.id, email };
}
