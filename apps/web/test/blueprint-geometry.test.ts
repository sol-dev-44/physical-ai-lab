/** Geometry behind the build blueprints: the outline of touching section polygons. */
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { chain, fmt, outlinePath, unionBoundary, type Pt } from "../components/builds/blueprints/geometry";

const square = (x: number, y: number, s = 1): Pt[] => [
  [x, y],
  [x + s, y],
  [x + s, y + s],
  [x, y + s],
];
const length = (segs: ReturnType<typeof unionBoundary>) =>
  segs.reduce((n, [a, b]) => n + Math.hypot(b[0] - a[0], b[1] - a[1]), 0);

describe("unionBoundary", () => {
  it("drops the edge two polygons share", () => {
    const segs = unionBoundary([square(0, 0), square(1, 0)]);
    expect(length(segs)).toBeCloseTo(6);
    expect(segs.some(([a, b]) => a[0] === 1 && b[0] === 1)).toBe(false);
  });

  it("keeps the uncovered part of a partly shared edge", () => {
    // A 1 x 2 strip beside a 1 x 1 square: half of the strip's inner edge is still outline.
    const strip: Pt[] = [
      [0, 0],
      [1, 0],
      [1, 2],
      [0, 2],
    ];
    const segs = unionBoundary([strip, square(1, 0)]);
    expect(length(segs)).toBeCloseTo(8);
  });

  it("chains the boundary into one closed loop", () => {
    const lines = chain(unionBoundary([square(0, 0), square(1, 0), square(0, 1)]));
    expect(lines).toHaveLength(1);
    const line = lines[0] ?? [];
    expect(line[0]).toEqual(line[line.length - 1]);
  });
});

describe("the hub section", () => {
  const file = path.join(__dirname, "../../../content/builds/household-robot.data.json");
  const hub = (JSON.parse(readFileSync(file, "utf8")) as { wheel: { hub_section: Pt[][] } }).wheel.hub_section;

  it("draws no line inside the solid where the export split it into strips", () => {
    const segs = unionBoundary(hub);
    const inside = (p: Pt) =>
      hub.filter((poly) => {
        const xs = poly.map((q) => q[0]);
        const zs = poly.map((q) => q[1]);
        return p[0] > Math.min(...xs) - 1e-9 && p[0] < Math.max(...xs) + 1e-9 && p[1] > Math.min(...zs) && p[1] < Math.max(...zs);
      }).length;
    // A boundary midpoint lies in at most one strip's bounding box; an internal edge would be in two.
    for (const [a, b] of segs) {
      const mid: Pt = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
      expect(inside(mid)).toBeLessThanOrEqual(1);
    }
    expect(outlinePath(hub)).toMatch(/^M/);
  });
});

describe("fmt", () => {
  it("drops trailing zeros", () => {
    expect(fmt(120)).toBe("120");
    expect(fmt(6.45)).toBe("6.45");
    expect(fmt(29.59, 1)).toBe("29.6");
  });
});
