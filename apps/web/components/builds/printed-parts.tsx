import { RevealItem, RevealList } from "@/components/motion/reveal";
import { Badge, type Tone } from "@/components/ui/badge";
import type { BuildData } from "@/lib/builds/data";
import { grams, printedCards, printedCount } from "@/lib/builds/view";
import { cn } from "@/lib/design/cn";
import { formatDate } from "@/lib/format";

const tones: Record<string, Tone> = { active: "ok", reserved: "info", spare: "neutral" };

/** One card per printed part: what it is, when it was printed, grams, and how it fitted. */
export function PrintedParts({ data }: { data: BuildData }) {
  const cards = printedCards(data);
  const total = cards.reduce((g, c) => g + (c.grams ?? 0), 0);
  return (
    <div>
      <RevealList className="grid gap-4 sm:grid-cols-2">
        {cards.map((c) => (
          <RevealItem
            key={c.title}
            className={cn(
              "flex flex-col rounded-card border border-line bg-surface p-5 shadow-card transition duration-base ease-out-quint hover:border-line-strong",
              c.retired && "bg-surface-2 shadow-none",
            )}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-mono text-xs text-subtle">
                  {c.qty} ×{c.material ? ` · ${c.material}` : ""}
                </p>
                <h3 className={cn("mt-1 font-semibold tracking-tight", c.retired && "text-muted")}>{c.title}</h3>
              </div>
              <Badge tone={c.retired ? "neutral" : (tones[c.status.toLowerCase()] ?? "neutral")}>
                {c.retired ? "Retired" : c.status}
              </Badge>
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-3 border-t border-line pt-4 text-sm">
              <div>
                <dt className="font-mono text-[0.6875rem] tracking-wider text-subtle uppercase">Printed</dt>
                <dd className="mt-0.5 text-fg">
                  {c.dates.length ? (
                    c.dates.map((d, i) => (
                      <span key={d}>
                        {i ? ", " : ""}
                        <time dateTime={d}>{formatDate(d)}</time>
                      </span>
                    ))
                  ) : (
                    <span className="text-subtle">Not logged</span>
                  )}
                </dd>
              </div>
              <div>
                <dt className="font-mono text-[0.6875rem] tracking-wider text-subtle uppercase">Filament</dt>
                <dd className="mt-0.5 font-mono text-fg tabular-nums">
                  {c.grams !== null ? grams(c.grams) : <span className="font-sans text-subtle">Not logged</span>}
                </dd>
              </div>
            </dl>
            <p className="mt-4 flex-1 text-sm text-muted">
              <span className="font-medium text-fg">Fit: </span>
              {c.notes}
            </p>
            {c.fixings.length ? (
              <ul className="mt-3 flex flex-wrap gap-1.5" aria-label="Fixings">
                {c.fixings.map((f) => (
                  <li key={f} className="rounded-full border border-line px-2.5 py-0.5 text-xs text-muted">
                    {f}
                  </li>
                ))}
              </ul>
            ) : null}
          </RevealItem>
        ))}
      </RevealList>
      <p className="mt-4 text-sm text-subtle">
        {printedCount(data)} parts,{" "}
        <span className="font-mono tabular-nums">{grams(total)}</span> of filament in all, from the usage log.
      </p>
    </div>
  );
}
