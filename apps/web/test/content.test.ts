/** Fails CI if any write-up in /content has bad front matter or a bad file name. */
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import { describe, expect, it } from "vitest";
import { type CollectionName, collections } from "../lib/content/collections";

const root = path.join(__dirname, "../../../content");

describe.each(Object.keys(collections) as CollectionName[])("content/%s", (name) => {
  const dir = path.join(root, name);
  const files = readdirSync(dir).filter((f) => f.endsWith(".mdx"));
  it.each(files.length ? files : ["(none)"])("%s", (file) => {
    if (file === "(none)") return;
    expect(file).toMatch(/^[a-z0-9][a-z0-9-]*\.mdx$/);
    const { data } = matter(readFileSync(path.join(dir, file), "utf8"));
    for (const [k, v] of Object.entries(data)) if (v instanceof Date) data[k] = v.toISOString().slice(0, 10);
    const r = collections[name].safeParse(data);
    expect(r.error?.issues ?? []).toEqual([]);
  });
});

it("experiment ids match their file names", () => {
  const dir = path.join(root, "experiments");
  for (const f of readdirSync(dir).filter((x) => x.endsWith(".mdx"))) {
    const { data } = matter(readFileSync(path.join(dir, f), "utf8"));
    expect(data.id).toBe(f.replace(/\.mdx$/, ""));
  }
});
