import Link from "next/link";
import { PrintButton } from "@/components/print-button";
import { Badge } from "@/components/ui/badge";
import { collectionDetail } from "@/lib/content/pages";

const { generateStaticParams, generateMetadata, Detail } = collectionDetail("research", (entry) => {
  const fm = entry.frontmatter;
  return (
    <div className="mb-12 flex flex-wrap items-center gap-x-3 gap-y-2 border-y border-line py-4 text-sm">
      {fm.status === "working-draft" ? <Badge tone="warn">Working draft</Badge> : <Badge tone="ok">Final</Badge>}
      {fm.experiments.length ? (
        <>
          <span className="text-subtle">Draws on</span>
          {fm.experiments.map((id) => (
            <Link
              key={id}
              href={`/experiments/${id}`}
              className="rounded-full border border-line px-2.5 py-0.5 font-mono text-xs text-muted hover:border-line-strong hover:text-fg"
            >
              {id}
            </Link>
          ))}
        </>
      ) : null}
      <span className="ml-auto">
        <PrintButton />
      </span>
    </div>
  );
});

export { generateMetadata, generateStaticParams };
export default Detail;
