import { RevealItem, RevealList } from "@/components/motion/reveal";
import { Badge } from "@/components/ui/badge";
import type { BuildData } from "@/lib/builds/data";
import { cn } from "@/lib/design/cn";

type Phase = BuildData["phases"][number];

const tracks: { id: Phase["track"]; title: string; intro: string }[] = [
  { id: "v1", title: "v1 · the rolling robot", intro: "Drive, talk, recognise, remember, keep the rules." },
  { id: "v2", title: "v2 · an arm on the deck", intro: "Pick up light toys and put them away." },
];

/**
 * The phases in two tracks, with each phase's pass test. `current` lists the phase numbers in
 * progress; earlier phases count as done, later ones as ahead.
 */
export function Roadmap({ phases, current }: { phases: Phase[]; current: number[] }) {
  // Nothing in progress: nothing counts as done.
  const first = current.length ? Math.min(...current) : -1;
  const next = phases.find((p) => p.n > Math.max(...current, -1))?.n;
  return (
    <div className="space-y-12">
      {tracks.map((t) => {
        const rows = phases.filter((p) => p.track === t.id);
        if (!rows.length) return null;
        return (
          <div key={t.id}>
            <div className="mb-5 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
              <h3 className="text-lg font-semibold tracking-tight">{t.title}</h3>
              <p className="text-sm text-muted">{t.intro}</p>
            </div>
            <RevealList className="relative space-y-3 before:absolute before:top-4 before:bottom-4 before:left-[1.1875rem] before:w-px before:bg-line-strong">
              {rows.map((p) => {
                const now = current.includes(p.n);
                const done = p.n < first;
                return (
                  <RevealItem key={p.n} className="relative grid grid-cols-[2.5rem_minmax(0,1fr)] gap-4">
                    <span
                      aria-hidden
                      className={cn(
                        "relative z-[1] mt-3 grid size-10 place-items-center rounded-full border font-mono text-sm tabular-nums",
                        now && "border-accent bg-accent-solid text-accent-contrast shadow-card",
                        done && "border-ok bg-ok-soft text-ok",
                        !now && !done && "border-line-strong bg-bg text-subtle",
                      )}
                    >
                      {p.n}
                    </span>
                    <div
                      className={cn(
                        "rounded-card border p-4 transition-colors duration-base sm:p-5",
                        now ? "border-accent/50 bg-accent-soft/40 shadow-card" : "border-line bg-surface hover:border-line-strong",
                      )}
                    >
                      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-x-4">
                        <p className={cn("font-medium", now ? "text-fg" : "text-fg/90")}>
                          <span className="sr-only">Phase {p.n}: </span>
                          {p.phase}
                        </p>
                        {now ? (
                          <Badge tone="accent" pulse>
                            Now
                          </Badge>
                        ) : done ? (
                          <Badge tone="ok">Done</Badge>
                        ) : p.n === next ? (
                          <Badge tone="info">Next</Badge>
                        ) : null}
                      </div>
                      <p className="mt-2 text-sm text-muted">
                        <span className="font-mono text-[0.6875rem] tracking-wider text-subtle uppercase">Done when </span>
                        {p.done_when}
                      </p>
                    </div>
                  </RevealItem>
                );
              })}
            </RevealList>
          </div>
        );
      })}
    </div>
  );
}
