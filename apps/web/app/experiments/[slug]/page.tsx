import { Suspense } from "react";
import { RunBoundary } from "@/components/run-boundary";
import { RunResults } from "@/components/run-results";
import { ExperimentGlyph } from "@/components/experiment-glyph";
import { StatusBadge } from "@/components/ui/status-badge";
import { EntryList } from "@/components/entry-list";
import { getCollection } from "@/lib/content/loader";
import { collectionDetail } from "@/lib/content/pages";

const { generateStaticParams, generateMetadata, Detail } = collectionDetail("experiments", (entry) => {
  const fm = entry.frontmatter;
  return (
    <section className="mb-12 space-y-6">
      <div aria-hidden className="flex items-end justify-between border-b border-line pb-4">
        <ExperimentGlyph id={fm.id} className="size-16 text-accent" />
        <span className="font-mono text-6xl font-semibold tracking-tighter text-line-strong tabular-nums">
          {fm.id.slice(3, 6)}
        </span>
      </div>
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
}, (entry) => <RelatedLog experimentId={entry.frontmatter.id} />);

/** Log entries that name this experiment in their front matter. */
async function RelatedLog({ experimentId }: { experimentId: string }) {
  const log = (await getCollection("log")).filter((e) => e.frontmatter.experiment === experimentId);
  if (!log.length) return null;
  return (
    <section className="mt-16">
      <h2 className="mb-4 font-mono text-xs tracking-[0.14em] text-subtle uppercase">From the lab log</h2>
      <EntryList entries={log} empty="" />
    </section>
  );
}

export { generateMetadata, generateStaticParams };
export default Detail;
