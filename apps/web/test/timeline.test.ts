import { readFileSync } from "node:fs";
import path from "node:path";
import { Event } from "@lab/schema";
import { expect, it } from "vitest";
import { type TickKind, bucket, tickKind } from "../lib/replay/timeline";

const fixture = path.join(__dirname, "../../../packages/schema/fixtures/logs/valid/full_run.jsonl");
const events = readFileSync(fixture, "utf8")
  .split("\n")
  .filter((l) => l.trim())
  .map((l) => Event.parse(JSON.parse(l)));

it("classifies the sample run's events", () => {
  expect(events.map(tickKind)).toEqual([
    "neutral", "request", "allow", "sent", "observed", "request", "deny", "request", "allow", "failed", "note", "neutral",
  ]);
});

it("keeps one tick per event when the run is short", () => {
  const ticks = bucket(events.map(tickKind));
  expect(ticks).toHaveLength(12);
  expect(ticks[6]).toEqual({ kind: "deny", from: 6, to: 7 });
});

it("buckets long runs and keeps the most important event in each bucket", () => {
  const kinds = Array.from({ length: 1000 }, (_, i): TickKind => (i === 503 ? "deny" : "request"));
  const ticks = bucket(kinds, 100);
  expect(ticks).toHaveLength(100);
  expect(ticks[50]).toEqual({ kind: "deny", from: 500, to: 510 });
  expect(ticks[49]?.kind).toBe("request");
});
