import "server-only";

import { readFile } from "node:fs/promises";
import path from "node:path";
import { cacheLife } from "next/cache";
import { z } from "zod";

/**
 * Numbers for the Tessera bench storage drawings, exported from the CAD by
 * bench/tessera/export_site.py into content/bench/tessera.data.json. A Python test fails when that
 * file is stale, and this schema fails the build when its shape changes.
 *
 * Plan coordinates are millimetres: x across the bench (+ right), y depth (+ back). Joint points
 * are centred on the line between two modules, u (across that line) first.
 */
const CONTENT_DIR = process.env.CONTENT_DIR ?? path.join(/*turbopackIgnore: true*/ process.cwd(), "../../content");

const point = z.tuple([z.number(), z.number()]);

const Module = z.strictObject({
  name: z.string(),
  col: z.number().int(),
  row: z.number().int(),
  nx: z.number().int(),
  ny: z.number().int(),
  height_mm: z.number(),
  material: z.enum(["PLA", "PETG"]),
  status: z.enum(["planned", "printed"]),
});
export type TesseraModule = z.output<typeof Module>;

export const TesseraData = z.strictObject({
  source: z.string(),
  grid: z.strictObject({
    unit_mm: z.number(),
    gap_mm: z.number(),
    wall_mm: z.number(),
    height_step_mm: z.number(),
    corner_r_mm: z.number(),
    cup_mm: z.number(),
  }),
  joint: z.strictObject({
    neck_mm: z.number(),
    end_mm: z.number(),
    depth_mm: z.number(),
    reach_mm: z.number(),
    flank_deg: z.number(),
    boss_width_mm: z.number(),
    boss_depth_mm: z.number(),
    key_clearance_mm: z.number(),
    rib_radius_mm: z.number(),
    rib_interference_mm: z.number(),
    socket: z.array(point).length(6),
    key: z.array(point).length(6),
    ribs: z.array(point).length(4),
    cup_sockets: z.array(point),
  }),
  layout: z.strictObject({
    cols: z.number().int(),
    rows: z.number().int(),
    mat_mm: point,
    modules: z.array(Module),
  }),
});
export type TesseraData = z.output<typeof TesseraData>;

export async function getTesseraData(): Promise<TesseraData> {
  "use cache";
  cacheLife("max");
  const raw = await readFile(path.join(CONTENT_DIR, "bench", "tessera.data.json"), "utf8");
  const parsed = TesseraData.safeParse(JSON.parse(raw));
  if (!parsed.success) {
    const why = parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ");
    throw new Error(`content/bench/tessera.data.json: ${why}. Re-run bench/tessera/export_site.py.`);
  }
  return parsed.data;
}
