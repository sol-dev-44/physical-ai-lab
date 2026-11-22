import { DriveController } from "./driveController";
import type { ClientMessage } from "./protocol";

function rig() {
  const sent: ClientMessage[] = [];
  const c = new DriveController((m) => sent.push(m), { maxW: 1.5, speedLimit: 0.2 });
  return { c, sent, types: () => sent.map((m) => m.type) };
}

describe("DriveController", () => {
  it("maps the stick to speed and turn rate: up is forward, right turns right", () => {
    const { c, sent } = rig();
    c.hold(0.6, 0.8, 0); // on the unit circle, so not scaled by the clamp
    expect(sent[0]).toMatchObject({ type: "drive", v: 0.16, w: -0.9 });
  });

  it("sends drive at most every 100 ms, and only on a real change", () => {
    const { c, types } = rig();
    c.hold(0, 0.5, 0);
    c.hold(0, 1, 50); // too soon
    c.hold(0, 1, 120); // sent
    c.hold(0, 1.01, 250); // too small a change
    expect(types().filter((t) => t === "drive")).toHaveLength(2);
  });

  it("sends a heartbeat every 100 ms while held, and none after release", () => {
    const { c, types } = rig();
    c.hold(0, 0.5, 0);
    c.tick(100);
    c.tick(200);
    c.release();
    c.tick(300);
    expect(types()).toEqual(["drive", "heartbeat", "heartbeat", "stop"]);
  });

  it("numbers every message so the robot can spot gaps", () => {
    const { c, sent } = rig();
    c.hold(0, 0.5, 0);
    c.tick(100);
    const seqs = sent.flatMap((m) => ("seq" in m ? [m.seq] : []));
    expect(seqs).toEqual([0, 1]);
  });

  it("sends (0, 0) at once when the stick is centred inside the 100 ms window", () => {
    const { c, sent } = rig();
    c.hold(0, 1, 0);
    c.hold(0, 0, 60);
    expect(sent[1]).toMatchObject({ type: "drive", v: 0, w: 0 });
  });

  it("sends a final position dropped for timing on the next tick, as a drive", () => {
    const { c, sent } = rig();
    c.hold(0, 0.5, 0);
    c.hold(0, 1, 40);
    c.tick(100);
    expect(sent.map((m) => m.type)).toEqual(["drive", "drive"]);
    expect(sent[1]).toMatchObject({ v: 0.2 });
  });

  it("does not resurrect a pending change that later turned out too small", () => {
    const { c, types } = rig();
    c.hold(0, 0.5, 0);
    c.hold(0, 1, 40); // pending
    c.hold(0, 0.5, 150); // back to what was sent: too small, clears pending
    c.tick(250);
    expect(types()).toEqual(["drive", "heartbeat"]);
  });

  it("snaps a finger resting near the centre to a (0, 0) drive, like the server", () => {
    const { c, sent } = rig();
    c.hold(0, 0.15, 0); // v = 0.03
    c.hold(0, 0.06, 200); // v = 0.012, a change of 0.018 < 0.02
    expect(sent[1]).toMatchObject({ type: "drive", v: 0, w: 0 });
  });

  it("sends a slower drive on the next tick after the speed limit is lowered while held", () => {
    const { c, sent } = rig();
    c.hold(0, 1, 0);
    c.setSpeedLimit(0.05);
    c.tick(100);
    expect(sent[1]).toMatchObject({ type: "drive", v: 0.05 });
  });

  it("setLimits replaces both limits and, when held, sends the new target on the next tick", () => {
    const { c, sent } = rig();
    c.hold(0, 1, 0);
    c.setLimits({ maxW: 0.5, speedLimit: 0.1 });
    c.tick(100);
    expect(sent[1]).toMatchObject({ type: "drive", v: 0.1, w: 0 });
    c.hold(1, 0, 200);
    expect(sent[2]).toMatchObject({ type: "drive", v: 0, w: -0.5 });
  });

  it("setLimits while not held sends nothing", () => {
    const { c, sent } = rig();
    c.setLimits({ maxW: 0.5, speedLimit: 0.1 });
    c.tick(100);
    expect(sent).toEqual([]);
  });

  it("does not let the caller's limits object change the controller", () => {
    const limits = { maxW: 1.5, speedLimit: 0.2 };
    const sent: ClientMessage[] = [];
    const c = new DriveController((m) => sent.push(m), limits);
    limits.speedLimit = 5;
    c.hold(0, 1, 0);
    expect(sent[0]).toMatchObject({ v: 0.2 });
  });

  it("ignores non-finite input", () => {
    const { c, sent } = rig();
    c.hold(NaN, 0, 0);
    c.hold(0, Infinity, 10);
    expect(sent).toEqual([]);
  });

  it("clamps the stick to the unit circle", () => {
    const { c, sent } = rig();
    c.hold(1.2, 1.2, 0);
    const m = sent[0];
    if (m?.type !== "drive") throw new Error("expected a drive");
    expect(Math.abs(m.v)).toBeLessThanOrEqual(0.2);
    expect(Math.abs(m.w)).toBeLessThanOrEqual(1.5);
  });

  it("treats hold after release as a fresh press", () => {
    const { c, types } = rig();
    c.hold(0, 1, 0);
    c.release();
    c.hold(0, 0.9, 10);
    c.tick(110);
    expect(types()).toEqual(["drive", "stop", "drive", "heartbeat"]);
  });

  it("release clears a pending change", () => {
    const { c, types } = rig();
    c.hold(0, 0.5, 0);
    c.hold(0, 1, 40);
    c.release();
    c.tick(200);
    expect(types()).toEqual(["drive", "stop"]);
  });
});
