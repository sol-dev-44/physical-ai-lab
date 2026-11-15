/**
 * Turns a run's events into a compact timeline: one tick per event, or per bucket of events
 * for long runs. A bucket shows its most important event (a denial outranks a send).
 */
import type { Event } from "@lab/schema";

export type TickKind = "neutral" | "request" | "allow" | "deny" | "sent" | "failed" | "observed" | "miss" | "note";

const rank: Record<TickKind, number> = {
  neutral: 0,
  request: 1,
  note: 2,
  allow: 3,
  observed: 3,
  sent: 4,
  miss: 5,
  failed: 6,
  deny: 7,
};

export const tickLabel: Record<TickKind, string> = {
  neutral: "run",
  request: "requested",
  allow: "allowed",
  deny: "denied",
  sent: "sent",
  failed: "failed",
  observed: "observed",
  miss: "no effect",
  note: "note",
};

export function tickKind(e: Event): TickKind {
  const p = (e.payload ?? {}) as Record<string, unknown>;
  switch (e.type) {
    case "command.requested":
      return "request";
    case "safety.checked":
      return p.decision === "deny" ? "deny" : "allow";
    case "command.sent":
      return "sent";
    case "command.failed":
      return "failed";
    case "outcome.observed":
      return p.success === false ? "miss" : "observed";
    case "note":
      return "note";
    default:
      return "neutral";
  }
}

export type Tick = { kind: TickKind; from: number; to: number };

/** Group kinds into at most `max` ticks. `from` is inclusive, `to` exclusive (event indexes). */
export function bucket(kinds: TickKind[], max = 240): Tick[] {
  if (kinds.length === 0) return [];
  const size = Math.max(1, Math.ceil(kinds.length / max));
  const ticks: Tick[] = [];
  for (let from = 0; from < kinds.length; from += size) {
    const to = Math.min(kinds.length, from + size);
    let kind: TickKind = "neutral";
    for (let i = from; i < to; i++) if (rank[kinds[i] as TickKind] > rank[kind]) kind = kinds[i] as TickKind;
    ticks.push({ kind, from, to });
  }
  return ticks;
}
