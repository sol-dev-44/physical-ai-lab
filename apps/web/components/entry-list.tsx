import Link from "next/link";
import type { CollectionName } from "@/lib/content/collections";
import type { Entry } from "@/lib/content/loader";

const routes: Record<CollectionName, string> = { experiments: "/experiments", log: "/log", builds: "/builds" };

export function EntryList<C extends CollectionName>({ entries, empty }: { entries: Entry<C>[]; empty: string }) {
  if (entries.length === 0) return <p className="text-muted">{empty}</p>;
  return (
    <ul className="divide-y divide-line">
      {entries.map((e) => (
        <li key={e.slug} className="py-3">
          <Link href={`${routes[e.collection]}/${e.slug}`} prefetch={true} className="font-medium hover:text-accent">
            {e.frontmatter.title}
          </Link>
          <div className="text-sm text-muted">
            <time dateTime={e.frontmatter.date}>{e.frontmatter.date}</time>
            {"status" in e.frontmatter ? ` · ${e.frontmatter.status}` : null}
            {e.frontmatter.draft ? " · draft" : null}
          </div>
          <p className="text-sm">{e.frontmatter.summary}</p>
        </li>
      ))}
    </ul>
  );
}
