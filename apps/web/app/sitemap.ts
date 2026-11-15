import type { MetadataRoute } from "next";
import { getCollection } from "@/lib/content/loader";
import { site } from "@/lib/site";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [research, experiments, log] = await Promise.all([
    getCollection("research"),
    getCollection("experiments"),
    getCollection("log"),
  ]);
  const pages = ["", ...site.nav.map((n) => n.href), "/harness/replay"].map((p) => ({ url: `${site.url}${p}` }));
  const entries = [
    ...research.map((e) => ({ url: `${site.url}/research/${e.slug}`, lastModified: e.frontmatter.date })),
    ...experiments.map((e) => ({ url: `${site.url}/experiments/${e.slug}`, lastModified: e.frontmatter.date })),
    ...log.map((e) => ({ url: `${site.url}/log/${e.slug}`, lastModified: e.frontmatter.date })),
  ];
  return [...pages, ...entries];
}
