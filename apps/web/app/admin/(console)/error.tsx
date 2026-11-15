"use client";

import { useEffect } from "react";
import { control } from "@/lib/design/controls";

/**
 * Shown when an admin read or action fails (Supabase down, a refused query, a run that
 * would not update). In production the server message is replaced by a digest; match it
 * against the server logs.
 */
export default function AdminError({ error, retry }: { error: unknown; retry: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);
  const digest = error instanceof Error && "digest" in error ? String(error.digest) : null;
  const message = error instanceof Error && process.env.NODE_ENV !== "production" ? error.message : null;

  return (
    <div role="alert" className="space-y-3 text-sm">
      <h2 className="text-lg font-semibold">The admin console could not load</h2>
      <p className="text-muted">A Supabase read or update failed. Reload the console before trying the action again.</p>
      {message ? <p className="font-mono text-danger">{message}</p> : null}
      {digest ? <p className="font-mono text-muted">Error id: {digest}</p> : null}
      <button type="button" onClick={() => retry()} className={control.button}>
        Try again
      </button>
    </div>
  );
}
