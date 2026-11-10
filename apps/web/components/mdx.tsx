import type { ReactNode } from "react";
import { Suspense } from "react";
import { RunResults } from "./run-results";

/** Components available inside MDX write-ups. Keep this list small and stable. */
function Callout({ children }: { children: ReactNode }) {
  return <aside className="not-prose my-4 border-l-2 border-accent pl-4 text-sm">{children}</aside>;
}

function Run({ id }: { id: string }) {
  return (
    <div className="not-prose my-4">
      <Suspense fallback={<p className="text-sm text-muted">Loading run {id}…</p>}>
        <RunResults runId={id} />
      </Suspense>
    </div>
  );
}

export const mdxComponents = { Callout, Run };
