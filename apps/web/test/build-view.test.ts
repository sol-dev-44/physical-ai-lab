import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it, vi } from "vitest";

vi.mock("server-only", () => ({}));
vi.mock("next/cache", () => ({ cacheLife: () => {} }));

const { BuildData } = await import("../lib/builds/data");
const view = await import("../lib/builds/view");

const file = path.join(__dirname, "../../../content/builds/household-robot.data.json");
const data = BuildData.parse(JSON.parse(readFileSync(file, "utf8")));

describe("build view helpers", () => {
  it("computes the hero stats from the data", () => {
    const stats = view.heroStats(data);
    expect(stats.map((s) => s.label)).toEqual([
      "Width over the tires",
      "Wheel diameter",
      "Centre of mass behind the axle",
      "Parts printed",
      "PETG used",
    ]);
    expect(stats[0]?.value).toBe(view.mm(data.base.width_over_tires_mm));
    expect(stats[2]?.value).toBe(view.mm(Math.abs(data.base.com_x_mm)));
    expect(stats[3]?.value).toBe(String(view.printedCount(data)));
  });

  it("joins printed parts to the usage log and adds up to petg_used_g", () => {
    const cards = view.printedCards(data);
    expect(cards).toHaveLength(data.printed.length);
    const total = cards.reduce((g, c) => g + (c.grams ?? 0), 0);
    expect(total).toBeCloseTo(data.petg_used_g, 1);
    expect(cards.every((c) => c.dates.length > 0)).toBe(true);
  });

  it("reads PETG spools from the stock table", () => {
    const s = view.petgSpools(data);
    expect(s?.capacity).toBe(1000);
    expect(s?.used).toBe(data.petg_used_g);
    expect(s?.sealed).toBe(1000);
  });

  it("parses free-text cells", () => {
    expect(view.parseGrams("about 846 g")).toBe(846);
    expect(view.parseGrams("1,000 g")).toBe(1000);
    expect(view.parseGrams("On order")).toBeNull();
    expect(view.materialGrams("PETG 10.0 g; 4 x M2 x 6", "PETG")).toBe(10);
    expect(view.asins("B07426WCLM, B0DNCJRX18")).toEqual(["B07426WCLM", "B0DNCJRX18"]);
    expect(view.parseNumberList("0, 1")).toEqual([0, 1]);
  });

  it("groups the timeline by day", () => {
    const groups = view.groupByDate(data.timeline);
    expect(groups.reduce((n, g) => n + g.items.length, 0)).toBe(data.timeline.length);
    expect(groups[0]?.day).toBe(1);
  });

  it("looks values up by path and fails loudly on a typo", () => {
    expect(view.lookup(data, "tire.bore_mm")).toBe(data.tire.bore_mm);
    expect(view.lookup(data, "cradle.window.0")).toBe(data.cradle.window[0]);
    expect(() => view.lookup(data, "tire.bore")).toThrow(/not in the build data/);
  });
});
