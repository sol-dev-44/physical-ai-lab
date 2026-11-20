import type { ReactNode } from "react";
import { cn } from "@/lib/design/cn";
import { n3, polylinePath, type Pt } from "./geometry";

/**
 * Static drafting marks: dimension lines, extension lines, leaders, centre lines and labels.
 * Plain SVG, so the drawings can stay server components. Lines are hairlines that keep their
 * pixel width at any size (`vector-effect: non-scaling-stroke`); dash patterns are then in
 * screen pixels too, which is what keeps centre lines looking the same on every drawing.
 *
 * Sizes that must read the same on every drawing (arrowheads, gaps) are given in design pixels
 * and scaled by `p`, the view's drawing units per pixel (`unitsPerPx`).
 */

const hair = { fill: "none", stroke: "currentColor", strokeWidth: 1, vectorEffect: "non-scaling-stroke" } as const;

export const DASH = {
  centre: "9 2.5 1.5 2.5",
  hidden: "3.5 2.5",
  phantom: "9 2.5 1.5 2.5 1.5 2.5",
} as const;

export function Line({
  a,
  b,
  className,
  dash,
}: {
  a: Pt;
  b: Pt;
  className?: string;
  dash?: keyof typeof DASH;
}) {
  return (
    <path
      d={polylinePath([a, b])}
      {...hair}
      strokeDasharray={dash ? DASH[dash] : undefined}
      className={className}
    />
  );
}

export function Path({ d, className, dash }: { d: string; className?: string; dash?: keyof typeof DASH }) {
  return <path d={d} {...hair} strokeDasharray={dash ? DASH[dash] : undefined} className={className} />;
}

/** A centre line (long dash, dot), in the subtle ink. */
export function CentreLine({ a, b, className }: { a: Pt; b: Pt; className?: string }) {
  return <Line a={a} b={b} dash="centre" className={cn("text-subtle", className)} />;
}

/** A filled arrowhead with its tip at `tip`, pointing along `dir`. */
export function Arrowhead({ tip, dir, p }: { tip: Pt; dir: Pt; p: number }) {
  const len = Math.hypot(dir[0], dir[1]) || 1;
  const ux = dir[0] / len;
  const uy = dir[1] / len;
  const L = 7 * p;
  const W = 2.1 * p;
  const bx = tip[0] - ux * L;
  const by = tip[1] - uy * L;
  const d = `M${n3(tip[0])} ${n3(tip[1])} L${n3(bx - uy * W)} ${n3(by + ux * W)} L${n3(bx + uy * W)} ${n3(by - ux * W)} Z`;
  return <path d={d} fill="currentColor" stroke="none" />;
}

type Anchor = "start" | "middle" | "end";
/** Where text sits relative to its point: centred on it, above it, or below it. */
type VAlign = "middle" | "above" | "below";
const dy: Record<VAlign, string> = { middle: "0.35em", above: "-0.45em", below: "1.1em" };

/**
 * Drawing text. `lines` stack downward from the first; the first line takes `tone`, later lines
 * are muted notes. Children (tspans) may replace `lines` for mixed tones on one line.
 */
export function Label({
  at,
  anchor = "start",
  v = "middle",
  lines,
  children,
  tone = "fg",
  size,
  rotate,
  className,
}: {
  at: Pt;
  anchor?: Anchor;
  v?: VAlign;
  lines?: readonly string[];
  children?: ReactNode;
  tone?: "fg" | "muted" | "subtle" | "accent";
  /** Relative size, in em of the drawing's text size. */
  size?: number;
  /** Degrees about `at` (−90 reads bottom to top, for a vertical dimension). */
  rotate?: number;
  className?: string;
}) {
  const toneClass = { fg: "fill-fg", muted: "fill-muted", subtle: "fill-subtle", accent: "fill-accent" }[tone];
  return (
    <text
      x={n3(at[0])}
      y={n3(at[1])}
      dy={dy[v]}
      textAnchor={anchor}
      fontSize={size ? `${size}em` : undefined}
      transform={rotate ? `rotate(${rotate} ${n3(at[0])} ${n3(at[1])})` : undefined}
      className={cn(toneClass, className)}
    >
      {children ??
        lines?.map((l, i) => (
          <tspan key={i} x={n3(at[0])} dy={i === 0 ? undefined : "1.25em"} className={i === 0 ? undefined : "fill-muted"}>
            {l}
          </tspan>
        ))}
    </text>
  );
}

/** A muted word after a number inside one Label: `<Num>6.45</Num><Note> web</Note>`. */
export function Note({ children }: { children: ReactNode }) {
  return <tspan className="fill-muted">{children}</tspan>;
}

/**
 * A linear dimension from `a` to `b`. `arrows`: "both" (tips on a and b, pointing out), "end"
 * (one tip on b: a radius or a half-section diameter, the line starting past the centre line),
 * "outside" (for spans too small for arrows between the lines: arrows point in from outside).
 * Extension lines are separate (`ext`), each from just off the part to just past the line.
 */
export function Dim({
  a,
  b,
  p,
  arrows = "both",
  ext = [],
  label,
  at,
  anchor = "middle",
  v = "above",
  rotate,
}: {
  a: Pt;
  b: Pt;
  p: number;
  arrows?: "both" | "end" | "outside";
  ext?: readonly (readonly [Pt, Pt])[];
  /** Omit to place the label separately (multi-line notes). */
  label?: ReactNode;
  /** Label position; the midpoint by default. */
  at?: Pt;
  anchor?: Anchor;
  v?: VAlign;
  rotate?: number;
}) {
  const dx = b[0] - a[0];
  const dy2 = b[1] - a[1];
  const len = Math.hypot(dx, dy2) || 1;
  const u: Pt = [dx / len, dy2 / len];
  const back: Pt = [-u[0], -u[1]];
  const tail = 11 * p;
  const line: [Pt, Pt] =
    arrows === "outside"
      ? [
          [a[0] - u[0] * tail, a[1] - u[1] * tail],
          [b[0] + u[0] * tail, b[1] + u[1] * tail],
        ]
      : [a, b];
  const mid: Pt = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  return (
    <g className="text-muted">
      {ext.map(([e0, e1], i) => (
        <Line key={i} a={e0} b={e1} className="opacity-80" />
      ))}
      <Line a={line[0]} b={line[1]} />
      {arrows === "both" ? (
        <>
          <Arrowhead tip={a} dir={back} p={p} />
          <Arrowhead tip={b} dir={u} p={p} />
        </>
      ) : null}
      {arrows === "end" ? <Arrowhead tip={b} dir={u} p={p} /> : null}
      {arrows === "outside" ? (
        <>
          <Arrowhead tip={a} dir={u} p={p} />
          <Arrowhead tip={b} dir={back} p={p} />
        </>
      ) : null}
      {label != null ? (
        <Label at={at ?? mid} anchor={anchor} v={v} rotate={rotate}>
          {label}
        </Label>
      ) : null}
    </g>
  );
}

/**
 * A leader: a hairline from a label to a feature, with an arrowhead on the feature (`tip`, the
 * first point) or a dot when it points into a surface rather than at an edge.
 */
export function Leader({ points, p, end = "arrow" }: { points: readonly Pt[]; p: number; end?: "arrow" | "dot" }) {
  const [tip, next] = points;
  if (!tip || !next) return null;
  return (
    <g className="text-muted">
      <path d={polylinePath(points)} {...hair} />
      {end === "arrow" ? (
        <Arrowhead tip={tip} dir={[tip[0] - next[0], tip[1] - next[1]]} p={p} />
      ) : (
        <circle cx={n3(tip[0])} cy={n3(tip[1])} r={n3(1.6 * p)} fill="currentColor" />
      )}
    </g>
  );
}

/** A detail callout on the main view: a dashed circle round the area and its letter. */
export function DetailMark({ c, r, letter, at }: { c: Pt; r: number; letter: string; at: Pt }) {
  return (
    <g className="text-subtle">
      <circle cx={n3(c[0])} cy={n3(c[1])} r={n3(r)} {...hair} strokeDasharray={DASH.hidden} />
      <Label at={at} anchor="middle" tone="fg" className="font-semibold">
        {letter}
      </Label>
    </g>
  );
}
