import "server-only";

/**
 * Rows from a Supabase query, or a thrown error. A failed admin read must not look like an
 * empty table: "No runs synced yet" is the wrong answer when the query was refused.
 */
export function rowsOrThrow<T>(what: string, res: { data: unknown; error: { message: string } | null }): T[] {
  if (res.error) throw new Error(`Could not load ${what}: ${res.error.message}`);
  return (res.data ?? []) as T[];
}
