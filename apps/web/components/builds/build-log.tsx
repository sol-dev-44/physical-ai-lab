import { RevealItem, RevealList } from "@/components/motion/reveal";
import type { BuildData } from "@/lib/builds/data";
import { groupByDate, sentence } from "@/lib/builds/view";
import { formatDate } from "@/lib/format";

/** The progress log as a vertical timeline, one group per day, entries in the order they happened. */
export function BuildLog({ timeline }: { timeline: BuildData["timeline"] }) {
  const days = groupByDate(timeline);
  return (
    <RevealList className="relative space-y-10">
      {days.map((d) => (
        <RevealItem key={d.date} className="relative grid gap-4 md:grid-cols-[9rem_minmax(0,1fr)] md:gap-8">
          <div className="md:sticky md:top-24 md:self-start">
            <p className="font-mono text-xs tracking-[0.14em] text-accent uppercase">Day {d.day}</p>
            <time dateTime={d.date} className="mt-1 block font-semibold tracking-tight">
              {formatDate(d.date)}
            </time>
            <p className="mt-0.5 text-xs text-subtle">
              {d.items.length} {d.items.length === 1 ? "entry" : "entries"}
            </p>
          </div>
          <ol className="relative border-l border-line-strong">
            {d.items.map((e, i) => (
              <li key={i} className="relative pb-6 pl-6 last:pb-0">
                <span
                  aria-hidden
                  className="absolute top-2 -left-[5px] size-[9px] rounded-full border-2 border-bg bg-accent-solid ring-1 ring-line-strong"
                />
                <p className="max-w-prose text-[0.9375rem] leading-relaxed text-fg">{sentence(e.text)}</p>
              </li>
            ))}
          </ol>
        </RevealItem>
      ))}
    </RevealList>
  );
}
