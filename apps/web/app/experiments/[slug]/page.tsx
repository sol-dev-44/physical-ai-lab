import { Suspense } from "react";
import { RunResults } from "@/components/run-results";
import { collectionDetail } from "@/lib/content/pages";

const { generateStaticParams, generateMetadata, Detail } = collectionDetail("experiments", (entry) => {
  const fm = entry.frontmatter;
  return (
    <section className="mb-10 space-y-4">
      <dl className="grid grid-cols-[8rem_1fr] gap-y-1 text-sm">
        <dt className="text-muted">ID</dt>
        <dd className="font-mono">{fm.id}</dd>
        <dt className="text-muted">Status</dt>
        <dd>{fm.status}</dd>
        {fm.hypothesis ? (
          <>
            <dt className="text-muted">Hypothesis</dt>
            <dd>{fm.hypothesis}</dd>
          </>
        ) : null}
        {fm.hardware.length ? (
          <>
            <dt className="text-muted">Hardware</dt>
            <dd>{fm.hardware.join(", ")}</dd>
          </>
        ) : null}
        {fm.app_url ? (
          <>
            <dt className="text-muted">App</dt>
            <dd>
              <a href={fm.app_url} className="underline">
                {fm.app_url}
              </a>
            </dd>
          </>
        ) : null}
      </dl>
      {fm.runs.length ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {fm.runs.map((id) => (
            <Suspense key={id} fallback={<p className="text-sm text-muted">Loading {id}…</p>}>
              <RunResults runId={id} />
            </Suspense>
          ))}
        </div>
      ) : null}
    </section>
  );
});

export { generateMetadata, generateStaticParams };
export default Detail;
