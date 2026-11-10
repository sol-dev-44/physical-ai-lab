import "server-only";

import { type SupabaseClient, createClient } from "@supabase/supabase-js";
import { supabaseEnv } from "./env";

/**
 * Anonymous client with no session. Safe inside 'use cache' because it never
 * reads the request. Row-level security limits it to published runs.
 */
export function publicClient(): SupabaseClient | null {
  const env = supabaseEnv();
  if (!env) return null;
  return createClient(env.url, env.anonKey, { auth: { persistSession: false, autoRefreshToken: false } });
}
