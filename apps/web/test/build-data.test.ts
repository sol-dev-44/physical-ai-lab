import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it, vi } from "vitest";

vi.mock("server-only", () => ({}));
vi.mock("next/cache", () => ({ cacheLife: () => {} }));

const { BuildData } = await import("../lib/builds/data");

const file = path.join(__dirname, "../../../content/builds/household-robot.data.json");

describe("household robot build data", () => {
  it("matches the schema the Builds page reads", () => {
    const parsed = BuildData.safeParse(JSON.parse(readFileSync(file, "utf8")));
    expect(parsed.success ? [] : parsed.error.issues).toEqual([]);
  });

  it("keeps the numbers the page leads with", () => {
    const data = BuildData.parse(JSON.parse(readFileSync(file, "utf8")));
    expect(data.wheel.od_mm).toBe(120);
    expect(data.base.com_x_mm).toBeLessThan(0); // centre of mass behind the axle
    expect(data.bom).toHaveLength(30);
  });
});
