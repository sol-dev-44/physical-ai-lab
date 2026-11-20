import "server-only";

import { readFile } from "node:fs/promises";
import path from "node:path";
import { cacheLife } from "next/cache";
import { z } from "zod";

/**
 * Numbers for a build's page, exported from the CAD and the lab docs by a script next to the
 * models (for the household robot: experiments/exp003-household-robot/cad/export_site.py) into
 * content/builds/<slug>.data.json. A Python test fails when that file is stale, and this schema
 * fails the build when its shape changes, so the page cannot drift from the design.
 *
 * Geometry is in millimetres. Section points are [r, z] (radius from the wheel axis, z along it
 * from the servo-side face); cradle points are [a, b] (along the servo case from the shaft axis,
 * across it); base positions are x fore-aft (+ forward, axle at 0) and y across.
 */
const CONTENT_DIR = process.env.CONTENT_DIR ?? path.join(/*turbopackIgnore: true*/ process.cwd(), "../../content");

const point = z.tuple([z.number(), z.number()]);
const text = z.string();

const horn = z.strictObject({
  od_mm: z.number(),
  thickness_mm: z.number(),
  bolt_count: z.number().int(),
  bolt_circle_mm: z.number(),
  bolt_size: text,
  center_head_mm: z.number(),
  center_head_height_mm: z.number(),
  shaft_height_mm: z.number(),
  raised_case_mm: z.number(),
});

const servoCase = z.strictObject({
  length_mm: z.number(),
  width_mm: z.number(),
  shaft_to_near_end_mm: z.number(),
  holes_along_mm: z.number(),
  holes_across_mm: z.number(),
  holes_near_offset_mm: z.number(),
  bottom_holes_along_mm: z.number(),
  bottom_holes_across_mm: z.number(),
  height_shaft_end_mm: z.number(),
  height_far_end_mm: z.number(),
  bottom_disc_od_mm: z.number(),
  bottom_disc_proud_mm: z.number(),
  bottom_step_mm: z.number(),
  bottom_step_from_mm: z.number(),
  bottom_keepout_from_mm: z.number(),
  bottom_keepout_to_mm: z.number(),
  bottom_keepout_half_width_mm: z.number(),
  bottom_keepout_proud_mm: z.number(),
  mount_screw_length_mm: z.number().int(),
  max_screw_depth_mm: z.number(),
});

export const BuildData = z.strictObject({
  slug: text,
  source: text,
  wheel: z.strictObject({
    od_mm: z.number(),
    width_mm: z.number(),
    rim_od_mm: z.number(),
    rim_wall_mm: z.number(),
    flange_mm: z.number(),
    flange_land_mm: z.number(),
    web_mm: z.number(),
    screw: text,
    counterbore_diameter_mm: z.number(),
    counterbore_depth_mm: z.number(),
    hole_diameter_mm: z.number(),
    center_pocket_diameter_mm: z.number(),
    center_pocket_depth_mm: z.number(),
    case_gap_mm: z.number(),
    lightening_holes: z.number().int(),
    lightening_radius_mm: z.number(),
    lightening_diameter_mm: z.number(),
    /** Half section of the hub through a bolt hole: one polygon per solid region. */
    hub_section: z.array(z.array(point)),
  }),
  tire: z.strictObject({
    od_mm: z.number(),
    rim_seat_od_mm: z.number(),
    /** True when the bore is sized to a caliper reading of the printed rim, not the design. */
    rim_measured: z.boolean(),
    bore_mm: z.number(),
    lip_bore_mm: z.number(),
    tread_mm: z.number(),
    over_flange_mm: z.number(),
    grip_stretch: z.number(),
    mount_stretch: z.number(),
    profile: z.array(point),
  }),
  cradle: z.strictObject({
    a_min_mm: z.number(),
    a_max_mm: z.number(),
    b_inner_mm: z.number(),
    b_outer_mm: z.number(),
    wall_mm: z.number(),
    pad_mm: z.number(),
    pad_diameter_mm: z.number(),
    cheek_mm: z.number(),
    cheek_height_mm: z.number(),
    ear_length_mm: z.number(),
    ear_mm: z.number(),
    holes: z.array(point),
    hole_diameter_mm: z.number(),
    disc_opening_radius_mm: z.number(),
    /** [a from, a to, half width] of the connector window. */
    window: z.tuple([z.number(), z.number(), z.number()]),
    throat_half_width_mm: z.number(),
    screw_depth_mm: z.number(),
    axle_above_foot_mm: z.number(),
  }),
  servo: z.strictObject({ model: text, horn, case: servoCase, measured_note: text }),
  base: z.strictObject({
    cradle_back_y_mm: z.number(),
    wheel_inner_y_mm: z.number(),
    track_mm: z.number(),
    width_over_tires_mm: z.number(),
    plate_half_width_mm: z.number(),
    plate_length_mm: z.number(),
    com_x_mm: z.number(),
    com_x_with_arm_mm: z.number(),
    caster_share: z.number(),
    masses: z.array(z.strictObject({ name: text, kg: z.number(), x_mm: z.number(), source: text })),
    battery_mm: z.tuple([z.number(), z.number(), z.number()]),
    battery_x_mm: z.number(),
    front_mm: z.number(),
    back_mm: z.number(),
    caster_x_mm: z.number(),
    electronics_x_mm: z.tuple([z.number(), z.number()]),
    arm_base_x_mm: z.number(),
    arm_kg: z.number(),
    arm_reach_com_mm: z.number(),
  }),
  printed: z.array(z.strictObject({ item: text, qty: text, status: text, notes: text })),
  petg_used_g: z.number(),
  consumables: z.strictObject({
    stock: z.array(
      z.strictObject({ item: text, start: text, used: text, left: text, planned: text, reorder: text, lead_time: text }),
    ),
    usage: z.array(z.strictObject({ date: text, what: text, used: text })),
  }),
  bom: z.array(z.strictObject({ n: z.number().int(), item: text, asin: text, check: text, group: text })),
  phases: z.array(
    z.strictObject({ track: z.enum(["v1", "v2"]), n: z.number().int(), phase: text, done_when: text }),
  ),
  timeline: z.array(z.strictObject({ date: z.iso.date(), text })),
  design: z.strictObject({
    tire: z.record(z.string(), z.union([z.number(), z.null()])),
    cradle: z.record(z.string(), z.union([z.number(), z.string()])),
  }),
});

export type BuildData = z.output<typeof BuildData>;

/** The data file for a build, or null when the build has none (a plain write-up). */
export async function getBuildData(slug: string): Promise<BuildData | null> {
  "use cache";
  cacheLife("max");
  let raw: string;
  try {
    raw = await readFile(path.join(CONTENT_DIR, "builds", `${slug}.data.json`), "utf8");
  } catch {
    return null;
  }
  const parsed = BuildData.safeParse(JSON.parse(raw));
  if (!parsed.success) {
    const why = parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ");
    throw new Error(`content/builds/${slug}.data.json: ${why}. Re-run the build's export script.`);
  }
  return parsed.data;
}
