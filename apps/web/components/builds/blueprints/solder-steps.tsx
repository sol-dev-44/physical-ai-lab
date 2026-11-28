import type { ReactNode } from "react";
import { Fade, Fill, Outline } from "./draw";
import { BlueprintFrame } from "./frame";
import { polygonPath, rectPath, type Pt } from "./geometry";
import { Dim, Label, Leader } from "./primitives";
import { hatchUrl, unitsPerPx, type ViewBox } from "./units";
import { BlueprintView } from "./view";

/**
 * How one rocker tab was soldered (exp003, 2026-11-27), in four steps. Not drawn from a CAD
 * model: the numbers are the bench method in experiments/exp003-household-robot/HARNESS.md
 * ("Bench method"), kept here as named constants so a change there is one edit here.
 */
const SOURCE = "experiments/exp003-household-robot/HARNESS.md (Bench method)";
const STRIP_MM = 6;
const TUBE_BACK_MM = 50;
const TUBE_LEN_MM = 20;
const TUBE_DIA_MM = 10;
const WIRE_OD_MM = 2.5; // 16 AWG silicone, about
const TAB_W_MM = 4.8;
const IRON_C = 370;

const insulation = "fill-surface-2";
const copper = "fill-accent-soft";
const ironFill = "fill-fg/70 dark:fill-fg/40";

/** A filled band with its outline, for wires, tabs and tubes. */
function Band({ d, fill, line = "text-muted", tone = "context", delay = 0, pattern }: { d: string; fill?: string; line?: string; tone?: "part" | "context"; delay?: number; pattern?: string }) {
  return (
    <>
      <Fill d={d} className={fill} fill={pattern} delay={delay + 0.2} />
      <Outline d={d} className={line} tone={tone} delay={delay} />
    </>
  );
}

export function SolderSteps() {
  return (
    <BlueprintFrame
      data={{ source: SOURCE }}
      title="Soldering a rocker tab"
      scale="Not to scale"
      legend={[
        { swatch: "part", label: "Bare copper, tab" },
        { swatch: "context", label: "Insulation, rocker body" },
        { swatch: "solid", label: "Iron tip" },
        { swatch: "section", label: "Heat-shrink" },
      ]}
      notes={[
        <>Strip with the iron cold; the heat-shrink cannot go on once the joint is made.</>,
        <>
          Iron at {IRON_C} °C for lead-free solder. Wipe the tip on the brass cleaner and tin it until it is silver
          before every joint.
        </>,
        <>Keep the iron on the tab under 3 seconds, so the rocker&apos;s plastic body does not soften.</>,
        <>Check with the multimeter&apos;s beep test: a beep with the switch on, silence with it off.</>,
      ]}
    >
      <div className="grid gap-x-8 gap-y-10 md:grid-cols-2">
        <Prep />
        <Tin />
        <Join />
        <Shrink />
      </div>
    </BlueprintFrame>
  );
}

function Step({ id, viewBox, caption, title, desc, children }: { id: string; viewBox: ViewBox; caption: string; title: string; desc: string; children: ReactNode }) {
  return (
    <BlueprintView id={id} viewBox={viewBox} hatch={viewBox[2] / 70} caption={caption} title={title} desc={desc}>
      {children}
    </BlueprintView>
  );
}

// 1. Prep: side view of a pair, X along the wires.
const PREP: ViewBox = [-4, -19, 118, 45];
function Prep() {
  const p = unitsPerPx(PREP);
  const bare0 = 94;
  const bare1 = bare0 + STRIP_MM;
  const tube1 = bare0 - TUBE_BACK_MM;
  const tube0 = tube1 - TUBE_LEN_MM;
  const r = TUBE_DIA_MM / 2;
  const w = WIRE_OD_MM;
  return (
    <Step
      id="bp-solder-prep"
      viewBox={PREP}
      caption="1 · Prep, iron cold"
      title="Step 1: the pair prepared"
      desc={`Two wires side by side, ${STRIP_MM} mm stripped and twisted together. A ${TUBE_LEN_MM} mm piece of ${TUBE_DIA_MM} mm heat-shrink is slid over both, ${TUBE_BACK_MM} mm back from the bare ends.`}
    >
      <Band d={rectPath(0, -w - 0.1, bare0, -0.1)} fill={insulation} />
      <Band d={rectPath(0, 0.1, bare0, w + 0.1)} fill={insulation} delay={0.05} />
      <Band d={rectPath(bare0, -1.8, bare1, 1.8)} fill={copper} line="text-accent" tone="part" delay={0.2} />
      <Band d={rectPath(tube0, -r, tube1, r)} pattern={hatchUrl("bp-solder-prep")} line="text-accent" tone="part" delay={0.3} />
      <Fade>
        <Dim a={[tube0, -9]} b={[tube1, -9]} p={p} ext={[[[tube0, -r - 1], [tube0, -11]], [[tube1, -r - 1], [tube1, -11]]]} label={`${TUBE_LEN_MM} tube`} />
        <Dim a={[bare0, -9]} b={[bare1, -9]} p={p} arrows="outside" ext={[[[bare0, -3.5], [bare0, -11]], [[bare1, -2.5], [bare1, -11]]]} label={`${STRIP_MM}`} at={[bare1 + 6, -9]} anchor="start" v="middle" />
        <Dim a={[tube1, 10]} b={[bare0, 10]} p={p} ext={[[[tube1, r + 1], [tube1, 12]], [[bare0, w + 1.2], [bare0, 12]]]} label={`${TUBE_BACK_MM} back`} v="below" />
        <Label at={[0, 21]} tone="muted">
          one tube over both wires
        </Label>
      </Fade>
    </Step>
  );
}

// 2. Tin: close side view of the bundle.
const TIN: ViewBox = [-2, -16, 34, 32];
function Tin() {
  const p = unitsPerPx(TIN);
  const w = WIRE_OD_MM;
  const b0 = 10;
  const b1 = b0 + STRIP_MM;
  const iron: Pt[] = [
    [12.3, 1.9],
    [14.1, 1.9],
    [23, 12.5],
    [19, 15.5],
  ];
  const solder: Pt[] = [
    [13.2, -1.9],
    [13.9, -2.3],
    [24.4, -13.6],
    [23.6, -14.3],
  ];
  return (
    <Step
      id="bp-solder-tin"
      viewBox={TIN}
      caption="2 · Tin the bundle"
      title="Step 2: tinning the twisted bundle"
      desc={`The iron, at ${IRON_C} degrees C, touches the bundle from below; the solder goes on the top of the bundle, not on the iron, until the strands turn silver.`}
    >
      <Band d={rectPath(-2, -w - 0.05, b0, -0.05)} fill={insulation} />
      <Band d={rectPath(-2, 0.05, b0, w + 0.05)} fill={insulation} delay={0.05} />
      <Band d={rectPath(b0, -1.8, b1, 1.8)} fill={copper} line="text-accent" tone="part" delay={0.2} />
      <Fill d={polygonPath(iron)} className={ironFill} delay={0.5} />
      <Outline d={polygonPath(iron)} className="text-fg" tone="context" delay={0.4} />
      <Fill d={polygonPath(solder)} className="fill-muted" delay={0.6} />
      <Fade>
        <Leader points={[[19.5, 10], [24, 6.5], [25, 6.5]]} p={p} end="dot" />
        <Label at={[31.5, 6.5]} anchor="end" lines={["iron under", `${IRON_C} °C`]} v="above" />
        <Leader points={[[19, -7.6], [15, -12], [12, -12]]} p={p} end="dot" />
        <Label at={[11.5, -12]} anchor="end">
          solder on top
        </Label>
        <Leader points={[[11.2, 0], [6, 8], [4, 8]]} p={p} end="dot" />
        <Label at={[3.5, 8]} anchor="end" lines={["silver", "strands"]} />
      </Fade>
    </Step>
  );
}

// 3 and 4: the tab face-on, rocker body below.
const TAB: ViewBox = [-16, -30, 40, 46];
const tabTop = -3;
const bodyTop = 8;

function TabAndBundle({ delay = 0 }: { delay?: number }) {
  const w = WIRE_OD_MM;
  return (
    <>
      <Band d={rectPath(-9, bodyTop, TAB_W_MM + 9, 16)} fill={insulation} delay={delay} />
      <Band d={rectPath(0, tabTop, TAB_W_MM, bodyTop)} fill="fill-surface" line="text-accent" tone="part" delay={delay + 0.1} />
      <Band d={rectPath(0.5, tabTop + 0.8, 0.5 + 3.8, bodyTop - 0.8)} fill={copper} line="text-accent" tone="part" delay={delay + 0.25} />
      <Band d={rectPath(0.4 - 0.05, -30, 0.4 + w - 0.15, tabTop + 0.8)} fill={insulation} delay={delay + 0.3} />
      <Band d={rectPath(0.4 + w + 0.05, -30, 0.4 + 2 * w - 0.05, tabTop + 0.8)} fill={insulation} delay={delay + 0.35} />
    </>
  );
}

const TAB_IRON: Pt[] = [
  [4.3, 2.2],
  [4.3, 4.2],
  [21, -4],
  [19.5, -8.5],
];

function Join() {
  const p = unitsPerPx(TAB);
  return (
    <Step
      id="bp-solder-join"
      viewBox={TAB}
      caption="3 · Join flat on the tab"
      title="Step 3: the bundle soldered flat on the tab"
      desc={`The tinned bundle lies flat along the ${TAB_W_MM} mm tab's face; it is too thick for the tab's hole. The iron presses it onto the tab for about 3 seconds, then the wire is held still for 10 seconds.`}
    >
      <TabAndBundle />
      <Band d={rectPath(TAB_W_MM / 2 - TUBE_DIA_MM * 0.31, -30, TAB_W_MM / 2 + TUBE_DIA_MM * 0.31, -23)} pattern={hatchUrl("bp-solder-join")} line="text-accent" tone="part" delay={0.4} />
      <Fill d={polygonPath(TAB_IRON)} className={ironFill} delay={0.6} />
      <Outline d={polygonPath(TAB_IRON)} className="text-fg" tone="context" delay={0.5} />
      <Fade>
        <Label at={[23, -14]} anchor="end" lines={["press 3 s,", "hold still 10 s"]} />
        <Leader points={[[0, 1], [-5, -2], [-6, -2]]} p={p} end="dot" />
        <Label at={[-6.5, -2]} anchor="end" lines={["tab", `${TAB_W_MM} wide`]} />
        <Label at={[TAB_W_MM / 2, 12.5]} anchor="middle" tone="muted">
          rocker
        </Label>
        <Leader points={[[-0.7, -26], [-5, -26], [-6, -26]]} p={p} end="dot" />
        <Label at={[-6.5, -26]} anchor="end" lines={["tube, parked", `${TUBE_BACK_MM} up`]} />
      </Fade>
    </Step>
  );
}

function Shrink() {
  const p = unitsPerPx(TAB);
  const r = TUBE_DIA_MM / 2;
  const cx = TAB_W_MM / 2;
  const tubeTop = bodyTop - TUBE_LEN_MM;
  return (
    <Step
      id="bp-solder-shrink"
      viewBox={TAB}
      caption="4 · Slide down, shrink"
      title="Step 4: heat-shrink over the joint"
      desc={`Once cool, the ${TUBE_LEN_MM} mm tube slides down over the tab and joint to the rocker body, and the heat gun shrinks it from 3 to 5 cm away, kept moving.`}
    >
      <TabAndBundle />
      <Band d={rectPath(cx - r * 0.62, tubeTop, cx + r * 0.62, bodyTop)} pattern={hatchUrl("bp-solder-shrink")} line="text-accent" tone="part" delay={0.4} />
      <Fade>
        {[-8, -3, 2].map((y) => (
          <path
            key={y}
            d={`M22 ${y} q-1.5 -1.2 -3 0 t-3 0 t-3 0`}
            fill="none"
            stroke="currentColor"
            strokeWidth={1}
            vectorEffect="non-scaling-stroke"
            className="text-accent"
          />
        ))}
        <Label at={[23, -15]} anchor="end" lines={["heat gun", "3 to 5 cm,", "keep moving"]} />
        <Dim
          a={[-6, bodyTop]}
          b={[-6, tubeTop]}
          p={p}
          ext={[
            [[cx - r * 0.62 - 1, tubeTop], [-7.5, tubeTop]],
            [[-8.5, bodyTop], [-7.5, bodyTop]],
          ]}
          label={`${TUBE_LEN_MM}`}
          at={[-7.2, (bodyTop + tubeTop) / 2]}
          rotate={-90}
          v="above"
        />
        <Label at={[TAB_W_MM / 2, 12.5]} anchor="middle" tone="muted">
          rocker
        </Label>
      </Fade>
    </Step>
  );
}
