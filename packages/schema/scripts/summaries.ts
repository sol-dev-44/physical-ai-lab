/** Regenerates fixtures/summaries/*.json from logs/valid using the TS fold. Review diffs before committing. */
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { Event, summarizeRun } from "../src";

const dir = fileURLToPath(new URL("../fixtures/", import.meta.url));
for (const f of readdirSync(`${dir}logs/valid`)) {
  const events = readFileSync(`${dir}logs/valid/${f}`, "utf8").trim().split("\n").map((l) => Event.parse(JSON.parse(l)));
  writeFileSync(`${dir}summaries/${f.replace(".jsonl", ".json")}`, JSON.stringify(summarizeRun(events), null, 2) + "\n");
}
