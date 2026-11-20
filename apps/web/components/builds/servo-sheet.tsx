import type { ReactNode } from "react";
import { Reveal } from "@/components/motion/reveal";
import type { BuildData } from "@/lib/builds/data";
import { mm, num } from "@/lib/builds/view";

type Row = { label: string; value: ReactNode; hint?: string };

const x = " × ";

/** The wheel servo's horn and case as a compact spec sheet, with where the numbers came from. */
export function ServoSheet({ servo }: { servo: BuildData["servo"] }) {
  const { horn: h, case: c } = servo;
  const horn: Row[] = [
    { label: "Outside diameter", value: mm(h.od_mm, 2) },
    { label: "Thickness", value: mm(h.thickness_mm, 2) },
    { label: "Bolts", value: `${h.bolt_count}${x}${h.bolt_size} on ${mm(h.bolt_circle_mm, 2)}`, hint: "bolt circle" },
    {
      label: "Centre screw head",
      value: `Ø${mm(h.center_head_mm, 2)}, ${mm(h.center_head_height_mm, 2)} proud`,
    },
    { label: "Horn top to case", value: mm(h.shaft_height_mm, 2), hint: "right round the shaft" },
    { label: "Horn top to raised block", value: mm(h.raised_case_mm, 2), hint: "beside the horn" },
  ];
  const body: Row[] = [
    { label: "Length × width", value: `${num(c.length_mm)}${x}${mm(c.width_mm, 2)}` },
    { label: "Height", value: `${num(c.height_shaft_end_mm)} / ${mm(c.height_far_end_mm, 2)}`, hint: "shaft end / far end" },
    { label: "Shaft to near end", value: mm(c.shaft_to_near_end_mm, 2) },
    {
      label: "Top holes",
      value: `${num(c.holes_along_mm)}${x}${mm(c.holes_across_mm, 2)}`,
      hint: `centre to centre; near pair ${mm(c.holes_near_offset_mm, 2)} from the shaft`,
    },
    { label: "Bottom holes", value: `${num(c.bottom_holes_along_mm)}${x}${mm(c.bottom_holes_across_mm, 2)}`, hint: "centre to centre" },
    {
      label: "Idler disc",
      value: `Ø${mm(c.bottom_disc_od_mm, 2)}, ${mm(c.bottom_disc_proud_mm, 2)} proud`,
      hint: "on the bottom, on the shaft axis",
    },
    {
      label: "Bottom step",
      value: mm(c.bottom_step_mm, 2),
      hint: `from ${mm(c.bottom_step_from_mm, 2)} along to the far end`,
    },
    {
      label: "Connectors and pad",
      value: `${num(c.bottom_keepout_from_mm)} to ${mm(c.bottom_keepout_to_mm, 2)} along`,
      hint: `±${mm(c.bottom_keepout_half_width_mm, 2)} across, ${mm(c.bottom_keepout_proud_mm, 2)} proud of the step`,
    },
    {
      label: "Mount screws",
      value: `${mm(c.mount_screw_length_mm)} long`,
      hint: `at most ${mm(c.max_screw_depth_mm, 2)} into the case`,
    },
  ];

  return (
    <Reveal>
      <div className="overflow-hidden rounded-card border border-line bg-surface shadow-card">
        <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-line bg-surface-2/60 px-5 py-3">
          <p className="font-mono text-xs tracking-[0.14em] text-subtle uppercase">Spec sheet</p>
          <p className="font-medium">{servo.model}</p>
        </div>
        <div className="grid md:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] md:divide-x md:divide-line">
          <Group title="Horn" rows={horn} />
          <Group title="Case" rows={body} />
        </div>
        <div className="flex gap-3 border-t border-line px-5 py-4 text-sm">
          <span className="mt-0.5 shrink-0 rounded-full bg-info-soft px-2 py-0.5 font-mono text-[0.6875rem] font-medium tracking-wide text-info uppercase">
            Lab vs model
          </span>
          <p className="text-muted">{servo.measured_note}</p>
        </div>
      </div>
    </Reveal>
  );
}

function Group({ title, rows }: { title: string; rows: Row[] }) {
  return (
    <div className="px-5 py-4">
      <p className="text-sm font-semibold tracking-tight">{title}</p>
      <dl className="mt-2 divide-y divide-line">
        {rows.map((r) => (
          <div key={r.label} className="grid grid-cols-[minmax(0,1fr)_auto] gap-x-4 py-2 text-sm">
            <dt className="text-muted">
              {r.label}
              {r.hint ? <span className="block text-xs text-subtle">{r.hint}</span> : null}
            </dt>
            <dd className="text-right font-mono text-fg tabular-nums">{r.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
