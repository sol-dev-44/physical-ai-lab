import { getCollection } from "@/lib/content/loader";
import { type FeedItem, renderFeed } from "@/lib/feed";
import { site } from "@/lib/site";

/** Research write-ups and lab log entries, newest first. Built from cached content, so it prerenders. */
export async function GET() {
  const [research, log] = await Promise.all([getCollection("research"), getCollection("log")]);
  const items: FeedItem[] = [
    ...research.map((e) => ({
      title: e.frontmatter.title,
      url: `${site.url}/research/${e.slug}`,
      date: e.frontmatter.date,
      summary: e.frontmatter.summary,
      category: "Research",
    })),
    ...log.map((e) => ({
      title: e.frontmatter.title,
      url: `${site.url}/log/${e.slug}`,
      date: e.frontmatter.date,
      summary: e.frontmatter.summary,
      category: "Lab log",
    })),
  ].sort((a, b) => b.date.localeCompare(a.date));
  const xml = renderFeed({ title: site.name, url: site.url, description: site.description }, items);
  return new Response(xml, { headers: { "Content-Type": "application/rss+xml; charset=utf-8" } });
}
