import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { expect, it } from "vitest";
import { Event, summarizeRun } from "../src";

const log = readFileSync(fileURLToPath(new URL("../fixtures/logs/valid/full_run.jsonl", import.meta.url)), "utf8");
const events = log.trim().split("\n").map((l) => Event.parse(JSON.parse(l)));

it("folds the reference run", () => {
  const s = summarizeRun(events);
  expect(s).toMatchObject({
    experiment_id: "exp000-ir-bridge",
    status: "completed",
    requested: 3,
    denied: 1,
    sent: 1,
    failed: 1,
    observed: 1,
    succeeded: 1,
    success_rate: 1,
  });
  expect(s.tools["fan.power"]).toEqual({ requested: 1, sent: 1, succeeded: 1, observed: 1 });
});

it("is deterministic", () => {
  expect(summarizeRun(events)).toEqual(summarizeRun(events));
});

it.each(["full_run", "unfinished_run"])("matches fixtures/summaries/%s.json (shared with Python and Rust)", (name) => {
  const dir = fileURLToPath(new URL("../fixtures/", import.meta.url));
  const evs = readFileSync(`${dir}logs/valid/${name}.jsonl`, "utf8").trim().split("\n").map((l) => Event.parse(JSON.parse(l)));
  expect(summarizeRun(evs)).toEqual(JSON.parse(readFileSync(`${dir}summaries/${name}.json`, "utf8")));
});
