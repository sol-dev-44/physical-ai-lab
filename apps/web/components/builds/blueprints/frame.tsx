import type { CSSProperties, ReactNode } from "react";
import type { BuildData } from "@/lib/builds/data";
import { cn } from "@/lib/design/cn";

export type LegendSwatch = "section" | "solid" | "part" | "context" | "hidden" | "centre" | "mass";
export type LegendItem = { swatch: LegendSwatch; label: string };

/** Faint drafting paper: a fine grid with a stronger line every fifth square. */
const paper: CSSProperties = {
  backgroundImage: [
    "linear-gradient(to right, color-mix(in oklab, var(--line) 85%, transparent) 1px, transparent 1px)",
    "linear-gradient(to bottom, color-mix(in oklab, var(--line) 85%, transparent) 1px, transparent 1px)",
    "linear-gradient(to right, color-mix(in oklab, var(--line) 45%, transparent) 1px, transparent 1px)",
    "linear-gradient(to bottom, color-mix(in oklab, var(--line) 45%, transparent) 1px, transparent 1px)",
  ].join(", "),
  backgroundSize: "80px 80px, 80px 80px, 16px 16px, 16px 16px",
  backgroundPosition: "-1px -1px",
};

/** Outlines are drawn with stroke dashes; without JavaScript, show them whole (the layout's own
 *  noscript rule covers `[data-reveal]` opacity). */
const NOSCRIPT_CSS = "[data-draw]{stroke-dasharray:none!important;opacity:1!important}";

/**
 * The sheet a drawing sits on: a card with drafting paper behind the views, an optional toolbar
 * above them, then a legend or notes and an engineering title block (part, units, scale, source).
 * Put one or more `BlueprintView`s in `children`.
 */
export function BlueprintFrame({
  data,
  title,
  scale,
  sheet,
  legend,
  notes,
  toolbar,
  caption,
  className,
  children,
}: {
  data: BuildData;
  /** Part name for the title block. */
  title: string;
  /** Scale note, e.g. "1 : 1 · details 3 : 1". */
  scale: string;
  /** Sheet number, e.g. "1 / 3". */
  sheet?: string;
  legend?: readonly LegendItem[];
  notes?: readonly ReactNode[];
  /** Controls above the drawing (BasePlan's centre-of-mass toggle). */
  toolbar?: ReactNode;
  caption?: ReactNode;
  className?: string;
  children: ReactNode;
}) {
  return (
    <figure className={cn("overflow-hidden rounded-card border border-line bg-surface shadow-card", className)}>
      <noscript>
        <style>{NOSCRIPT_CSS}</style>
      </noscript>
      {toolbar ? <div className="border-b border-line px-4 py-3 sm:px-6">{toolbar}</div> : null}

      <div className="relative px-3 py-6 sm:px-6 sm:py-8">
        <div aria-hidden className="pointer-events-none absolute inset-0 opacity-70" style={paper} />
        <div className="relative">{children}</div>
      </div>

      <div className="grid border-t border-line md:grid-cols-[minmax(0,1fr)_minmax(0,20rem)]">
        <div className="px-4 py-4 sm:px-6">
          {legend && legend.length > 0 ? <Legend items={legend} /> : null}
          {notes && notes.length > 0 ? (
            <ol
              className={cn(
                "space-y-1.5 text-xs leading-relaxed text-muted",
                legend && legend.length > 0 && "mt-4 border-t border-line pt-4",
              )}
            >
              {notes.map((n, i) => (
                <li key={i} className="flex gap-2.5">
                  <span className="font-mono text-subtle tabular-nums">{i + 1}.</span>
                  <span>{n}</span>
                </li>
              ))}
            </ol>
          ) : null}
        </div>
        <TitleBlock title={title} scale={scale} sheet={sheet} source={data.source} />
      </div>

      {caption ? (
        <figcaption className="border-t border-line px-4 py-3 text-sm leading-relaxed text-muted sm:px-6">
          {caption}
        </figcaption>
      ) : null}
    </figure>
  );
}

function Cell({ label, children, className }: { label: string; children: ReactNode; className?: string }) {
  return (
    <div className={cn("min-w-0 px-3 py-2", className)}>
      <dt className="font-mono text-[0.625rem] tracking-[0.14em] text-subtle uppercase">{label}</dt>
      <dd className="mt-0.5">{children}</dd>
    </div>
  );
}

function TitleBlock({ title, scale, sheet, source }: { title: string; scale: string; sheet?: string; source: string }) {
  return (
    <dl className="grid grid-cols-[minmax(0,1fr)_auto] border-t border-line text-sm md:border-t-0 md:border-l">
      <Cell label="Part" className={cn("border-b border-line", sheet ? "border-r" : "col-span-2")}>
        <span className="font-semibold">{title}</span>
      </Cell>
      {sheet ? (
        <Cell label="Sheet" className="border-b border-line">
          <span className="font-mono tabular-nums">{sheet}</span>
        </Cell>
      ) : null}
      <Cell label="Scale" className="border-r border-b border-line">
        <span className="font-mono text-xs">{scale}</span>
      </Cell>
      <Cell label="Units" className="border-b border-line">
        <span className="font-mono text-xs">mm</span>
      </Cell>
      <Cell label="Source" className="col-span-2">
        <code className="font-mono text-[0.6875rem] break-all text-muted">{source}</code>
      </Cell>
    </dl>
  );
}

function Legend({ items }: { items: readonly LegendItem[] }) {
  return (
    <ul className="flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted">
      {items.map((it) => (
        <li key={it.label} className="inline-flex items-center gap-2">
          <Swatch kind={it.swatch} />
          {it.label}
        </li>
      ))}
    </ul>
  );
}

function Swatch({ kind }: { kind: LegendSwatch }) {
  const box = "h-3 w-5 shrink-0 rounded-[2px]";
  switch (kind) {
    case "section":
      return (
        <span
          aria-hidden
          className={cn(box, "border border-accent bg-accent-soft text-accent")}
          style={{ backgroundImage: "repeating-linear-gradient(-45deg, currentColor 0 1px, transparent 1px 4px)" }}
        />
      );
    case "solid":
      return <span aria-hidden className={cn(box, "border border-fg bg-fg/70 dark:bg-fg/40")} />;
    case "part":
      return <span aria-hidden className={cn(box, "border-[1.5px] border-accent bg-accent-soft")} />;
    case "context":
      return <span aria-hidden className={cn(box, "border border-dashed border-muted bg-surface-2")} />;
    case "hidden":
    case "centre":
      return (
        <svg aria-hidden viewBox="0 0 20 12" className="h-3 w-5 shrink-0 text-muted">
          <path
            d="M0 6 H20"
            stroke="currentColor"
            strokeWidth={1}
            strokeDasharray={kind === "hidden" ? "3.5 2.5" : "9 2.5 1.5 2.5"}
          />
        </svg>
      );
    case "mass":
      return (
        <svg aria-hidden viewBox="0 0 12 12" className="size-3 shrink-0 text-fg">
          <MassSymbolPaths cx={6} cy={6} r={5} />
        </svg>
      );
  }
}

/** The centre-of-mass symbol: a circle with opposite quarters filled. */
export function MassSymbolPaths({ cx, cy, r }: { cx: number; cy: number; r: number }) {
  return (
    <>
      <circle cx={cx} cy={cy} r={r} className="fill-surface" stroke="currentColor" strokeWidth={1} vectorEffect="non-scaling-stroke" />
      <path d={`M${cx} ${cy} L${cx + r} ${cy} A${r} ${r} 0 0 1 ${cx} ${cy + r} Z`} fill="currentColor" />
      <path d={`M${cx} ${cy} L${cx - r} ${cy} A${r} ${r} 0 0 1 ${cx} ${cy - r} Z`} fill="currentColor" />
    </>
  );
}
