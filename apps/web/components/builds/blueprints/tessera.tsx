import type { TesseraData, TesseraModule } from "@/lib/bench/tessera";
import { Fade, Fill, Outline } from "./draw";
import { BlueprintFrame } from "./frame";
import { breakPath, fmt, n3, polygonPath, polylinePath, rectPath, type Pt } from "./geometry";
import { Dim, DetailMark, Label, Leader, Line } from "./primitives";
import { hatchUrl, unitsPerPx, type ViewBox } from "./units";
import { BlueprintView } from "./view";

/**
 * Tessera bench storage drawings, from content/bench/tessera.data.json (bench/tessera/export_site.py).
 * Plan views: x across the bench, y depth; on screen the back is at the top.
 */

type Joint = TesseraData["joint"];
type Grid = TesseraData["grid"];

/** Half the bowtie's width where it crosses a module's outer face (u = gap from the joint line). */
function faceHalf(j: Joint, g: Grid): number {
  return (j.neck_mm + ((j.end_mm - j.neck_mm) * g.gap_mm) / j.reach_mm) / 2;
}

type Edge = { from: Pt; to: Pt; out: Pt };

/** A cup's four outer edges, anticlockwise in plan (y up), with each edge's outward normal. */
function edges(x0: number, y0: number, x1: number, y1: number): Edge[] {
  return [
    { from: [x0, y0], to: [x1, y0], out: [0, -1] },
    { from: [x1, y0], to: [x1, y1], out: [1, 0] },
    { from: [x1, y1], to: [x0, y1], out: [0, 1] },
    { from: [x0, y1], to: [x0, y0], out: [-1, 0] },
  ];
}

const add = (a: Pt, b: Pt, s = 1): Pt => [a[0] + b[0] * s, a[1] + b[1] * s];

/**
 * A 1 x 1 cup's outline and cavity in plan, offset by `ox`: the outer face with a half-bowtie
 * socket notched in at the middle of each edge, and the cavity with the boss behind each socket.
 */
function cupShapes(g: Grid, j: Joint, ox: number): { outer: Pt[]; cavity: Pt[] } {
  const x0 = ox + g.gap_mm;
  const x1 = ox + g.unit_mm - g.gap_mm;
  const y0 = g.gap_mm;
  const y1 = g.unit_mm - g.gap_mm;
  const fh = faceHalf(j, g);
  const eh = j.end_mm / 2;
  const bh = j.boss_width_mm / 2;
  const outer: Pt[] = [];
  const cavity: Pt[] = [];
  for (const e of edges(x0, y0, x1, y1)) {
    const d: Pt = [Math.sign(e.to[0] - e.from[0]), Math.sign(e.to[1] - e.from[1])];
    const mid: Pt = [(e.from[0] + e.to[0]) / 2, (e.from[1] + e.to[1]) / 2];
    const inward: Pt = [-e.out[0], -e.out[1]];
    outer.push(e.from, add(mid, d, -fh), add(add(mid, inward, j.depth_mm), d, -eh), add(add(mid, inward, j.depth_mm), d, eh), add(mid, d, fh));
    const wallStart = add(add(e.from, inward, g.wall_mm), d, g.wall_mm);
    const wallMid = add(mid, inward, g.wall_mm);
    const bossMid = add(mid, inward, j.boss_depth_mm);
    cavity.push(wallStart, add(wallMid, d, -bh), add(bossMid, d, -bh), add(bossMid, d, bh), add(wallMid, d, bh));
  }
  return { outer, cavity };
}

// ----------------------------------------------------------------------------------------------
// Sheet 1: the joint

const PAIR: ViewBox = [-8, -13, 120, 88];
const DETAIL: ViewBox = [-16, -17.5, 32, 36];

export function TesseraJoint({ data }: { data: TesseraData }) {
  const { grid: g, joint: j } = data;
  return (
    <BlueprintFrame
      data={data}
      title="Tessera joint, plan"
      scale="Fit to width"
      sheet="1 / 2"
      legend={[
        { swatch: "section", label: "Walls, cut at mid-height" },
        { swatch: "solid", label: "Bowtie key (blue PLA)" },
      ]}
      notes={[
        <>
          Cups stand {fmt(g.gap_mm)} mm inside their {fmt(g.unit_mm, 0)} mm cells, so neighbours never bind; a{" "}
          {fmt(g.unit_mm, 0)} mm cup is {fmt(g.cup_mm, 1)} mm square with {fmt(g.wall_mm, 1)} mm walls.
        </>,
        <>
          Every outside edge has a half-bowtie socket at its middle, running top to bottom. Behind each one the wall
          thickens into a {fmt(j.boss_width_mm, 1)} mm boss.
        </>,
        <>
          The key clears the socket by {fmt(j.key_clearance_mm)} mm a side, so it starts in by hand. Its four crush ribs
          stand {fmt(j.rib_interference_mm)} mm into the socket walls and squash on the way in, which takes out the play
          the plain keys had.
        </>,
      ]}
    >
      <div className="grid items-end gap-8 md:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <Pair data={data} />
        <Detail data={data} />
      </div>
    </BlueprintFrame>
  );
}

function Pair({ data }: { data: TesseraData }) {
  const { grid: g, joint: j } = data;
  const p = unitsPerPx(PAIR);
  const u = g.unit_mm;
  const Y = (y: number) => u - y;
  const toScreen = (pt: Pt): Pt => [pt[0], Y(pt[1])];
  const cups = [0, u].map((ox) => cupShapes(g, j, ox));
  const keyAt: Pt = [u, u / 2];
  const key = j.key.map(([ku, kv]) => toScreen([keyAt[0] + ku, keyAt[1] + kv]));
  const ribs = j.ribs.map(([ru, rv]) => toScreen([keyAt[0] + ru, keyAt[1] + rv]));
  const names = ["TIPS", "SPARE"];
  const groove: Pt = toScreen([u / 2, u - g.gap_mm - j.depth_mm / 2]);

  return (
    <BlueprintView
      id="bp-tessera-pair"
      viewBox={PAIR}
      hatch={1.6}
      caption="Plan · two cups keyed"
      title="Two Tessera cups joined by a bowtie key, plan view"
      desc={
        `Two ${fmt(g.cup_mm, 1)} mm square cups on the ${fmt(u, 0)} mm grid, side by side. A bowtie key sits in the ` +
        `two facing sockets on the shared edge. Every other edge shows an empty socket, a vertical groove.`
      }
    >
      {cups.map((c, i) => (
        <g key={i}>
          <Fill d={`${polygonPath(c.outer.map(toScreen))} ${polygonPath(c.cavity.map(toScreen))}`} fill={hatchUrl("bp-tessera-pair")} fillRule="evenodd" />
          <Outline d={polygonPath(c.outer.map(toScreen))} className="text-accent" />
          <Outline d={polygonPath(c.cavity.map(toScreen))} className="text-accent" tone="context" delay={0.15} />
        </g>
      ))}
      <Fill d={polygonPath(key)} className="fill-fg/70 dark:fill-fg/40" delay={0.6} />
      {ribs.map((r, i) => (
        <Fill key={i} d={circlePath(r, j.rib_radius_mm)} className="fill-fg/70 dark:fill-fg/40" delay={0.6} />
      ))}
      <Outline d={polygonPath(key)} className="text-fg" tone="context" delay={0.5} />

      <Fade>
        {names.map((n, i) => (
          <Label key={n} at={[u * i + u / 2, Y(u / 2)]} anchor="middle" tone="muted">
            {n}
          </Label>
        ))}
        <DetailMark c={toScreen(keyAt)} r={11} letter="A" at={[keyAt[0] + 14, Y(keyAt[1]) - 12]} />
        <Leader points={[groove, [groove[0], -6], [groove[0] + 6, -6]]} p={p} end="dot" />
        <Label at={[groove[0] + 7.5, -6]}>socket (empty)</Label>
        <Dim
          a={[0, Y(0) + 14]}
          b={[u, Y(0) + 14]}
          p={p}
          ext={[
            [[0, Y(0) + 1.5], [0, Y(0) + 16]],
            [[u, Y(0) + 1.5], [u, Y(0) + 16]],
          ]}
          label={`${fmt(u, 0)} grid`}
          v="below"
        />
        <Dim
          a={[u + g.gap_mm, Y(0) + 6]}
          b={[2 * u - g.gap_mm, Y(0) + 6]}
          p={p}
          ext={[[[2 * u - g.gap_mm, Y(0) + 1.5], [2 * u - g.gap_mm, Y(0) + 8]]]}
          label={`${fmt(g.cup_mm, 1)} cup`}
          v="below"
        />
      </Fade>
    </BlueprintView>
  );
}

/** A circle as a path, so it can draw on and fade like the outlines. */
function circlePath(c: Pt, r: number): string {
  return `M${n3(c[0] - r)} ${n3(c[1])} a${n3(r)} ${n3(r)} 0 1 0 ${n3(2 * r)} 0 a${n3(r)} ${n3(r)} 0 1 0 ${n3(-2 * r)} 0 Z`;
}

/** Detail A: the key in its two sockets, in joint coordinates (u across the joint line, v along it). */
function Detail({ data }: { data: TesseraData }) {
  const { grid: g, joint: j } = data;
  const p = unitsPerPx(DETAIL);
  const S = (pt: Pt): Pt => [pt[0], -pt[1]];
  const W = 12; // half the window along the joint line
  const fh = faceHalf(j, g);
  const eh = j.end_mm / 2;
  const face = g.gap_mm;
  const wall = g.gap_mm + g.wall_mm;
  const boss = g.gap_mm + j.boss_depth_mm;
  const bh = j.boss_width_mm / 2;
  const reach = j.reach_mm;
  const edge = 13.5; // where the window cuts the material, across the joint line

  // One cup's material in the window (s = -1 left, +1 right), open where the window cuts it.
  const side = (s: number) => {
    const m = (pts: Pt[]) => pts.map(([a, b]) => S([s * a, b]));
    const faceRun = m([
      [face, -W],
      [face, -fh],
      [reach, -eh],
      [reach, eh],
      [face, fh],
      [face, W],
    ]);
    const cav = m([
      [wall, W],
      [wall, bh],
      [boss, bh],
      [boss, -bh],
      [wall, -bh],
      [wall, -W],
    ]);
    return { faceRun, cav, solid: [...faceRun, ...cav] };
  };
  const sides = [-1, 1].map(side);
  const key = j.key.map(S);
  const ribs = j.ribs.map(S);
  const [rib] = ribs;
  const flankMid = S([-(face + reach) / 2, (fh + eh) / 2]);

  return (
    <BlueprintView
      id="bp-tessera-key"
      viewBox={DETAIL}
      hatch={0.7}
      caption="Detail A · key in two sockets"
      title="Detail A: the bowtie key in its two sockets"
      desc={
        `The key spans both sockets: ${fmt(j.neck_mm, 1)} mm wide on the joint line and ${fmt(j.end_mm, 1)} mm at each ` +
        `end, ${fmt(reach)} mm from the line. The flanks run ${fmt(j.flank_deg, 1)} degrees off the pull direction. ` +
        `Four crush ribs, ${fmt(2 * j.rib_radius_mm, 1)} mm round, press into the socket walls.`
      }
    >
      {sides.map((sd, i) => (
        <g key={i}>
          <Fill d={polygonPath(sd.solid)} fill={hatchUrl("bp-tessera-key")} />
          <Outline d={polylinePath(sd.faceRun)} className="text-accent" />
          <Outline d={polylinePath(sd.cav)} className="text-accent" tone="context" delay={0.15} />
          <Fade>
            <path d={breakPath(sd.cav[0] ?? [0, 0], sd.faceRun[sd.faceRun.length - 1] ?? [0, 0], 0.5, 2)} className="text-muted" fill="none" stroke="currentColor" strokeWidth={1} vectorEffect="non-scaling-stroke" />
            <path d={breakPath(sd.faceRun[0] ?? [0, 0], sd.cav[sd.cav.length - 1] ?? [0, 0], 0.5, 2)} className="text-muted" fill="none" stroke="currentColor" strokeWidth={1} vectorEffect="non-scaling-stroke" />
          </Fade>
        </g>
      ))}
      <Fill d={polygonPath(key)} className="fill-fg/70 dark:fill-fg/40" delay={0.6} />
      {ribs.map((r, i) => (
        <Fill key={i} d={circlePath(r, j.rib_radius_mm)} className="fill-fg/70 dark:fill-fg/40" delay={0.6} />
      ))}
      <Outline d={polygonPath(key)} className="text-fg" tone="context" delay={0.5} />

      <Fade>
        <Line a={[0, -W - 1.5]} b={[0, W + 1.5]} dash="centre" className="text-subtle" />
        <Dim
          a={[edge + 1, -eh]}
          b={[edge + 1, eh]}
          p={p}
          ext={[
            [[reach + 0.6, -eh], [edge + 1.8, -eh]],
            [[reach + 0.6, eh], [edge + 1.8, eh]],
          ]}
          label={fmt(j.end_mm, 1)}
          at={[edge + 1.6, 0]}
          rotate={-90}
          v="below"
        />
        <Dim
          a={[0, -W - 3]}
          b={[reach, -W - 3]}
          p={p}
          ext={[[[reach, -eh - 0.6], [reach, -W - 3.8]]]}
          label={fmt(reach)}
          v="above"
        />
        <Leader points={[S([0, -j.neck_mm / 2]), [-3.5, W + 2.5], [-6, W + 2.5]]} p={p} />
        <Label at={[-6.5, W + 2.5]} anchor="end">
          {`neck ${fmt(j.neck_mm, 1)}`}
        </Label>
        {rib ? (
          <>
            <Leader points={[rib, [rib[0] + 2.5, rib[1] - 5.5], [rib[0] + 3.5, rib[1] - 5.5]]} p={p} end="dot" />
            <Label at={[rib[0] + 4, rib[1] - 5.5]}>rib</Label>
          </>
        ) : null}
        <Leader points={[flankMid, [-edge + 1, -W - 3], [-edge + 2, -W - 3]]} p={p} end="dot" />
        <Label at={[-edge + 2.4, -W - 3]} v="above">{`${fmt(j.flank_deg, 1)}°`}</Label>
      </Fade>
    </BlueprintView>
  );
}

// ----------------------------------------------------------------------------------------------
// Sheet 2: the bench layout

const MAT_SHOWN_MM = 62; // the mat is drawn cut off: only its back edge matters here

export function TesseraLayout({ data }: { data: TesseraData }) {
  const { grid: g, layout: lay } = data;
  const width = lay.cols * g.unit_mm;
  const depth = lay.rows * g.unit_mm;
  const printed = lay.modules.filter((m) => m.status === "printed");
  return (
    <BlueprintFrame
      data={data}
      title="Tessera bench layout"
      scale="Fit to width"
      sheet="2 / 2"
      legend={[
        { swatch: "part", label: "Printed" },
        { swatch: "context", label: "Planned" },
      ]}
      notes={[
        <>
          {lay.cols} by {lay.rows} squares, {fmt(width, 0)} by {fmt(depth, 0)} mm, behind the soldering mat. Numbers are
          heights in mm ({fmt(g.height_step_mm, 0)} mm steps): tall at the back, low at the front, so every tool is in
          sight from the chair.
        </>,
        <>
          Left to right follows the job: heat by the iron, then solder and flux, then cleaning, with the alcohol
          farthest from the heat. The heat gun holster prints in PETG.
        </>,
        <>
          Printed so far: {printed.map((m) => m.name).join(", ")}.
        </>,
      ]}
    >
      <LayoutPlan data={data} />
    </BlueprintFrame>
  );
}

function LayoutPlan({ data }: { data: TesseraData }) {
  const { grid: g, layout: lay } = data;
  const u = g.unit_mm;
  const width = lay.cols * u;
  const depth = lay.rows * u;
  const [matW] = lay.mat_mm;
  const VB: ViewBox = [-12, -30, width + 40, depth + MAT_SHOWN_MM + 76];
  const p = unitsPerPx(VB);
  const Y = (rowFromFront: number) => depth - rowFromFront;
  const matX0 = (width - matW) / 2;
  const matTop = depth + 34;
  const matBottom = matTop + MAT_SHOWN_MM;
  const inset = 2;

  const box = (m: TesseraModule): [number, number, number, number] => [
    m.col * u + inset,
    Y((m.row + m.ny) * u) + inset,
    (m.col + m.nx) * u - inset,
    Y(m.row * u) - inset,
  ];

  return (
    <BlueprintView
      id="bp-tessera-layout"
      viewBox={VB}
      className="mx-auto max-w-[44rem]"
      caption="Plan · back of the bench at the top"
      title="Tessera bench layout, plan view"
      desc={
        `${lay.cols} by ${lay.rows} grid of ${fmt(u, 0)} mm squares behind the soldering mat. ` +
        lay.modules
          .map((m) => `${m.name}, ${m.nx} by ${m.ny}, ${fmt(m.height_mm, 0)} mm tall, ${m.status}`)
          .join("; ") +
        "."
      }
    >
      {/* grid squares, faint */}
      <g className="text-line">
        {Array.from({ length: lay.cols + 1 }, (_, i) => (
          <Line key={`c${i}`} a={[i * u, 0]} b={[i * u, depth]} />
        ))}
        {Array.from({ length: lay.rows + 1 }, (_, k) => (
          <Line key={`r${k}`} a={[0, k * u]} b={[width, k * u]} />
        ))}
      </g>

      {lay.modules.map((m, i) => {
        const [x0, y0, x1, y1] = box(m);
        const d = rectPath(x0, y0, x1, y1);
        const done = m.status === "printed";
        return (
          <g key={m.name}>
            <Fill d={d} className={done ? "fill-accent-soft" : "fill-surface-2"} delay={0.1 + i * 0.04} />
            {done ? (
              <Outline d={d} className="text-accent" delay={i * 0.04} />
            ) : (
              <path d={d} fill="none" stroke="currentColor" strokeWidth={1} strokeDasharray="3.5 2.5" vectorEffect="non-scaling-stroke" className="text-muted" />
            )}
          </g>
        );
      })}

      {/* the mat, cut off */}
      <path
        d={`${polylinePath([
          [matX0, matBottom],
          [matX0, matTop],
          [matX0 + matW, matTop],
          [matX0 + matW, matBottom],
        ])} ${breakPath([matX0, matBottom], [matX0 + matW, matBottom], 4, 4)}`}
        fill="none"
        stroke="currentColor"
        strokeWidth={1}
        strokeDasharray="3.5 2.5"
        vectorEffect="non-scaling-stroke"
        className="text-muted"
      />

      <Fade>
        {lay.modules.map((m) => {
          const [x0, y0, x1, y1] = box(m);
          const cx = (x0 + x1) / 2;
          const cy = (y0 + y1) / 2;
          const h = `${fmt(m.height_mm, 0)}${m.material === "PETG" ? " PETG" : ""}`;
          return (
            <Label key={m.name} at={[cx, cy - 8]} anchor="middle" size={0.82} lines={[m.name, h]} tone={m.status === "printed" ? "accent" : "fg"} />
          );
        })}
        <Label at={[width / 2, matTop + 26]} anchor="middle" tone="muted">
          silicone mat (work area)
        </Label>
        <Label at={[0, depth + 17]} tone="muted">
          heat
        </Label>
        <Label at={[width / 2, depth + 17]} anchor="middle" tone="muted">
          solder, flux
        </Label>
        <Label at={[width, depth + 17]} anchor="end" tone="muted">
          cleaning
        </Label>
        <Dim
          a={[0, -12]}
          b={[width, -12]}
          p={p}
          ext={[
            [[0, -2], [0, -15]],
            [[width, -2], [width, -15]],
          ]}
          label={`${fmt(width, 0)} (${lay.cols} × ${fmt(u, 0)})`}
        />
        <Dim
          a={[width + 14, 0]}
          b={[width + 14, depth]}
          p={p}
          ext={[
            [[width + 2, 0], [width + 17, 0]],
            [[width + 2, depth], [width + 17, depth]],
          ]}
          label={fmt(depth, 0)}
          at={[width + 19, depth / 2]}
          rotate={90}
          v="middle"
        />
      </Fade>
    </BlueprintView>
  );
}
