import type { BuildData } from "@/lib/builds/data";
import { Fade, Fill, Outline } from "./draw";
import { BlueprintFrame } from "./frame";
import {
  breakPath,
  breakPoints,
  fmt,
  outlinePath,
  polygonPath,
  polygonsPath,
  rectPath,
  topAtRadius,
  type Pt,
  type Seg,
} from "./geometry";
import { CentreLine, DetailMark, Dim, Label, Leader, Note, Path } from "./primitives";
import { hatchUrl, TIRE_FILL, unitsPerPx, type ViewBox } from "./units";
import { BlueprintView } from "./view";

/** Section edges on the axis are the centre line, not an outline. */
const offAxis = (s: Seg) => !(Math.abs(s[0][0]) < 1e-6 && Math.abs(s[1][0]) < 1e-6);
const times = (s: string) => s.replace(/ x /g, " × ");

const MAIN: ViewBox = [-8, -50, 92, 62];
const DETAIL_A: ViewBox = [-4, -27, 96, 46];
const DETAIL_B: ViewBox = [-50, -19, 94, 50];
/** Detail views are drawn at three times the main view. */
const K = 3;

/**
 * Half cross-section of the drive wheel through a bolt hole, the axis on the left. Radius runs
 * across and z (along the axle) runs up, so the servo-side face that sits on the horn (z = 0) is
 * at the bottom and the drawing is wide rather than tall on a phone. Two details at 3 : 1 carry
 * what is too small at full size: the hub centre (screws, counterbores, pocket) and the tire on
 * the rim (tread, flange, bore).
 */
export function WheelSection({ data }: { data: BuildData }) {
  const { wheel: w, tire: t, servo } = data;
  const hub = w.hub_section;
  const R = w.od_mm / 2;
  const Z = w.width_mm;
  const rimR = w.rim_od_mm / 2;
  const boreR = t.bore_mm / 2;
  const flangeR = rimR + w.flange_mm;
  const holeIn = w.lightening_radius_mm - w.lightening_diameter_mm / 2;
  const holeOut = w.lightening_radius_mm + w.lightening_diameter_mm / 2;
  const boltR = servo.horn.bolt_circle_mm / 2;
  const hubPts = hub.flat();
  const tireAt0 = Math.max(...t.profile.filter((q) => Math.abs(q[1]) < 1e-3).map((q) => q[0]));

  const screw = times(w.screw);
  const caption = t.rim_measured ? (
    <>
      The hub is drawn as designed, with a {fmt(w.rim_od_mm)} mm rim. The tire is sized to the rim as printed (
      {fmt(t.rim_seat_od_mm)} mm by caliper), so its {fmt(t.bore_mm)} mm bore overlaps the drawn rim; on the real
      rim the overlap is the {fmt(t.rim_seat_od_mm - t.bore_mm)} mm squeeze that holds the tire.
    </>
  ) : (
    <>
      Hub and tire are both drawn as designed: the {fmt(t.bore_mm)} mm bore overlaps the {fmt(w.rim_od_mm)} mm rim
      by the squeeze that holds the tire.
    </>
  );

  return (
    <BlueprintFrame
      data={data}
      title="Drive wheel: hub and tire"
      scale="Fit to width · details × 3"
      sheet="1 / 3"
      legend={[
        { swatch: "section", label: "PETG hub, cut" },
        { swatch: "solid", label: "TPU tire" },
        { swatch: "hidden", label: "Servo horn and screw (not cut)" },
        { swatch: "centre", label: "Axis" },
      ]}
      caption={caption}
    >
      <div className="grid gap-x-8 gap-y-8 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)] lg:items-center">
        <MainView
          data={data}
          R={R}
          Z={Z}
          rimR={rimR}
          holeIn={holeIn}
          holeOut={holeOut}
          tireAt0={tireAt0}
          className="lg:row-span-2"
        />
        <DetailA data={data} boltR={boltR} screw={screw} />
        <DetailB data={data} rimR={rimR} boreR={boreR} flangeR={flangeR} hubPts={hubPts} />
      </div>
    </BlueprintFrame>
  );
}

function MainView({
  data,
  R,
  Z,
  rimR,
  holeIn,
  holeOut,
  tireAt0,
  className,
}: {
  data: BuildData;
  R: number;
  Z: number;
  rimR: number;
  holeIn: number;
  holeOut: number;
  tireAt0: number;
  className?: string;
}) {
  const { wheel: w, tire: t } = data;
  const id = "bp-wheel";
  const p = unitsPerPx(MAIN);
  const M = (q: Pt): Pt => [q[0], -q[1]];
  const row1 = -(Z + 6);
  const row2 = -(Z + 12);
  const wx = R + 7;
  const webX = holeOut - 3;
  const lead = holeIn + 3.6;

  return (
    <BlueprintView
      id={id}
      viewBox={MAIN}
      hatch={1.6}
      className={className}
      caption="Half section through a bolt hole"
      title="Drive wheel, half cross-section"
      desc={
        `Half section of the drive wheel: ${fmt(w.od_mm)} mm outside diameter and ${fmt(Z)} mm wide. ` +
        `PETG hub with a ${fmt(w.rim_od_mm)} mm rim, a ${fmt(w.web_mm)} mm web next to the servo and ` +
        `${fmt(w.flange_mm)} mm flanges; ${w.lightening_holes} lightening holes of ${fmt(w.lightening_diameter_mm, 1)} mm. ` +
        `TPU tire ${fmt(t.tread_mm)} mm thick with a ${fmt(t.bore_mm)} mm bore.`
      }
    >
      <Fill d={polygonPath(t.profile, M)} className={TIRE_FILL} />
      <Fill d={polygonsPath(w.hub_section, M)} className="fill-accent-soft" />
      <Fill d={polygonsPath(w.hub_section, M)} fill={hatchUrl(id)} />
      <Outline d={outlinePath(w.hub_section, M, offAxis)} className="text-accent" />
      <Outline d={polygonPath(t.profile, M)} className="text-fg" delay={0.1} />

      <Fade>
        <CentreLine a={[0, row2 - 4]} b={[0, 8]} />
        <Label at={[0, 10.2]} anchor="middle" tone="subtle">
          axis
        </Label>
        <Label at={[14, 5.6]}>
          <Note>servo side: </Note>z 0 sits on the horn
        </Label>

        <Dim
          a={[-4, row1]}
          b={[rimR, row1]}
          p={p}
          arrows="end"
          ext={[[[rimR, -(Z + 1.2)], [rimR, row1 - 1.6]]]}
          at={[rimR / 2, row1]}
          label={
            <>
              Ø{fmt(w.rim_od_mm)}
              <Note> rim</Note>
            </>
          }
        />
        <Dim
          a={[-4, row2]}
          b={[R, row2]}
          p={p}
          arrows="end"
          ext={[[[R, -(topAtRadius(t.profile, R) + 1)], [R, row2 - 1.6]]]}
          at={[R / 2, row2]}
          label={
            <>
              Ø{fmt(w.od_mm)}
              <Note> outside</Note>
            </>
          }
        />
        <Dim
          a={[wx, 0]}
          b={[wx, -Z]}
          p={p}
          ext={[
            [
              [tireAt0 + 1, 0],
              [wx + 1.6, 0],
            ],
            [
              [tireAt0 + 1, -Z],
              [wx + 1.6, -Z],
            ],
          ]}
          at={[wx + 2.2, -Z / 2]}
          anchor="start"
          v="middle"
          label={
            <>
              {fmt(Z)}
              <Note> wide</Note>
            </>
          }
        />
        <Dim
          a={[webX, 0]}
          b={[webX, -w.web_mm]}
          p={p}
          ext={[
            [
              [holeOut - 0.6, 0],
              [webX - 1.4, 0],
            ],
            [
              [holeOut - 0.6, -w.web_mm],
              [webX - 1.4, -w.web_mm],
            ],
          ]}
          at={[webX - 2.2, -w.web_mm / 2]}
          anchor="end"
          v="middle"
          label={
            <>
              <Note>web </Note>
              {fmt(w.web_mm)}
            </>
          }
        />

        <Leader
          p={p}
          points={[
            [holeIn, -w.web_mm / 2],
            [lead, -(w.web_mm + 6.8)],
          ]}
        />
        <Label at={[lead - 0.6, -(w.web_mm + 9)]}>
          {w.lightening_holes} × Ø{fmt(w.lightening_diameter_mm, 1)}
          <Note> holes</Note>
        </Label>

        <DetailMark c={[5.5, -3.2]} r={7.5} letter="A" at={[14.4, -9.6]} />
        <DetailMark c={[rimR + 2, -(Z - 2)]} r={5} letter="B" at={[rimR - 5.5, -(Z - 5)]} />
      </Fade>
    </BlueprintView>
  );
}

function DetailA({ data, boltR, screw }: { data: BuildData; boltR: number; screw: string }) {
  const { wheel: w, servo } = data;
  const id = "bp-wheel-a";
  const p = unitsPerPx(DETAIL_A);
  const A = (q: Pt): Pt => [K * q[0], -K * q[1]];
  const cut = 12.4 * K;
  const top = -(w.web_mm * K + 4);
  const brk = breakPoints([cut, top + 1.5], [cut, 1.5], 0.7, 3);
  const clip = `${id}-clip`;
  const clipD = polygonPath([[-1.5, top], ...brk, [-1.5, 1.5]]);
  const horn = servo.horn;
  const cbR = w.counterbore_diameter_mm / 2;
  const holeR = w.hole_diameter_mm / 2;
  const floorZ = w.web_mm - w.counterbore_depth_mm;
  const tipA = A([boltR + (holeR + cbR) / 2, floorZ]);
  const pocketTip = A([w.center_pocket_diameter_mm / 2 - 1.2, w.center_pocket_depth_mm]);

  return (
    <BlueprintView
      id={id}
      viewBox={DETAIL_A}
      hatch={1.6}
      caption="Detail A · hub centre · × 3"
      title="Detail A: hub centre"
      desc={
        `Hub centre at three times scale. ${screw} screws on a ${fmt(horn.bolt_circle_mm)} mm circle, ` +
        `in ${fmt(w.counterbore_diameter_mm)} mm counterbores ${fmt(w.counterbore_depth_mm)} mm deep, through ` +
        `${fmt(w.hole_diameter_mm)} mm holes. A ${fmt(w.center_pocket_diameter_mm)} mm centre pocket, ` +
        `${fmt(w.center_pocket_depth_mm)} mm deep, fits over the horn's centre screw head.`
      }
    >
      <defs>
        <clipPath id={clip}>
          <path d={clipD} />
        </clipPath>
      </defs>
      <g clipPath={`url(#${clip})`}>
        <Fill d={polygonsPath(w.hub_section, A)} className="fill-accent-soft" />
        <Fill d={polygonsPath(w.hub_section, A)} fill={hatchUrl(id)} />
        <Outline d={outlinePath(w.hub_section, A, offAxis)} className="text-accent" />
      </g>
      <Outline
        d={breakPath([cut, top + 1.5], [cut, 1.5], 0.7, 3)}
        tone="context"
        className="text-muted"
        delay={0.2}
      />

      <Fade>
        <Path d={rectPath(0, 0, K * (horn.od_mm / 2), K * horn.thickness_mm)} dash="hidden" className="text-muted" />
        <Path
          d={rectPath(0, -K * horn.center_head_height_mm, (K * horn.center_head_mm) / 2, 0)}
          dash="hidden"
          className="text-muted"
        />
        <CentreLine a={[0, top - 2]} b={[0, K * horn.thickness_mm + 3]} />
        <CentreLine a={[K * boltR, top - 2]} b={[K * boltR, K * horn.thickness_mm + 3]} />

        <Leader p={p} points={[tipA, [tipA[0] + 5.5, -18.5], [40, -18.5]]} />
        <Label
          at={[41, -18.5]}
          lines={[
            screw,
            `Ø${fmt(w.counterbore_diameter_mm)} × ${fmt(w.counterbore_depth_mm)} counterbores`,
            `Ø${fmt(w.hole_diameter_mm)} through`,
          ]}
        />

        <Label at={[K * (horn.od_mm / 2) + 1.6, (K * horn.thickness_mm) / 2]} tone="muted">
          servo horn
        </Label>

        <Leader p={p} points={[pocketTip, [pocketTip[0] + 2.5, 3], [13, 10.6]]} />
        <Label
          at={[14, 11]}
          lines={[
            `Ø${fmt(w.center_pocket_diameter_mm)} × ${fmt(w.center_pocket_depth_mm)} centre pocket`,
            "over the horn's centre screw",
          ]}
        />
      </Fade>
    </BlueprintView>
  );
}

function DetailB({
  data,
  rimR,
  boreR,
  flangeR,
  hubPts,
}: {
  data: BuildData;
  rimR: number;
  boreR: number;
  flangeR: number;
  hubPts: readonly Pt[];
}) {
  const { wheel: w, tire: t } = data;
  const id = "bp-wheel-b";
  const p = unitsPerPx(DETAIL_B);
  const R = w.od_mm / 2;
  const r0 = rimR - 4;
  const z0 = w.width_mm;
  const B = (q: Pt): Pt => [K * (q[0] - r0), -K * (q[1] - z0)];
  const X = (r: number) => K * (r - r0);
  const Y = (z: number) => -K * (z - z0);
  const yBreak = Y(z0 - 9.6);
  const brk = breakPoints([X(R + 1.2), yBreak], [X(r0 - 1.2), yBreak], 0.7, 4);
  const clip = `${id}-clip`;
  const clipD = polygonPath([[X(r0 - 1.2), -4], [X(R + 1.5), -4], ...brk]);

  const seatTop = topAtRadius(hubPts, rimR);
  const boreTop = topAtRadius(t.profile, boreR);
  const treadTop = topAtRadius(t.profile, R);
  const row1 = -5.5;
  const row2 = -13;
  const tail = 11 * p;
  const yRim = Y(seatTop - 1.3);
  const yBore = Y(seatTop - 4);

  return (
    <BlueprintView
      id={id}
      viewBox={DETAIL_B}
      hatch={1.6}
      caption="Detail B · tire on the rim · × 3"
      title="Detail B: tire on the rim"
      desc={
        `Tire on the rim at three times scale. Tread ${fmt(t.tread_mm)} mm; flanges stand ${fmt(w.flange_mm)} mm ` +
        `above the ${fmt(w.rim_od_mm)} mm rim. The tire bore is ${fmt(t.bore_mm)} mm` +
        (t.rim_measured ? `, sized to the printed rim's ${fmt(t.rim_seat_od_mm)} mm seat.` : ".")
      }
    >
      <defs>
        <clipPath id={clip}>
          <path d={clipD} />
        </clipPath>
      </defs>
      <g clipPath={`url(#${clip})`}>
        <Fill d={polygonPath(t.profile, B)} className={TIRE_FILL} />
        <Fill d={polygonsPath(w.hub_section, B)} className="fill-accent-soft" />
        <Fill d={polygonsPath(w.hub_section, B)} fill={hatchUrl(id)} />
        <Outline d={outlinePath(w.hub_section, B, offAxis)} className="text-accent" />
        <Outline d={polygonPath(t.profile, B)} className="text-fg" delay={0.1} />
      </g>
      <Outline
        d={breakPath([X(R + 0.6), yBreak], [X(rimR - 3.6), yBreak], 0.7, 4)}
        tone="context"
        className="text-muted"
        delay={0.2}
      />

      <Fade>
        <Dim
          a={[X(boreR), row1]}
          b={[X(R), row1]}
          p={p}
          ext={[
            [
              [X(R), Y(treadTop) - 1],
              [X(R), row1 - 1.6],
            ],
            [
              [X(boreR), Y(boreTop) - 1],
              [X(boreR), row1 - 1.6],
            ],
          ]}
          at={[X(boreR) - 1.4, row1]}
          anchor="end"
          v="middle"
          label={
            <>
              {fmt(t.tread_mm)}
              <Note> tread</Note>
            </>
          }
        />
        <Dim
          a={[X(rimR), row2]}
          b={[X(flangeR), row2]}
          p={p}
          arrows="outside"
          ext={[
            [
              [X(flangeR), -1],
              [X(flangeR), row2 - 1.6],
            ],
            [
              [X(rimR), Y(seatTop) - 1],
              [X(rimR), row2 - 1.6],
            ],
          ]}
          at={[X(flangeR) + tail + 1.4, row2]}
          anchor="start"
          v="middle"
          label={
            <>
              {fmt(w.flange_mm)}
              <Note> flange</Note>
            </>
          }
        />

        <Leader
          p={p}
          points={[
            [X(rimR), yRim],
            [-3.5, yRim],
          ]}
        />
        <Label at={[-4.5, yRim]} anchor="end">
          Ø{fmt(w.rim_od_mm)}
          <Note> rim, as drawn</Note>
        </Label>
        <Leader
          p={p}
          points={[
            [X(boreR), yBore],
            [-3.5, yBore],
          ]}
        />
        <Label
          at={[-4.5, yBore]}
          anchor="end"
          lines={
            t.rim_measured
              ? [`Ø${fmt(t.bore_mm)} tire bore`, `for the Ø${fmt(t.rim_seat_od_mm)} rim`, "as printed"]
              : [`Ø${fmt(t.bore_mm)} tire bore`]
          }
        />
      </Fade>
    </BlueprintView>
  );
}
