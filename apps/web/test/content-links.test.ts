/**
 * Every internal link in a write-up must point at a page that exists: a static route under app/,
 * or a write-up in one of the content collections. A renamed slug fails here, not in production.
 */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { expect, it } from "vitest";

const appDir = path.join(__dirname, "../app");
const contentDir = path.join(__dirname, "../../../content");
const collections = ["experiments", "log", "research", "builds"];

function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((f) => {
    const p = path.join(dir, f);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
}

/** Routes with a page.tsx and no dynamic segment, e.g. "/harness/replay". Route groups are dropped. */
function staticRoutes(): Set<string> {
  const routes = new Set<string>(["/feed.xml", "/sitemap.xml", "/robots.txt"]);
  for (const f of walk(appDir)) {
    if (path.basename(f) !== "page.tsx") continue;
    const rel = path.relative(appDir, path.dirname(f)).split(path.sep).filter((s) => s && !s.startsWith("("));
    if (rel.some((s) => s.startsWith("["))) continue;
    routes.add(`/${rel.join("/")}`.replace(/\/$/, "") || "/");
  }
  return routes;
}

function exists(route: string, statics: Set<string>): boolean {
  if (statics.has(route)) return true;
  const [, collection, slug, ...rest] = route.split("/");
  if (!collection || !slug || rest.length || !collections.includes(collection)) return false;
  return existsSync(path.join(contentDir, collection, `${slug}.mdx`));
}

it("has no broken internal links in the write-ups", () => {
  const statics = staticRoutes();
  const broken: string[] = [];
  for (const file of walk(contentDir).filter((f) => f.endsWith(".mdx"))) {
    const text = readFileSync(file, "utf8");
    const links = [...text.matchAll(/\]\((\/[^)\s]*)\)|href="(\/[^"]*)"/g)].map((m) => (m[1] ?? m[2]) as string);
    for (const link of links) {
      const route = link.split(/[?#]/)[0]?.replace(/\/$/, "") || "/";
      if (!exists(route, statics)) broken.push(`${path.relative(contentDir, file)}: ${link}`);
    }
  }
  expect(broken).toEqual([]);
});

it("knows the site's main routes", () => {
  const statics = staticRoutes();
  for (const r of ["/", "/research", "/experiments", "/log", "/harness", "/harness/replay", "/about"]) {
    expect(statics.has(r), r).toBe(true);
  }
});
