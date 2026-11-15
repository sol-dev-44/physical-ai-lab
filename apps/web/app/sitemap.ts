import type { MetadataRoute } from "next";
import { getCollection } from "@/lib/content/loader";
import { site } from "@/lib/site";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [experiments, log] = await Promise.all([getCollection("experiments"), getCollection("log")]);
  const pages = ["", ...site.nav.map((n) => n.href), "/harness/replay"].map((p) => ({ url: `${site.url}${p}` }));
  const entries = [
    ...experiments.map((e) => ({ url: `${site.url}/experiments/${e.slug}`, lastModified: e.frontmatter.date })),
    ...log.map((e) => ({ url: `${site.url}/log/${e.slug}`, lastModified: e.frontmatter.date })),
  ];
  return [...pages, ...entries];
}
