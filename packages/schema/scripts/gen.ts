/**
 * Generates schema/event.v0.schema.json from the zod source.
 * `--check` fails if the committed file is out of date (run in CI).
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { z } from "zod";
import { Event } from "../src/event";

const out = fileURLToPath(new URL("../schema/event.v0.schema.json", import.meta.url));
const schema = {
  ...z.toJSONSchema(Event, { target: "draft-2020-12", io: "input" }),
  $id: "https://lab.local/schema/event.v0.schema.json",
  title: "Lab event v0",
};
const text = JSON.stringify(schema, null, 2) + "\n";

if (process.argv.includes("--check")) {
  const current = readFileSync(out, "utf8");
  if (current !== text) {
    console.error("schema/event.v0.schema.json is stale. Run: pnpm schema:gen");
    process.exit(1);
  }
  console.log("schema up to date");
} else {
  writeFileSync(out, text);
  console.log(`wrote ${out}`);
}
