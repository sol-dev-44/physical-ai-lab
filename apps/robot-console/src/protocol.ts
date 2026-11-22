// Mirror of services/lab-agent/src/lab_agent/console/protocol.py. Change both together;
// both test against packages/schema/fixtures/console.
import { z } from "zod";

// z.number() already rejects NaN and Infinity and never coerces strings, matching the strict,
// finite Python models.
const seq = z.number().int().min(0).max(2 ** 53 - 1);

export const ClientMessage = z.discriminatedUnion("type", [
  z.strictObject({ type: z.literal("hello"), token: z.string().min(1).max(256) }),
  z.strictObject({ type: z.literal("drive"), v: z.number(), w: z.number(), seq }),
  z.strictObject({ type: z.literal("heartbeat"), seq }),
  z.strictObject({ type: z.literal("stop") }),
]);
export type ClientMessage = z.infer<typeof ClientMessage>;

const count = z.number().int().min(0).max(2 ** 31 - 1); // ids and millimetres
const nullableInt = count.nullable();

export const State = z.strictObject({
  type: z.literal("state"),
  t: z.number(),
  fake: z.boolean(),
  battery: z.strictObject({
    volts: z.number(),
    amps: z.number(),
    soc_pct: z.number(),
    runtime_min: z.number(),
  }),
  servos: z.array(
    z.strictObject({ id: count, temp_c: z.number(), load_pct: z.number(), volts: z.number() }),
  ),
  tof: z.strictObject({ left_mm: nullableInt, center_mm: nullableInt, right_mm: nullableInt }),
  cliff_mm: z.array(nullableInt),
  bumpers: z.array(z.boolean()),
  wifi_dbm: z.number().nullable(),
  pi_temp_c: z.number().nullable(),
  lease_alive: z.boolean(),
  moving: z.boolean(),
  estop: z.boolean(),
  stop_file: z.boolean(),
  controller: z.strictObject({ connected: z.boolean(), battery_pct: z.number().nullable().optional() }),
});
export type State = z.infer<typeof State>;

export const Welcome = z.strictObject({
  type: z.literal("welcome"),
  run_id: z.string(),
  max_v: z.number(),
  max_w: z.number(),
  lease_s: z.number(),
});
export type Welcome = z.infer<typeof Welcome>;

export const Refused = z.strictObject({
  type: z.literal("refused"),
  rule: z.string(),
  reason: z.string().optional(),
});
export type Refused = z.infer<typeof Refused>;

export const ServerMessage = z.discriminatedUnion("type", [Welcome, State, Refused]);
export type ServerMessage = z.infer<typeof ServerMessage>;
