import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { getCollection } from "@/lib/content/loader";
import { formatDate, formatMonth } from "@/lib/format";
import { Badge } from "@/components/ui/badge";

export const metadata = {
  title: "Log",
  description: "The lab's build diary, in order: wins, failures and dead ends.",
};

export default async function Page() {
  const log = await getCollection("log");
  // Entries arrive newest first; group them by month, keeping that order.
  const months = new Map<string, typeof log>();
  for (const e of log) {
    const key = e.frontmatter.date.slice(0, 7);
    months.set(key, [...(months.get(key) ?? []), e]);
  }
  return (
    <>
      <PageHeader eyebrow="Lab log" title="Build diary" intro="In order: wins, failures and dead ends." />
      {log.length === 0 ? <p className="text-muted">No entries yet.</p> : null}
      <div className="space-y-16">
        {[...months].map(([month, entries]) => (
          <section key={month} aria-labelledby={`m-${month}`} className="grid gap-6 lg:grid-cols-[12rem_1fr]">
              <h2 id={`m-${month}`} className="font-mono text-xs tracking-[0.14em] text-subtle uppercase lg:pt-6">
                {formatMonth(month)}
              </h2>
              <ol className="border-t border-line">
                {entries.map((e) => (
                  <li key={e.slug} className="border-b border-line">
                    <Link href={`/log/${e.slug}`} className="group block py-6">
                      <p className="flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-xs text-subtle">
                        <time dateTime={e.frontmatter.date}>{formatDate(e.frontmatter.date)}</time>
                        {e.frontmatter.experiment ? <span>{e.frontmatter.experiment}</span> : null}
                        {e.frontmatter.draft ? <Badge tone="warn">Draft</Badge> : null}
                      </p>
                      <p className="mt-2 text-lg font-semibold tracking-tight transition-colors duration-fast group-hover:text-accent">
                        {e.frontmatter.title}
                      </p>
                      <p className="mt-1.5 max-w-2xl text-sm text-muted">{e.frontmatter.summary}</p>
                      {e.frontmatter.tags.length ? (
                        <ul className="mt-3 flex flex-wrap gap-1.5" aria-label="Tags">
                          {e.frontmatter.tags.map((t) => (
                            <li key={t} className="rounded-full bg-surface-2 px-2 py-0.5 font-mono text-[0.6875rem] text-muted">
                              {t}
                            </li>
                          ))}
                        </ul>
                      ) : null}
                    </Link>
                  </li>
                ))}
              </ol>
          </section>
        ))}
      </div>
    </>
  );
}
