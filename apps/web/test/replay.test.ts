/** Both viewer engines must agree on every shared log fixture, step by step. */
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { getEngine } from "../lib/replay/engines";

const dir = path.join(__dirname, "../../../packages/schema/fixtures/logs");
const logs = ["valid", "invalid"].flatMap((sub) =>
  readdirSync(path.join(dir, sub)).map((f) => [`${sub}/${f}`, readFileSync(path.join(dir, sub, f), "utf8")] as const),
);

describe.each(logs)("%s", (_name, text) => {
  it("ts and wasm engines agree", async () => {
    const [a, b] = [(await getEngine("ts")).open(text), (await getEngine("wasm")).open(text)];
    expect(b.valid).toBe(a.valid);
    expect(b.length).toBe(a.length);
    expect(new Set(b.issues.map((i) => i.line))).toEqual(new Set(a.issues.map((i) => i.line)));
    for (let n = 0; n <= a.length; n++) expect(b.summaryAt(n)).toEqual(a.summaryAt(n));
    for (let i = 0; i < a.length; i++) expect(b.event(i)).toEqual(a.event(i));
    a.free();
    b.free();
  });
});
