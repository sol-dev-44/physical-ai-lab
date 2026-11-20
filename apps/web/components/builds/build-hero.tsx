import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Stat } from "@/components/ui/stat";
import { StatusBadge } from "@/components/ui/status-badge";
import type { BuildData } from "@/lib/builds/data";
import { heroStats } from "@/lib/builds/view";
import type { Frontmatter } from "@/lib/content/collections";
import { formatDate } from "@/lib/format";

/**
 * The top of a build page: title, status, summary, the headline numbers (computed from the
 * build's data) and the main hardware. No motion here, so it paints before hydration.
 */
export function BuildHero({ fm, data }: { fm: Frontmatter<"builds">; data: BuildData | null }) {
  const stats = data ? heroStats(data) : [];
  const updated = data?.timeline.at(-1)?.date;
  return (
    <header id="top" className="relative scroll-mt-24 pb-12 sm:pb-16">
      <div aria-hidden className="bg-graph pointer-events-none absolute -inset-x-5 -top-16 bottom-0 -z-10 sm:-inset-x-8" />
      <Link
        href="/builds"
        className="inline-flex min-h-11 items-center font-mono text-xs tracking-[0.14em] text-accent uppercase hover:underline"
      >
        ← Builds
      </Link>
      <div className="mt-3 max-w-4xl">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
          <StatusBadge status={fm.status} />
          {fm.draft ? <Badge tone="warn">Draft</Badge> : null}
          <p className="font-mono text-xs text-subtle">
            Started <time dateTime={fm.date}>{formatDate(fm.date)}</time>
            {updated && updated !== fm.date ? (
              <>
                {" · "}updated <time dateTime={updated}>{formatDate(updated)}</time>
              </>
            ) : null}
          </p>
        </div>
        <h1 className="mt-4 text-display font-semibold">{fm.title}</h1>
        <p className="mt-6 max-w-2xl text-lg text-muted">{fm.summary}</p>
      </div>

      {stats.length ? (
        <ul
          aria-label="Key numbers"
          className="mt-10 grid grid-cols-2 gap-x-6 gap-y-8 border-t border-line pt-8 sm:grid-cols-3 lg:grid-cols-5"
        >
          {stats.map((s) => (
            <li key={s.label}>
              <Stat value={s.value} label={s.label} note={s.note} />
            </li>
          ))}
        </ul>
      ) : null}

      {fm.parts.length ? (
        <div className="mt-10">
          <p className="font-mono text-xs tracking-[0.14em] text-subtle uppercase">Main hardware</p>
          <ul className="mt-3 flex flex-wrap gap-2">
            {fm.parts.map((p) => (
              <li key={p} className="rounded-full border border-line bg-surface px-3 py-1 text-sm text-muted">
                {p}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </header>
  );
}
