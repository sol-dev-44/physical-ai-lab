import { Children, type ReactNode, isValidElement } from "react";
import { Suspense } from "react";
import { slugify } from "../lib/content/headings";
import { Figure } from "./figure";
import { HarnessDiagram } from "./harness-diagram";
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

/** Plain text of a heading's children, for its id. */
function textOf(node: ReactNode): string {
  return Children.toArray(node)
    .map((c) => (typeof c === "string" || typeof c === "number" ? String(c) : isValidElement<{ children?: ReactNode }>(c) ? textOf(c.props.children) : ""))
    .join("");
}

/** Section headings get an id and a hover anchor, so contents lists and shared links can point at them. */
function H2({ children }: { children?: ReactNode }) {
  const id = slugify(textOf(children));
  return (
    <h2 id={id} className="group scroll-mt-24">
      {children}
      <a href={`#${id}`} aria-label="Link to this section" className="ml-2 text-subtle no-underline opacity-0 transition-opacity group-hover:opacity-100 focus:opacity-100">
        #
      </a>
    </h2>
  );
}

export const mdxComponents = { Callout, Run, Figure, HarnessDiagram, h2: H2 };
