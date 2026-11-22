import type { ClientMessage } from "./protocol";

export type Send = (msg: ClientMessage) => void;

const HEARTBEAT_MS = 100;
const MIN_SEND_MS = 100;
const MIN_DV = 0.02;
const MIN_DW = 0.05;

/** Turns a held joystick into drive, heartbeat and stop messages (CONTROL_APP.md, Safety).
 * Pure logic with an injected clock, so it is tested without timers or a socket. */
export class DriveController {
  private seq = 0;
  private held = false;
  private last: { v: number; w: number; at: number } | null = null;
  private lastBeat = 0;

  constructor(
    private readonly send: Send,
    private readonly limits: { maxW: number; speedLimit: number },
  ) {}

  /** x and y in [-1, 1]: y up is forward, x right is a right turn (negative w). */
  hold(x: number, y: number, now: number): void {
    const v = round(y * this.limits.speedLimit);
    const w = round(-x * this.limits.maxW);
    this.held = true;
    const l = this.last;
    if (l && (now - l.at < MIN_SEND_MS || (Math.abs(v - l.v) < MIN_DV && Math.abs(w - l.w) < MIN_DW))) {
      return;
    }
    this.send({ type: "drive", v, w, seq: this.seq++ });
    this.last = { v, w, at: now };
    this.lastBeat = now;
  }

  tick(now: number): void {
    if (this.held && now - this.lastBeat >= HEARTBEAT_MS) {
      this.send({ type: "heartbeat", seq: this.seq++ });
      this.lastBeat = now;
    }
  }

  release(): void {
    if (!this.held) return;
    this.held = false;
    this.last = null;
    this.send({ type: "stop" });
  }

  setSpeedLimit(speedLimit: number): void {
    this.limits.speedLimit = speedLimit;
  }
}

const round = (n: number) => Math.round(n * 1000) / 1000 + 0; // + 0 turns -0 into 0
