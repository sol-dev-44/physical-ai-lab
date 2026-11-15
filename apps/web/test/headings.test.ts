import { expect, it } from "vitest";
import { extractHeadings, slugify } from "../lib/content/headings";

it("slugifies headings the same way the h2 component does", () => {
  expect(slugify("1. The problem")).toBe("1-the-problem");
  expect(slugify("What `didn't` work")).toBe("what-didn-t-work");
});

it("lists level-2 headings and skips code blocks", () => {
  const body = ["## Why", "text", "```", "## not a heading", "```", "### Sub", "## 2. The harness"].join("\n");
  expect(extractHeadings(body)).toEqual([
    { id: "why", text: "Why" },
    { id: "2-the-harness", text: "2. The harness" },
  ]);
});
