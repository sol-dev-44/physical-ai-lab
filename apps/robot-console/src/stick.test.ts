import { stickVector } from "./stick";

const rect = { left: 0, top: 0, width: 200, height: 200 };

describe("stickVector", () => {
  it("is zero at the centre", () => {
    expect(stickVector(rect, 100, 100)).toEqual({ x: 0, y: 0 });
  });
  it("points up as +y and right as +x", () => {
    expect(stickVector(rect, 100, 0)).toEqual({ x: 0, y: 1 });
    expect(stickVector(rect, 200, 100)).toEqual({ x: 1, y: 0 });
  });
  it("clamps to the unit circle", () => {
    const v = stickVector(rect, 400, 400);
    expect(Math.hypot(v.x, v.y)).toBeCloseTo(1);
  });
});
