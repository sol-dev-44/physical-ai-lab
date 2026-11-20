import Link from "next/link";
import { StatusBadge } from "@/components/ui/status-badge";
import type { BuildData } from "@/lib/builds/data";
import { heroStats, sentence } from "@/lib/builds/view";
import type { Entry } from "@/lib/content/loader";
import { cn } from "@/lib/design/cn";
import { formatDate } from "@/lib/format";

/** One build on the index: status, title, summary, a few headline numbers and the latest log line. */
export function BuildCard({ entry, data, featured = false }: { entry: Entry<"builds">; data: BuildData | null; featured?: boolean }) {
  const fm = entry.frontmatter;
  const stats = data ? heroStats(data).slice(0, 4) : [];
  const latest = data?.timeline.at(-1);
  return (
    <Link
      href={`/builds/${entry.slug}`}
      className={cn(
        "group relative isolate flex h-full flex-col overflow-hidden rounded-card border border-line bg-surface shadow-card",
        "transition duration-base ease-out-quint hover:-translate-y-0.5 hover:border-line-strong hover:shadow-lift",
      )}
    >
      <div className={cn("relative p-6", featured && "sm:p-10")}>
        <div aria-hidden className="bg-graph pointer-events-none absolute inset-0 -z-10 opacity-70" />
        <div className="flex flex-wrap items-center justify-between gap-3">
          <StatusBadge status={fm.status} />
          <p className="font-mono text-xs text-subtle">
            Started <time dateTime={fm.date}>{formatDate(fm.date)}</time>
          </p>
        </div>
        <h2 className={cn("mt-5 font-semibold tracking-tight", featured ? "text-title" : "text-xl")}>{fm.title}</h2>
        <p className={cn("mt-3 max-w-2xl text-muted", featured && "text-lg")}>{fm.summary}</p>
      </div>

      {stats.length ? (
        <ul aria-label="Key numbers" className="grid grid-cols-2 border-t border-line sm:grid-cols-4">
          {stats.map((s, i) => (
            <li
              key={s.label}
              className={cn(
                "border-line px-6 py-5",
                i % 2 === 1 && "border-l",
                i >= 2 && "border-t sm:border-t-0",
                i >= 1 && "sm:border-l",
              )}
            >
              <p className="font-mono text-xl font-semibold tracking-tight tabular-nums sm:text-2xl">{s.value}</p>
              <p className="mt-1 text-xs text-muted">{s.label}</p>
            </li>
          ))}
        </ul>
      ) : null}

      <div className={cn("flex flex-1 flex-col justify-between gap-5 border-t border-line p-6", featured && "sm:px-10")}>
        {latest ? (
          <p className="line-clamp-3 text-sm text-muted">
            <span className="font-mono text-xs text-subtle">
              Latest · <time dateTime={latest.date}>{formatDate(latest.date)}</time>
            </span>
            <br />
            {sentence(latest.text)}
          </p>
        ) : fm.parts.length ? (
          <ul className="flex flex-wrap gap-1.5" aria-label="Main hardware">
            {fm.parts.map((p) => (
              <li key={p} className="rounded-full border border-line px-2.5 py-0.5 text-xs text-muted">
                {p}
              </li>
            ))}
          </ul>
        ) : null}
        <span className="inline-flex items-center gap-1 text-sm font-medium text-accent">
          Open the build
          <span aria-hidden className="transition-transform duration-base ease-out-quint group-hover:translate-x-0.5">
            →
          </span>
        </span>
      </div>
    </Link>
  );
}
