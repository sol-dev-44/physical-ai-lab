/**
 * The event contract, described for readers. Event types and payload fields are read from the
 * schema itself (@lab/schema), so the harness page can't drift from the code; only the one-line
 * descriptions are written here, and a test checks they cover exactly the schema's types.
 */
import { Event } from "@lab/schema";
import type { z } from "zod";

export type EventType = Event["type"];

export const eventDescriptions: Record<EventType, string> = {
  "run.started": "A run begins: which experiment, at which commit, and whether it is a null test.",
  "run.ended": "The run finishes as completed, aborted or failed.",
  "command.requested": "Someone or something asks for a tool call: a person, the CLI, the admin queue or a policy.",
  "safety.checked": "The gate's decision on that request, allow or deny, with the rule that decided.",
  "command.sent": "The allowed command reaches the device, with its latency.",
  "command.failed": "The device or the driver failed, with the error.",
  "outcome.observed": "What actually happened, and who judged it: a person, the camera, a sensor or the device.",
  note: "A free-text observation, kept in order with everything else.",
};

export type ContractRow = { type: EventType; description: string; toolCall: boolean; fields: string[] };

function isOptional(schema: z.ZodType): boolean {
  return schema.safeParse(undefined).success;
}

/** One row per event type, in the schema's order. Optional payload fields end with "?". */
export function contractRows(): ContractRow[] {
  return Event.options.map((option) => {
    const shape = option.shape as Record<string, z.ZodType>;
    const type = (option.shape.type as z.ZodLiteral<EventType>).value;
    const payload = (option.shape.payload as unknown as z.ZodObject).shape as Record<string, z.ZodType>;
    return {
      type,
      description: eventDescriptions[type],
      toolCall: "tool" in shape && !isOptional(shape.tool as z.ZodType),
      fields: Object.entries(payload).map(([k, v]) => (isOptional(v) ? `${k}?` : k)),
    };
  });
}
