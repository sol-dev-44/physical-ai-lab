/** ADR 0011: every published clip must be listed, with its review, in public/clips/README.md. */
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { expect, it } from "vitest";

const dir = path.join(__dirname, "../public/clips");

it("lists every clip in the clips README", () => {
  const readme = readFileSync(path.join(dir, "README.md"), "utf8");
  const unlisted = readdirSync(dir).filter((f) => f !== "README.md" && !readme.includes(`| ${f} |`));
  expect(unlisted).toEqual([]);
});
