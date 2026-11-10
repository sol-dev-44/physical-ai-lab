/**
 * Lab event contract, version 0.
 *
 * Every experiment, in any language, writes these events to an append-only
 * JSONL log. Everything downstream (replay, evals, the site) reads only these.
 *
 * Rules:
 * - The envelope is strict: unknown top-level keys are rejected.
 * - Payloads are typed per event type but loose: extra keys are allowed so an
 *   experiment can record more detail without a schema bump.
 * - Breaking changes mean a new version (v: 1) and a new schema file. Never
 *   edit v0 in a way that rejects logs that used to be valid.
 */
import { z } from "zod";

export const SCHEMA_VERSION = 0 as const;

/** ULID: 26 chars, Crockford base32, sortable by time. */
export const Ulid = z.string().regex(/^[0-9A-HJKMNP-TV-Z]{26}$/, "must be a ULID");

/** e.g. exp000-20261109-r1 */
export const RunId = z.string().regex(/^[a-z0-9][a-z0-9-]{2,79}$/, "must be a lowercase slug");

/** e.g. exp000-ir-bridge */
export const ExperimentId = z.string().regex(/^exp[0-9]{3}(-[a-z0-9]+)*$/, "must look like exp000-name");

/** Dotted tool name from the registry, e.g. fan.power, robot.forward */
export const ToolName = z
  .string()
  .regex(/^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$/, "must be a dotted tool name");

/** RFC 3339 UTC timestamp with a Z suffix, millisecond precision optional. */
export const Timestamp = z
  .string()
  .regex(/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,6})?Z$/, "must be RFC 3339 UTC (Z)");

export const Actor = z.enum(["human", "cli", "agent", "llm", "replay", "system"]);

const Args = z.record(z.string(), z.unknown());

const envelope = {
  v: z.literal(SCHEMA_VERSION),
  event_id: Ulid,
  run_id: RunId,
  seq: z.int().min(0),
  ts: Timestamp,
  actor: Actor,
  /** Causal parent within the same run, e.g. command.sent -> safety.checked. */
  parent_id: Ulid.optional(),
  device: z.string().min(1).optional(),
};

/** Fields for events that are about one tool call. */
const toolCall = {
  tool: ToolName,
  args: Args,
};

const RunStarted = z.strictObject({
  ...envelope,
  type: z.literal("run.started"),
  payload: z.looseObject({
    experiment_id: ExperimentId,
    git_sha: z.string().optional(),
    /** Set when this run is a fork or replay of another run. */
    forked_from: RunId.optional(),
    /** True for null-test runs (no real signal sent). */
    null_test: z.boolean().optional(),
  }),
});

const RunEnded = z.strictObject({
  ...envelope,
  type: z.literal("run.ended"),
  payload: z.looseObject({
    status: z.enum(["completed", "aborted", "failed"]),
  }),
});

const CommandRequested = z.strictObject({
  ...envelope,
  ...toolCall,
  type: z.literal("command.requested"),
  payload: z.looseObject({}),
});

const SafetyChecked = z.strictObject({
  ...envelope,
  ...toolCall,
  type: z.literal("safety.checked"),
  payload: z.looseObject({
    decision: z.enum(["allow", "deny"]),
    rule: z.string().optional(),
    reason: z.string().optional(),
  }),
});

const CommandSent = z.strictObject({
  ...envelope,
  ...toolCall,
  type: z.literal("command.sent"),
  payload: z.looseObject({
    latency_ms: z.number().min(0).optional(),
  }),
});

const CommandFailed = z.strictObject({
  ...envelope,
  ...toolCall,
  type: z.literal("command.failed"),
  payload: z.looseObject({
    error: z.string().min(1),
  }),
});

const OutcomeObserved = z.strictObject({
  ...envelope,
  tool: ToolName.optional(),
  type: z.literal("outcome.observed"),
  payload: z.looseObject({
    success: z.boolean(),
    method: z.enum(["human", "camera", "sensor", "device"]),
    note: z.string().optional(),
  }),
});

const Note = z.strictObject({
  ...envelope,
  type: z.literal("note"),
  payload: z.looseObject({
    text: z.string().min(1),
  }),
});

export const Event = z.discriminatedUnion("type", [
  RunStarted,
  RunEnded,
  CommandRequested,
  SafetyChecked,
  CommandSent,
  CommandFailed,
  OutcomeObserved,
  Note,
]);

export type Event = z.infer<typeof Event>;
export type EventType = Event["type"];
export const EVENT_TYPES = Event.options.map((o) => o.shape.type.value) as EventType[];
