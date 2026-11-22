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
    c.hold(0.5, 1, 0);
    expect(sent[0]).toMatchObject({ type: "drive", v: 0.2, w: -0.75 });
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
});
