import { Event } from "@lab/schema";
import { expect, it } from "vitest";
import { contractRows, eventDescriptions } from "../lib/contract";

it("describes exactly the schema's event types", () => {
  const schemaTypes = Event.options.map((o) => o.shape.type.value).sort();
  expect(Object.keys(eventDescriptions).sort()).toEqual(schemaTypes);
});

it("reads payload fields and tool calls from the schema", () => {
  const rows = Object.fromEntries(contractRows().map((r) => [r.type, r]));
  expect(rows["safety.checked"]).toMatchObject({ toolCall: true, fields: ["decision", "rule?", "reason?"] });
  expect(rows["outcome.observed"]).toMatchObject({ toolCall: false, fields: ["success", "method", "note?"] });
  expect(rows["run.started"]?.fields).toContain("experiment_id");
});
