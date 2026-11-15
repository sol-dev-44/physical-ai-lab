import type { ReactNode } from "react";
import { Suspense } from "react";
import { RunBoundary } from "./run-boundary";
import { RunResults } from "./run-results";

/** Components available inside MDX write-ups. Keep this list small and stable. */
function Callout({ children }: { children: ReactNode }) {
  return <aside className="not-prose my-8 rounded-r-control border-l-2 border-accent bg-accent-soft/60 px-5 py-4 text-sm text-fg">{children}</aside>;
}

function Run({ id }: { id: string }) {
  return (
    <div className="not-prose my-4">
      <RunBoundary runId={id}>
        <Suspense fallback={<p className="text-sm text-muted">Loading run {id}…</p>}>
          <RunResults runId={id} />
        </Suspense>
      </RunBoundary>
    </div>
  );
}

export const mdxComponents = { Callout, Run };
