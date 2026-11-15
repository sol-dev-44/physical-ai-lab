import Link from "next/link";
import type { Entry } from "@/lib/content/loader";
import { cn } from "@/lib/design/cn";
import { StatusBadge } from "./ui/status-badge";

/** One experiment as a linked card: id, status, title, summary, hardware. */
export function ExperimentCard({
  entry,
  featured = false,
  headingLevel = 3,
}: {
  entry: Entry<"experiments">;
  featured?: boolean;
  /** Pick the level that fits the page's outline: 2 under the page title, 3 under a section heading. */
  headingLevel?: 2 | 3;
}) {
  const fm = entry.frontmatter;
  const Heading = headingLevel === 2 ? "h2" : "h3";
  return (
    <Link
      href={`/experiments/${entry.slug}`}
      className={cn(
        "group flex h-full flex-col rounded-card border border-line bg-surface p-6 shadow-card",
        "transition duration-base ease-out-quint hover:-translate-y-0.5 hover:border-line-strong hover:shadow-lift",
        featured && "sm:p-8",
      )}
    >
      <div className="flex items-center justify-between gap-3">
        <span className="font-mono text-xs text-subtle">{fm.id}</span>
        <StatusBadge status={fm.status} />
      </div>
      <Heading className={cn("mt-4 font-semibold tracking-tight", featured ? "text-2xl" : "text-lg")}>{fm.title}</Heading>
      <p className="mt-2 flex-1 text-sm text-muted">{fm.summary}</p>
      {fm.hardware.length ? (
        <ul className="mt-5 flex flex-wrap gap-1.5" aria-label="Hardware">
          {fm.hardware.map((h) => (
            <li key={h} className="rounded-full border border-line px-2.5 py-0.5 text-xs text-muted">
              {h}
            </li>
          ))}
        </ul>
      ) : null}
      <span className="mt-6 inline-flex items-center gap-1 text-sm font-medium text-accent">
        Read the write-up
        <span aria-hidden className="transition-transform duration-base ease-out-quint group-hover:translate-x-0.5">
          →
        </span>
      </span>
    </Link>
  );
}
