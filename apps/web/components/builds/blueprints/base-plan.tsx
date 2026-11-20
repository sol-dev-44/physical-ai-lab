"use client";

import { m } from "motion/react";
import { useState, type ReactNode } from "react";
import type { BuildData } from "@/lib/builds/data";
import { cn } from "@/lib/design/cn";
import { duration } from "@/lib/design/motion";
import { Fade, Fill, Outline } from "./draw";
import { BlueprintFrame, MassSymbolPaths } from "./frame";
import { fmt, n3, polylinePath, rectPath, type Pt } from "./geometry";
import { Arrowhead, CentreLine, Dim, DASH, Label, Leader, Line, Note, Path } from "./primitives";
import { TIRE_FILL, unitsPerPx, type ViewBox } from "./units";
import { BlueprintView } from "./view";

const PLAN: ViewBox = [-197, -170, 394, 378];
const spring = { type: "spring", duration: duration.slow * 1.4, bounce: 0.2 } as const;

/**
 * Top view of the robot base, front at the top: x fore-aft (+ forward, axle at 0) runs up the
 * page, y across. The toggle moves the centre of mass between v1 and v1 with the v2 arm held at
 * full forward reach, the case that decides whether the robot tips onto its nose.
 */
export function BasePlan({ data }: { data: BuildData }) {
  const [arm, setArm] = useState(false);
  const b = data.base;
  const com = arm ? b.com_x_with_arm_mm : b.com_x_mm;
  const behind = -com;
  const casterShare = arm ? behind / -b.caster_x_mm : b.caster_share;
  const armLabel = `with v2 arm (${fmt(b.arm_kg)} kg at full reach)`;

  const toolbar = (
    <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-3">
      <div role="group" aria-label="Centre of mass case" className="flex flex-wrap items-center gap-2">
        <span className="mr-1 font-mono text-[0.6875rem] tracking-[0.14em] text-subtle uppercase">Centre of mass</span>
        <Toggle pressed={!arm} onClick={() => setArm(false)}>
          v1
        </Toggle>
        <Toggle pressed={arm} onClick={() => setArm(true)}>
          {armLabel}
        </Toggle>
      </div>
      <p aria-live="polite" className="text-sm text-muted">
        <span className="font-mono font-medium text-fg tabular-nums">{fmt(behind, 1)} mm</span> behind the axle; the
        caster carries about <span className="font-mono text-fg tabular-nums">{Math.round(casterShare * 100)}%</span>
      </p>
    </div>
  );

  return (
    <BlueprintFrame
      data={data}
      title="Base, plan view"
      scale="Fit to width"
      sheet="3 / 3"
      toolbar={toolbar}
      legend={[
        { swatch: "part", label: "Plate and cradles (printed)" },
        { swatch: "solid", label: "Tires" },
        { swatch: "context", label: "Battery and servos" },
        { swatch: "hidden", label: "Electronics deck, v2 arm (planned)" },
        { swatch: "centre", label: "Axle, wheel centres" },
        { swatch: "mass", label: "Centre of mass" },
      ]}
      notes={[
        <>
          Centre of mass from the estimated masses:{" "}
          {b.masses.map((ms) => `${ms.name} ${fmt(ms.kg)} kg`).join(", ")}. The v2 arm adds {fmt(b.arm_kg)} kg{" "}
          {fmt(b.arm_reach_com_mm)} mm ahead of its base.
        </>,
        <>
          Electronics deck {fmt(-b.electronics_x_mm[0])} to {fmt(-b.electronics_x_mm[1])} mm behind the axle; caster{" "}
          {fmt(-b.caster_x_mm)} mm; v2 arm base {fmt(-b.arm_base_x_mm)} mm. The caster and arm are marked by position
          only.
        </>,
      ]}
    >
      <Plan data={data} arm={arm} />
    </BlueprintFrame>
  );
}

function Toggle({ pressed, onClick, children }: { pressed: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      aria-pressed={pressed}
      onClick={onClick}
      className={cn(
        "inline-flex min-h-11 items-center rounded-control border px-3.5 text-left text-sm font-medium",
        "transition-colors duration-fast ease-out-quint",
        pressed ? "border-accent bg-accent-soft text-accent" : "border-line-strong bg-surface text-fg hover:border-fg",
      )}
    >
      {children}
    </button>
  );
}

function Plan({ data, arm }: { data: BuildData; arm: boolean }) {
  const b = data.base;
  const c = data.cradle;
  const horn = data.servo.horn;
  const p = unitsPerPx(PLAN);
  // Screen: X across, Y = −x, so forward is up and the axle runs across at Y = 0.
  const Y = (x: number) => -x;
  const pw = b.plate_half_width_mm;
  const wi = b.wheel_inner_y_mm;
  const ww = data.wheel.width_mm;
  const wr = data.wheel.od_mm / 2;
  const wc = wi + ww / 2;
  const wo = wi + ww;
  const cb = b.cradle_back_y_mm;
  const step = cb + c.wall_mm + c.pad_mm;
  const caseTop = wi - horn.shaft_height_mm;
  const cradleTop = step + c.cheek_height_mm;
  const [bw, bl] = b.battery_mm;
  const [e0, e1] = b.electronics_x_mm;
  const front = Y(b.front_mm);
  const back = Y(b.back_mm);
  const comY = Y(arm ? b.com_x_with_arm_mm : b.com_x_mm);
  const armY = Y(b.arm_base_x_mm + b.arm_reach_com_mm);
  const sides = [-1, 1] as const;

  const rowT = front - 18;
  const rowW = front - 40;
  const dimX = -(wo + 9.5);
  const leadOut = Math.round(-wr - 5);

  return (
    <BlueprintView
      id="bp-base"
      viewBox={PLAN}
      className="mx-auto max-w-[38rem]"
      caption="Plan · front at the top"
      title="Robot base, plan view"
      desc={
        `Top view of the base, front at the top. ${fmt(b.width_over_tires_mm)} mm over the tires, track ` +
        `${fmt(b.track_mm)} mm. Plate ${fmt(b.plate_length_mm)} by ${fmt(2 * pw)} mm, from ${fmt(b.front_mm)} mm ` +
        `ahead of the axle to ${fmt(-b.back_mm)} mm behind. Battery ${fmt(bw)} by ${fmt(bl)} mm across the robot, ` +
        `centred ${fmt(-b.battery_x_mm)} mm behind the axle; caster ${fmt(-b.caster_x_mm)} mm behind. ` +
        `Centre of mass ${fmt(-b.com_x_mm, 1)} mm behind the axle, or ${fmt(-b.com_x_with_arm_mm, 1)} mm with the ` +
        `v2 arm at full reach.`
      }
    >
      <Fill d={rectPath(-pw, front, pw, back)} className="fill-accent-soft/60" />
      <Outline d={rectPath(-pw, front, pw, back)} className="text-accent" />

      {sides.map((s) => (
        <g key={s}>
          <Fill d={rectPath(s * wi, -wr, s * wo, wr)} className={TIRE_FILL} />
          <Outline d={rectPath(s * wi, -wr, s * wo, wr)} className="text-fg" delay={0.1} />
          <Fill d={rectPath(s * step, Y(-c.a_min_mm), s * caseTop, Y(-c.a_max_mm))} className="fill-surface-2" />
          <Outline
            d={rectPath(s * step, Y(-c.a_min_mm), s * caseTop, Y(-c.a_max_mm))}
            tone="context"
            className="text-muted"
            delay={0.15}
          />
          <Outline
            d={rectPath(s * (wi - horn.thickness_mm), -horn.od_mm / 2, s * wi, horn.od_mm / 2)}
            tone="context"
            className="text-muted"
            delay={0.2}
          />
          <Fill
            d={rectPath(s * cb, Y(-c.a_min_mm + c.ear_length_mm), s * cradleTop, Y(-c.a_max_mm - c.ear_length_mm))}
            className="fill-accent-soft"
          />
          <Outline
            d={rectPath(s * cb, Y(-c.a_min_mm + c.ear_length_mm), s * cradleTop, Y(-c.a_max_mm - c.ear_length_mm))}
            className="text-accent"
            delay={0.2}
          />
        </g>
      ))}

      <Fill d={rectPath(-bw / 2, Y(b.battery_x_mm + bl / 2), bw / 2, Y(b.battery_x_mm - bl / 2))} className="fill-surface-2" />
      <Outline
        d={rectPath(-bw / 2, Y(b.battery_x_mm + bl / 2), bw / 2, Y(b.battery_x_mm - bl / 2))}
        tone="context"
        className="text-muted"
        delay={0.25}
      />

      <Fade>
        <g className="text-muted">
          {sides.map((s) => (
            <g key={s}>
              <Line a={[s * cb, Y(-c.a_min_mm)]} b={[s * cradleTop, Y(-c.a_min_mm)]} className="text-accent" />
              <Line a={[s * cb, Y(-c.a_max_mm)]} b={[s * cradleTop, Y(-c.a_max_mm)]} className="text-accent" />
            </g>
          ))}
          <Path d={rectPath(-(pw - 8), Y(e0), pw - 8, Y(e1))} dash="hidden" />
          <circle cx={0} cy={n3(Y(b.caster_x_mm))} r={12} className="fill-surface-2" stroke="currentColor" strokeWidth={1} vectorEffect="non-scaling-stroke" />
          <Line a={[-17, Y(b.caster_x_mm)]} b={[17, Y(b.caster_x_mm)]} />
          <Line a={[0, Y(b.caster_x_mm) - 17]} b={[0, Y(b.caster_x_mm) + 17]} />
          <circle
            cx={0}
            cy={n3(Y(b.arm_base_x_mm))}
            r={12}
            fill="none"
            stroke="currentColor"
            strokeWidth={1}
            strokeDasharray={DASH.phantom}
            vectorEffect="non-scaling-stroke"
          />
          <Line a={[-17, Y(b.arm_base_x_mm)]} b={[17, Y(b.arm_base_x_mm)]} />
        </g>

        <CentreLine a={[-(wo + 18), 0]} b={[wo + 18, 0]} />
        {sides.map((s) => (
          <CentreLine key={s} a={[s * wc, -wr - 10]} b={[s * wc, wr + 10]} />
        ))}

        <Label at={[-90, 0]} v="above" tone="muted">
          axle
        </Label>
        <Label at={[-bw / 2 + 4, Y(b.battery_x_mm) + 4]} lines={["battery", `${fmt(bw)} × ${fmt(bl)}`]} />
        <Label at={[-(pw - 14), Y(e0) + 12]} tone="muted">
          electronics
        </Label>
        <Label at={[18, Y(b.arm_base_x_mm)]} tone="muted">
          v2 arm base
        </Label>
        <Label at={[-18, Y(b.caster_x_mm)]} anchor="end" tone="muted">
          caster
        </Label>
        <Label at={[0, back + 11]} anchor="middle">
          plate {fmt(b.plate_length_mm)} × {fmt(2 * pw)}
        </Label>

        <Leader p={p} end="dot" points={[[wc - 8, leadOut + 19], [118, -80]]} />
        <Label at={[116, -80]} anchor="end">
          Ø{fmt(data.wheel.od_mm)} × {fmt(ww)}
          <Note> wheel</Note>
        </Label>
        <Leader p={p} end="dot" points={[[-(cb + cradleTop) / 2, Y(-c.a_min_mm + c.ear_length_mm) + 4], [-92, -56]]} />
        <Label at={[-90, -56]}>
          servo <Note>in cradle</Note>
        </Label>

        <Dim
          a={[-wc, rowT]}
          b={[wc, rowT]}
          p={p}
          ext={sides.map((s) => [
            [s * wc, -wr - 11],
            [s * wc, rowT - 2],
          ])}
          label={
            <>
              {fmt(b.track_mm)}
              <Note> track</Note>
            </>
          }
        />
        <Dim
          a={[-wo, rowW]}
          b={[wo, rowW]}
          p={p}
          ext={sides.map((s) => [
            [s * wo, -wr - 3],
            [s * wo, rowW - 2],
          ])}
          label={
            <>
              {fmt(b.width_over_tires_mm)}
              <Note> over the tires</Note>
            </>
          }
        />
        <g className="text-muted">
          <Line a={[-185, rowW + 8]} b={[-185, -164]} />
          <Arrowhead tip={[-185, -166]} dir={[0, -1]} p={p} />
        </g>
        <Label at={[-176, -160]} tone="muted">
          front
        </Label>

        <Dim
          a={[dimX, front]}
          b={[dimX, 0]}
          p={p}
          ext={[
            [
              [-pw - 2, front],
              [dimX - 2, front],
            ],
          ]}
          v="above"
          rotate={-90}
          label={
            <>
              {fmt(b.front_mm)}
              <Note> ahead</Note>
            </>
          }
        />
        <Dim
          a={[dimX, 0]}
          b={[dimX, back]}
          p={p}
          ext={[
            [
              [-pw - 2, back],
              [dimX - 2, back],
            ],
          ]}
          v="above"
          rotate={-90}
          label={
            <>
              {fmt(-b.back_mm)}
              <Note> behind</Note>
            </>
          }
        />

        <m.g initial={false} animate={{ opacity: arm ? 1 : 0 }} transition={{ duration: duration.base }}>
          <Path d={polylinePath([[0, Y(b.arm_base_x_mm)], [0, armY]])} dash="phantom" className="text-muted" />
          <circle cx={0} cy={n3(armY)} r={5} className="fill-muted" />
          <Label at={[12, armY]} tone="muted">
            {fmt(b.arm_kg)} kg arm
          </Label>
        </m.g>

        <g className="text-fg">
          <m.line
            x1={22}
            y1={0}
            x2={22}
            initial={false}
            animate={{ y2: comY }}
            transition={spring}
            stroke="currentColor"
            strokeWidth={1}
            vectorEffect="non-scaling-stroke"
          />
          <m.g initial={false} animate={{ y: comY }} transition={spring}>
            <MassSymbolPaths cx={0} cy={0} r={9} />
            <Line a={[11, 0]} b={[26, 0]} />
            <Arrowhead tip={[22, 0] as Pt} dir={[0, 1]} p={p} />
            <Label at={[28, 0]} className="font-medium">
              {fmt(-(arm ? b.com_x_with_arm_mm : b.com_x_mm), 1)}
            </Label>
          </m.g>
        </g>
      </Fade>
    </BlueprintView>
  );
}
