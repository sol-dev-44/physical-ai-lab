import { Suspense } from "react";
import { RunBoundary } from "@/components/run-boundary";
import { RunResults } from "@/components/run-results";
import { StatusBadge } from "@/components/ui/status-badge";
import { collectionDetail } from "@/lib/content/pages";

const { generateStaticParams, generateMetadata, Detail } = collectionDetail("experiments", (entry) => {
  const fm = entry.frontmatter;
  return (
    <section className="mb-12 space-y-6">
      <dl className="grid gap-x-6 gap-y-4 rounded-card border border-line bg-surface p-6 text-sm shadow-card sm:grid-cols-[7rem_1fr]">
        <dt className="font-mono text-xs tracking-wider text-subtle uppercase sm:pt-0.5">Status</dt>
        <dd>
          <StatusBadge status={fm.status} />
        </dd>
        {fm.hypothesis ? (
          <>
            <dt className="font-mono text-xs tracking-wider text-subtle uppercase sm:pt-0.5">Hypothesis</dt>
            <dd className="text-fg">{fm.hypothesis}</dd>
          </>
        ) : null}
        {fm.hardware.length ? (
          <>
            <dt className="font-mono text-xs tracking-wider text-subtle uppercase sm:pt-0.5">Hardware</dt>
            <dd>
              <ul className="flex flex-wrap gap-1.5">
                {fm.hardware.map((h) => (
                  <li key={h} className="rounded-full border border-line px-2.5 py-0.5 text-xs text-muted">
                    {h}
                  </li>
                ))}
              </ul>
            </dd>
          </>
        ) : null}
        <dt className="font-mono text-xs tracking-wider text-subtle uppercase sm:pt-0.5">ID</dt>
        <dd className="font-mono text-muted">{fm.id}</dd>
        {fm.app_url ? (
          <>
            <dt className="font-mono text-xs tracking-wider text-subtle uppercase sm:pt-0.5">App</dt>
            <dd>
              <a href={fm.app_url} className="text-accent underline">
                {fm.app_url}
              </a>
            </dd>
          </>
        ) : null}
      </dl>
      {fm.runs.length ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {fm.runs.map((id) => (
            <RunBoundary key={id} runId={id}>
              <Suspense fallback={<p className="text-sm text-muted">Loading {id}…</p>}>
                <RunResults runId={id} />
              </Suspense>
            </RunBoundary>
          ))}
        </div>
      ) : null}
    </section>
  );
});

export { generateMetadata, generateStaticParams };
export default Detail;
