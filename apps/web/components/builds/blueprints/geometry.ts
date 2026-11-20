/**
 * Pure geometry for the blueprints: polygon paths, the outline of a set of touching polygons,
 * and number formatting. No React and no `@/` imports, so tests can load it directly.
 */

export type Pt = readonly [number, number];
export type Seg = readonly [Pt, Pt];
export type Map2 = (p: Pt) => Pt;

const EPS = 1e-6;
const same: Map2 = (p) => p;

/** A number for an SVG path: three decimals at most, no trailing zeros. */
export function n3(v: number): string {
  return String(Number(v.toFixed(3)));
}

/** A number for a label: two decimals at most, no trailing zeros (120, 6.45, 106.6). */
export function fmt(v: number, digits = 2): string {
  return String(Number(v.toFixed(digits)));
}

export function polygonPath(pts: readonly Pt[], to: Map2 = same): string {
  if (pts.length === 0) return "";
  return `${polylinePath(pts, to)} Z`;
}

export function polylinePath(pts: readonly Pt[], to: Map2 = same): string {
  return pts
    .map((p, i) => {
      const [x, y] = to(p);
      return `${i === 0 ? "M" : "L"}${n3(x)} ${n3(y)}`;
    })
    .join(" ");
}

/** Several closed polygons as one path (one subpath each). */
export function polygonsPath(polys: readonly (readonly Pt[])[], to: Map2 = same): string {
  return polys.map((p) => polygonPath(p, to)).join(" ");
}

/** A rectangle from two corners, as a closed path. */
export function rectPath(x0: number, y0: number, x1: number, y1: number): string {
  return polygonPath([
    [x0, y0],
    [x1, y0],
    [x1, y1],
    [x0, y1],
  ]);
}

const near = (a: Pt, b: Pt) => Math.abs(a[0] - b[0]) < EPS && Math.abs(a[1] - b[1]) < EPS;

/**
 * The outline of a region exported as several polygons that touch along shared edges (the hub
 * section comes as one polygon per solid strip). Edges, or parts of edges, that two polygons share
 * are inside the region and dropped; what is left is the boundary, as separate segments.
 */
export function unionBoundary(polys: readonly (readonly Pt[])[]): Seg[] {
  const edges = polys.flatMap((poly, i) =>
    poly.map((a, k) => ({ i, a, b: poly[(k + 1) % poly.length] ?? a })),
  );
  const out: Seg[] = [];
  for (const e of edges) {
    const dx = e.b[0] - e.a[0];
    const dy = e.b[1] - e.a[1];
    const len2 = dx * dx + dy * dy;
    if (len2 < EPS) continue;
    const len = Math.sqrt(len2);
    const covered: [number, number][] = [];
    for (const o of edges) {
      if (o.i === e.i) continue;
      // Collinear: both ends of the other edge lie on this edge's line.
      const off = (p: Pt) => Math.abs(dx * (p[1] - e.a[1]) - dy * (p[0] - e.a[0])) / len;
      if (off(o.a) > EPS || off(o.b) > EPS) continue;
      const t = (p: Pt) => (dx * (p[0] - e.a[0]) + dy * (p[1] - e.a[1])) / len2;
      const lo = Math.max(0, Math.min(t(o.a), t(o.b)));
      const hi = Math.min(1, Math.max(t(o.a), t(o.b)));
      if (hi - lo > EPS) covered.push([lo, hi]);
    }
    covered.sort((x, y) => x[0] - y[0]);
    const at = (s: number): Pt => [e.a[0] + dx * s, e.a[1] + dy * s];
    let s = 0;
    for (const [lo, hi] of covered) {
      if (lo > s + EPS) out.push([at(s), at(lo)]);
      s = Math.max(s, hi);
    }
    if (s < 1 - EPS) out.push([at(s), e.b]);
  }
  return out;
}

/** Joins segments that meet end to end into polylines, so corners draw as joins, not gaps. */
export function chain(segs: readonly Seg[]): Pt[][] {
  const left = [...segs];
  const lines: Pt[][] = [];
  while (left.length > 0) {
    const first = left.shift();
    if (!first) break;
    const line: Pt[] = [first[0], first[1]];
    let grew = true;
    while (grew) {
      grew = false;
      const end = line[line.length - 1];
      if (!end) break;
      const k = left.findIndex((s) => near(s[0], end) || near(s[1], end));
      const s = k >= 0 ? left[k] : undefined;
      if (s) {
        left.splice(k, 1);
        line.push(near(s[0], end) ? s[1] : s[0]);
        grew = true;
      }
    }
    lines.push(line);
  }
  return lines;
}

/**
 * The outline of touching polygons as one path. `keep` drops boundary segments that are not
 * drawn edges, such as the axis side of a half section.
 */
export function outlinePath(
  polys: readonly (readonly Pt[])[],
  to: Map2 = same,
  keep: (s: Seg) => boolean = () => true,
): string {
  return chain(unionBoundary(polys).filter(keep))
    .map((line) => {
      const closed = line.length > 2 && near(line[0] ?? [NaN, NaN], line[line.length - 1] ?? [0, 0]);
      return closed ? polygonPath(line.slice(0, -1), to) : polylinePath(line, to);
    })
    .join(" ");
}

/**
 * A freehand-style break line between two points: a gentle zigzag, the drafting mark for
 * "the part continues past here" on a detail view.
 */
export function breakPath(a: Pt, b: Pt, amp: number, waves = 3): string {
  return polylinePath(breakPoints(a, b, amp, waves));
}

/** The points of a break line, for building a clip path that follows it. */
export function breakPoints(a: Pt, b: Pt, amp: number, waves = 3): Pt[] {
  const pts: Pt[] = [a];
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  const len = Math.hypot(dx, dy) || 1;
  const nx = -dy / len;
  const ny = dx / len;
  const steps = waves * 2;
  for (let i = 1; i < steps; i++) {
    const s = i / steps;
    const k = i % 2 === 1 ? amp : -amp;
    pts.push([a[0] + dx * s + nx * k, a[1] + dy * s + ny * k]);
  }
  pts.push(b);
  return pts;
}

/** Highest z (second coordinate) at which a profile reaches radius r. */
export function topAtRadius(profile: readonly Pt[], r: number): number {
  const zs = profile.filter((p) => Math.abs(p[0] - r) < 1e-3).map((p) => p[1]);
  return zs.length > 0 ? Math.max(...zs) : 0;
}
