"use client";

import { type ErrorInfo, catchError } from "next/error";

/**
 * Keeps one broken run (a stored event that no longer matches the contract, a failed read)
 * from taking down the whole write-up around it.
 */
function RunFallback({ runId }: { runId: string }, { retry }: ErrorInfo) {
  return (
    <p role="alert" className="rounded border border-line p-4 text-sm text-muted">
      Results for <code>{runId}</code> could not load.{" "}
      <button type="button" onClick={() => retry()} className="underline">
        Try again
      </button>
    </p>
  );
}

export const RunBoundary = catchError(RunFallback);
