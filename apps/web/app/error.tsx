"use client";

import Link from "next/link";
import { useEffect } from "react";
import { control } from "@/lib/design/controls";

/** Fallback for any page that throws while rendering. The header stays, so the reader can move on. */
export default function PageError({ error, retry }: { error: unknown; retry: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);
  const digest = error instanceof Error && "digest" in error ? String(error.digest) : null;

  return (
    <div role="alert">
      <h1 className="text-title font-semibold">This page could not load</h1>
      <p className="mt-2 text-muted">Something failed on our side. Trying again usually works.</p>
      <div className="mt-4 flex flex-wrap items-center gap-4 text-sm">
        <button type="button" onClick={() => retry()} className={control.button}>
          Try again
        </button>
        <Link href="/" className={control.textLink}>
          Back home
        </Link>
      </div>
      {digest ? <p className="mt-4 font-mono text-xs text-muted">Error id: {digest}</p> : null}
    </div>
  );
}
