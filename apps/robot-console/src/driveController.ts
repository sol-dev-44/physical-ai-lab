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
  private pending: { v: number; w: number } | null = null;
  private stick = { x: 0, y: 0 };
  private lastBeat = 0;
  private limits: { maxW: number; speedLimit: number };

  constructor(
    private readonly send: Send,
    limits: { maxW: number; speedLimit: number },
  ) {
    this.limits = { ...limits };
  }

  /** x and y in [-1, 1]: y up is forward, x right is a right turn (negative w).
   * Mirrors DriveSession.drive in lab_agent/console/drive.py: a resting finger near the
   * centre is (0, 0), a move to (0, 0) is never delayed, and a change dropped only for
   * timing is kept and sent by tick(), so the wheels never keep an old command. */
  hold(x: number, y: number, now: number): void {
    if (!Number.isFinite(x) || !Number.isFinite(y)) return;
    const r = Math.hypot(x, y);
    const k = r > 1 ? 1 / r : 1;
    this.stick = { x: x * k, y: y * k };
    this.held = true;
    const { v, w } = this.target();
    const l = this.last;
    if (l && !(v === 0 && w === 0 && (l.v !== 0 || l.w !== 0))) {
      if (now - l.at < MIN_SEND_MS) {
        this.pending = { v, w };
        return;
      }
      if (Math.abs(v - l.v) < MIN_DV && Math.abs(w - l.w) < MIN_DW) {
        this.pending = null;
        return;
      }
    }
    this.sendDrive(v, w, now);
  }

  tick(now: number): void {
    if (!this.held) return;
    const l = this.last;
    if (this.pending && (!l || now - l.at >= MIN_SEND_MS)) {
      this.sendDrive(this.pending.v, this.pending.w, now);
    } else if (now - this.lastBeat >= HEARTBEAT_MS) {
      this.send({ type: "heartbeat", seq: this.seq++ });
      this.lastBeat = now;
    }
  }

  release(): void {
    this.pending = null;
    if (!this.held) return;
    this.held = false;
    this.last = null;
    this.send({ type: "stop" });
  }

  /** Replace both limits (the welcome message's). When held, the next tick sends the new target. */
  setLimits(limits: { maxW: number; speedLimit: number }): void {
    this.limits = { ...limits };
    if (this.held) this.pending = this.target();
  }

  setSpeedLimit(speedLimit: number): void {
    this.setLimits({ maxW: this.limits.maxW, speedLimit });
  }

  private target(): { v: number; w: number } {
    let v = round(this.stick.y * this.limits.speedLimit);
    let w = round(-this.stick.x * this.limits.maxW);
    if (Math.abs(v) < MIN_DV && Math.abs(w) < MIN_DW) v = w = 0;
    return { v, w };
  }

  private sendDrive(v: number, w: number, now: number): void {
    this.send({ type: "drive", v, w, seq: this.seq++ });
    this.last = { v, w, at: now };
    this.lastBeat = now;
    this.pending = null;
  }
}

const round = (n: number) => Math.round(n * 1000) / 1000 + 0; // + 0 turns -0 into 0
