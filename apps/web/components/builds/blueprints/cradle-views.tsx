import type { BuildData } from "@/lib/builds/data";
import { Fade, Fill, Outline } from "./draw";
import { BlueprintFrame } from "./frame";
import { fmt, n3, polygonPath, polygonsPath, polylinePath, rectPath, type Pt } from "./geometry";
import { CentreLine, Dim, Label, Leader, Line, Note, Path } from "./primitives";
import { hatchUrl, unitsPerPx, type ViewBox } from "./units";
import { BlueprintView } from "./view";

const BACK: ViewBox = [-27, -28, 90, 56];
const SIDE: ViewBox = [-32, -48, 102, 92];
/** The section is drawn at twice the back view. */
const K = 2;
/** The supplied screws are M2 (the servo's 1.5 mm pilot holes take M2 self-tappers). */
const SCREW = "M2";
const SCREW_D = 2;

const circlePath = (c: Pt, r: number) =>
  `M${n3(c[0] - r)} ${n3(c[1])} a${n3(r)} ${n3(r)} 0 1 0 ${n3(2 * r)} 0 a${n3(r)} ${n3(r)} 0 1 0 ${n3(-2 * r)} 0 Z`;

/**
 * The servo cradle: a back view in its a–b frame (a along the case from the shaft axis, b across
 * it, the foot cheek at −b drawn at the bottom), and a section through the far holes at twice
 * the scale for the wall, pads, cheeks and the axle height the chassis needs.
 */
export function CradleViews({ data }: { data: BuildData }) {
  const c = data.cradle;
  const kase = data.servo.case;
  const along = Math.max(...c.holes.map((h) => h[0])) - Math.min(...c.holes.map((h) => h[0]));
  const across = Math.max(...c.holes.map((h) => h[1])) - Math.min(...c.holes.map((h) => h[1]));
  const [w0, w1, wh] = c.window;

  return (
    <BlueprintFrame
      data={data}
      title={`Servo cradle (${data.servo.model})`}
      scale="Fit to width · section × 2"
      sheet="2 / 3"
      legend={[
        { swatch: "part", label: "Cradle, PETG" },
        { swatch: "section", label: "Cradle, cut" },
        { swatch: "hidden", label: "Hidden: cheeks and pads behind the wall" },
        { swatch: "context", label: "Servo and screws (phantom)" },
        { swatch: "centre", label: "Shaft axis, axle" },
      ]}
      notes={[
        <>
          {c.holes.length} × Ø{fmt(c.hole_diameter_mm)} holes through Ø{fmt(c.pad_diameter_mm)} ×{" "}
          {fmt(c.pad_mm)} mm pads, {fmt(along)} × {fmt(across)} apart: the servo&apos;s bottom holes.
        </>,
        <>
          {SCREW} × {kase.mount_screw_length_mm} supplied screws, {fmt(c.screw_depth_mm)} mm into the case (
          {fmt(kase.max_screw_depth_mm)} at most).
        </>,
        <>
          One opening: R{fmt(c.disc_opening_radius_mm)} round the idler disc, a {fmt(2 * c.throat_half_width_mm)} mm
          throat, and a {fmt(w1 - w0)} × {fmt(2 * wh)} mm window for the bus plugs.
        </>,
        <>
          Ears {fmt(c.ear_length_mm)} × {fmt(c.ear_mm)} mm on the foot side, for the chassis screws; the axle is{" "}
          {fmt(c.axle_above_foot_mm)} mm above the foot.
        </>,
      ]}
    >
      <div className="grid gap-x-8 gap-y-8 lg:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)] lg:items-center">
        <BackView data={data} along={along} across={across} />
        <SideSection data={data} />
      </div>
    </BlueprintFrame>
  );
}

function BackView({ data, along, across }: { data: BuildData; along: number; across: number }) {
  const c = data.cradle;
  const id = "bp-cradle";
  const p = unitsPerPx(BACK);
  // Screen: x = a, y = −b, so +b is up and the foot (−b) is at the bottom.
  const P = (q: Pt): Pt => [q[0], -q[1]];
  const a0 = c.a_min_mm;
  const a1 = c.a_max_mm;
  const bo = c.b_outer_mm;
  const ea = c.ear_length_mm;
  const outline: Pt[] = [
    [a0, bo],
    [a1, bo],
    [a1, -bo + c.ear_mm],
    [a1 + ea, -bo + c.ear_mm],
    [a1 + ea, -bo],
    [a0 - ea, -bo],
    [a0 - ea, -bo + c.ear_mm],
    [a0, -bo + c.ear_mm],
  ];
  const outlineD = polygonPath(outline, P);

  // The merged opening: the disc circle, a throat to the window, the window. In screen
  // coordinates the arc runs from the throat's top edge round the left to its bottom edge.
  const R = c.disc_opening_radius_mm;
  const t = c.throat_half_width_mm;
  const [w0, w1, wh] = c.window;
  const at = Math.sqrt(Math.max(R * R - t * t, 0));
  const openingD =
    `M${n3(at)} ${n3(-t)} A${n3(R)} ${n3(R)} 0 1 0 ${n3(at)} ${n3(t)} ` +
    polylinePath(
      [
        [w0, t],
        [w0, wh],
        [w1, wh],
        [w1, -wh],
        [w0, -wh],
        [w0, -t],
      ],
      (q) => q,
    ).replace(/^M/, "L") +
    " Z";
  const holes = c.holes.map((h) => P(h));
  const hr = c.hole_diameter_mm / 2;
  const mask = `${id}-mask`;
  const clip = `${id}-clip`;

  const top = -(bo + 5.4);
  const bottom = bo + 5.4;
  const hx = Math.min(...holes.map((h) => h[0]));
  const hx2 = Math.max(...holes.map((h) => h[0]));
  const hyTop = Math.min(...holes.map((h) => h[1]));
  const hyBot = Math.max(...holes.map((h) => h[1]));
  const rightX = a1 + ea + 5;
  const rr = R / Math.SQRT2;

  return (
    <BlueprintView
      id={id}
      viewBox={BACK}
      caption="Back view · a along the case, b across"
      title="Servo cradle, back view"
      desc={
        `Back view of the servo cradle, ${fmt(a1 - a0 + 2 * ea)} mm long with its ears and ${fmt(2 * bo)} mm across. ` +
        `Four ${fmt(c.hole_diameter_mm)} mm holes ${fmt(along)} by ${fmt(across)} mm apart on ${fmt(c.pad_diameter_mm)} mm pads. ` +
        `One opening: radius ${fmt(R)} mm round the shaft axis, a ${fmt(2 * t)} mm throat and a ` +
        `${fmt(w1 - w0)} by ${fmt(2 * wh)} mm connector window.`
      }
    >
      <defs>
        <mask id={mask} maskUnits="userSpaceOnUse" x={BACK[0]} y={BACK[1]} width={BACK[2]} height={BACK[3]}>
          <path d={outlineD} fill="white" stroke="white" strokeWidth={2} />
          <path d={openingD} fill="black" />
          {holes.map((h, i) => (
            <path key={i} d={circlePath(h, hr)} fill="black" />
          ))}
        </mask>
        <clipPath id={clip}>
          <path d={outlineD} />
        </clipPath>
      </defs>

      <g mask={`url(#${mask})`}>
        <Fill d={outlineD} className="fill-accent-soft" />
        <Outline d={outlineD} className="text-accent" />
      </g>
      <g clipPath={`url(#${clip})`}>
        <Outline d={openingD} className="text-accent" delay={0.15} />
      </g>
      {holes.map((h, i) => (
        <Outline key={i} d={circlePath(h, hr)} className="text-accent" delay={0.25} />
      ))}

      <Fade>
        <g className="text-muted">
          <Line a={P([a0, c.b_inner_mm])} b={P([a1, c.b_inner_mm])} dash="hidden" />
          <Line a={P([a0, -c.b_inner_mm])} b={P([a1, -c.b_inner_mm])} dash="hidden" />
          {holes.map((h, i) => (
            <Path key={i} d={circlePath(h, c.pad_diameter_mm / 2)} dash="hidden" />
          ))}
        </g>

        <CentreLine a={[-R - 3, 0]} b={[R + 3, 0]} />
        <CentreLine a={[0, top - 2]} b={[0, R + 3]} />
        <Label at={[-1.6, top]} anchor="end" tone="muted">
          shaft axis
        </Label>

        <Dim
          a={[0, top]}
          b={[hx, top]}
          p={p}
          ext={[[[hx, hyTop - hr - 1], [hx, top - 1.6]]]}
          label={fmt(hx)}
        />
        <Dim
          a={[hx, top]}
          b={[hx2, top]}
          p={p}
          ext={[[[hx2, hyTop - hr - 1], [hx2, top - 1.6]]]}
          label={fmt(along)}
        />
        <Dim
          a={[rightX, hyTop]}
          b={[rightX, hyBot]}
          p={p}
          ext={[
            [
              [hx2 + hr + 1, hyTop],
              [rightX + 1.6, hyTop],
            ],
            [
              [hx2 + hr + 1, hyBot],
              [rightX + 1.6, hyBot],
            ],
          ]}
          at={[rightX + 1.8, 0]}
          anchor="start"
          v="middle"
          label={fmt(across)}
        />
        <Dim
          a={[a0 - ea, bottom]}
          b={[a1 + ea, bottom]}
          p={p}
          ext={[
            [
              [a0 - ea, bo + 1],
              [a0 - ea, bottom + 1.6],
            ],
            [
              [a1 + ea, bo + 1],
              [a1 + ea, bottom + 1.6],
            ],
          ]}
          v="below"
          label={
            <>
              {fmt(a1 - a0 + 2 * ea)}
              <Note> overall</Note>
            </>
          }
        />

        <Dim a={[0, 0]} b={[-rr, -rr]} p={p} arrows="end" at={[-R + 1.2, -1.9]} anchor="start" v="middle" label={`R${fmt(R)}`} />
        <Label at={[(w0 + w1) / 2, -2.4]} anchor="middle" tone="muted" size={0.85}>
          window
        </Label>
        <Label at={[(w0 + w1) / 2, 2.4]} anchor="middle" size={0.85}>
          {fmt(w1 - w0)} × {fmt(2 * wh)}
        </Label>
      </Fade>
    </BlueprintView>
  );
}

function SideSection({ data }: { data: BuildData }) {
  const c = data.cradle;
  const kase = data.servo.case;
  const id = "bp-cradle-b";
  const p = unitsPerPx(SIDE);
  const back = -(c.wall_mm + c.pad_mm);
  const wallTop = -c.pad_mm;
  // Screen: x = K·(c − back), y = −K·b; the foot (−b) at the bottom, the axle across at y = 0.
  const S = (q: Pt): Pt => [K * (q[0] - back), -K * q[1]];
  const X = (cc: number) => K * (cc - back);
  const Y = (b: number) => -K * b;

  const bo = c.b_outer_mm;
  const bi = c.b_inner_mm;
  const ch = c.cheek_height_mm;
  const hb = Math.max(...c.holes.map((h) => Math.abs(h[1])));
  const pr = c.pad_diameter_mm / 2;
  const hr = c.hole_diameter_mm / 2;
  const padOut = Math.min(hb + pr, bi);
  // Section through the far pair of holes: the back wall is cut by the two holes into three
  // pieces; the outer two carry the cheeks; pads stand on the wall round each hole.
  const lower: Pt[] = [
    [back, -bo],
    [ch, -bo],
    [ch, -bi],
    [wallTop, -bi],
    [wallTop, -padOut],
    [0, -padOut],
    [0, -(hb + hr)],
    [back, -(hb + hr)],
  ];
  const upper: Pt[] = lower.map(([x, y]) => [x, -y]);
  const middle: Pt[] = [
    [back, -(hb - hr)],
    [0, -(hb - hr)],
    [0, -(hb - pr)],
    [wallTop, -(hb - pr)],
    [wallTop, hb - pr],
    [0, hb - pr],
    [0, hb - hr],
    [back, hb - hr],
  ];
  const section = [lower, middle, upper];
  const caseHalf = kase.width_mm / 2;
  const caseEnd = X(ch + 4);
  const screwEnd = X(c.screw_depth_mm);
  const axleY = Y(0);
  const foot = Y(-bo);
  const dimY = foot + 6;

  return (
    <BlueprintView
      id={id}
      viewBox={SIDE}
      hatch={1.8}
      caption="Section through the far holes · × 2"
      title="Servo cradle, section through the far holes"
      desc={
        `Section of the cradle at twice scale. Back wall ${fmt(c.wall_mm)} mm with ${fmt(c.pad_mm)} mm pads; ` +
        `cheeks ${fmt(c.cheek_mm)} mm thick reach ${fmt(ch)} mm from the face the servo sits on. ` +
        `The wheel axle is ${fmt(c.axle_above_foot_mm)} mm above the foot. ${SCREW} by ${kase.mount_screw_length_mm} ` +
        `supplied screws go ${fmt(c.screw_depth_mm)} mm into the case.`
      }
    >
      <Fill d={polygonsPath(section, S)} className="fill-accent-soft" />
      <Fill d={polygonsPath(section, S)} fill={hatchUrl(id)} />
      {section.map((poly, i) => (
        <Outline key={i} d={polygonPath(poly, S)} className="text-accent" delay={i * 0.08} />
      ))}

      <Fade>
        <g className="text-muted">
          <Path
            d={polylinePath([
              [caseEnd, Y(caseHalf)],
              [X(0), Y(caseHalf)],
              [X(0), Y(-caseHalf)],
              [caseEnd, Y(-caseHalf)],
            ])}
            dash="phantom"
          />
          {[hb, -hb].map((b) => (
            <Path key={b} d={rectPath(X(back), Y(b) - SCREW_D, screwEnd, Y(b) + SCREW_D)} dash="hidden" />
          ))}
        </g>
        <Label at={[(X(0) + caseEnd) / 2 + 2, Y(caseHalf / 2)]} anchor="middle" tone="muted">
          servo case
        </Label>

        <CentreLine a={[-9, axleY]} b={[caseEnd + 4, axleY]} />
        <Label at={[caseEnd + 5, axleY]} tone="muted">
          axle
        </Label>
        <Label at={[X(ch) + 2, foot]} tone="muted">
          foot
        </Label>

        <Dim
          a={[-6, axleY]}
          b={[-6, foot]}
          p={p}
          ext={[
            [
              [-1, foot],
              [-7.6, foot],
            ],
          ]}
        />
        <Label at={[-8.4, axleY + 0.5 * (foot - axleY) - 4.7]} anchor="end" lines={[fmt(c.axle_above_foot_mm), "axle above", "the foot"]} />

        <Leader
          p={p}
          end="dot"
          points={[
            [X(back) + K * c.wall_mm * 0.5, -8],
            [-7, -8],
          ]}
        />
        <Label at={[-8.4, -8]} anchor="end">
          <Note>wall </Note>
          {fmt(c.wall_mm)}
        </Label>
        <Leader
          p={p}
          end="dot"
          points={[
            [X(wallTop) + K * c.pad_mm * 0.5, Y(hb - pr) - 1],
            [-7, Y(hb - pr) - 1],
          ]}
        />
        <Label at={[-8.4, Y(hb - pr) - 1]} anchor="end">
          <Note>pad </Note>
          {fmt(c.pad_mm)}
        </Label>

        <Dim
          a={[X(0), dimY]}
          b={[X(ch), dimY]}
          p={p}
          ext={[
            [
              [X(0), Y(-caseHalf) + 1],
              [X(0), dimY + 1.6],
            ],
            [
              [X(ch), foot + 1],
              [X(ch), dimY + 1.6],
            ],
          ]}
          v="below"
          label={
            <>
              {fmt(ch)}
              <Note> cheek height</Note>
            </>
          }
        />

        <Leader
          p={p}
          points={[
            [screwEnd, Y(hb)],
            [screwEnd + 1.2, -42],
            [15, -42],
          ]}
        />
        <Label
          at={[16, -42]}
          lines={[`${SCREW} × ${kase.mount_screw_length_mm} supplied screws,`, `${fmt(c.screw_depth_mm)} mm into the case`]}
        />
      </Fade>
    </BlueprintView>
  );
}
