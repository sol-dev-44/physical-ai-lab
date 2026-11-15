import Link from "next/link";
import type { CollectionName } from "@/lib/content/collections";
import type { Entry } from "@/lib/content/loader";
import { formatDate } from "@/lib/format";
import { Badge } from "./ui/badge";

const routes: Record<CollectionName, string> = {
  experiments: "/experiments",
  log: "/log",
  builds: "/builds",
  research: "/research",
};

/** A dated list of write-ups: date in its own column from `sm` up. */
export function EntryList<C extends CollectionName>({ entries, empty }: { entries: Entry<C>[]; empty: string }) {
  if (entries.length === 0) return <p className="text-muted">{empty}</p>;
  return (
    <ul className="border-t border-line">
      {entries.map((e) => (
        <li key={e.slug} className="border-b border-line">
          <Link
            href={`${routes[e.collection]}/${e.slug}`}
            className="group grid gap-x-8 gap-y-1 py-5 sm:grid-cols-[9rem_1fr]"
          >
            <time dateTime={e.frontmatter.date} className="pt-0.5 font-mono text-xs text-subtle">
              {formatDate(e.frontmatter.date)}
            </time>
            <div>
              <p className="font-medium tracking-tight transition-colors duration-fast group-hover:text-accent">
                {e.frontmatter.title}
                {e.frontmatter.draft ? (
                  <Badge tone="warn" className="ml-2 align-middle">
                    Draft
                  </Badge>
                ) : null}
              </p>
              <p className="mt-1 text-sm text-muted">{e.frontmatter.summary}</p>
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}
