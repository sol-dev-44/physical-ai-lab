// @vitest-environment node
// (jsdom replaces the URL global, and fileURLToPath rejects its URLs; this test only reads files.)
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { ClientMessage, ServerMessage } from "./protocol";

const dir = fileURLToPath(new URL("../../../packages/schema/fixtures/console", import.meta.url));
const files = (kind: string) => readdirSync(join(dir, kind)).filter((f) => f.endsWith(".json"));
const parse = (kind: string, f: string) => {
  const data: unknown = JSON.parse(readFileSync(join(dir, kind, f), "utf8"));
  return (f.startsWith("client_") ? ClientMessage : ServerMessage).safeParse(data);
};

describe("console protocol fixtures (shared with the Python server)", () => {
  it.each(files("valid"))("accepts %s", (f) => {
    expect(parse("valid", f).success).toBe(true);
  });
  it.each(files("invalid"))("rejects %s", (f) => {
    expect(parse("invalid", f).success).toBe(false);
  });
});
