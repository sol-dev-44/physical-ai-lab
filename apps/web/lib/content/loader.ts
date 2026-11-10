import "server-only";

import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import matter from "gray-matter";
import { cacheLife } from "next/cache";
import { type CollectionName, type Frontmatter, collections } from "./collections";

/** Repo-root /content. Override with CONTENT_DIR (e.g. for tests). */
// turbopackIgnore: content is included explicitly via outputFileTracingIncludes in next.config.ts.
const CONTENT_DIR = process.env.CONTENT_DIR ?? path.join(/*turbopackIgnore: true*/ process.cwd(), "../../content");
const SLUG = /^[a-z0-9][a-z0-9-]*$/;

export type Entry<C extends CollectionName> = {
  collection: C;
  slug: string;
  frontmatter: Frontmatter<C>;
  body: string;
};

const showDrafts = process.env.NODE_ENV !== "production";

async function readEntry<C extends CollectionName>(collection: C, file: string): Promise<Entry<C>> {
  const slug = file.replace(/\.mdx$/, "");
  if (!SLUG.test(slug)) throw new Error(`content/${collection}/${file}: file name must be a lowercase slug`);
  const raw = await readFile(path.join(CONTENT_DIR, collection, file), "utf8");
  const { data, content } = matter(raw);
  // gray-matter turns YAML dates into Date objects; keep them as YYYY-MM-DD strings.
  for (const [k, v] of Object.entries(data)) if (v instanceof Date) data[k] = v.toISOString().slice(0, 10);
  const parsed = collections[collection].safeParse(data);
  if (!parsed.success) {
    const why = parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ");
    throw new Error(`content/${collection}/${file}: invalid front matter: ${why}`);
  }
  return { collection, slug, frontmatter: parsed.data as Frontmatter<C>, body: content };
}

/** All entries in a collection, newest first. Drafts hidden in production. */
export async function getCollection<C extends CollectionName>(collection: C): Promise<Entry<C>[]> {
  "use cache";
  cacheLife("max");
  let files: string[];
  try {
    files = (await readdir(path.join(CONTENT_DIR, collection))).filter((f) => f.endsWith(".mdx"));
  } catch {
    return [];
  }
  const entries = await Promise.all(files.map((f) => readEntry(collection, f)));
  return entries
    .filter((e) => showDrafts || !e.frontmatter.draft)
    .sort((a, b) => b.frontmatter.date.localeCompare(a.frontmatter.date) || a.slug.localeCompare(b.slug));
}

export async function getEntry<C extends CollectionName>(collection: C, slug: string): Promise<Entry<C> | null> {
  const all = await getCollection(collection);
  return all.find((e) => e.slug === slug) ?? null;
}
