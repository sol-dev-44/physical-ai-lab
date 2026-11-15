/** RSS 2.0 for the site's write-ups. Pure functions so the feed is easy to test. */

export type FeedItem = { title: string; url: string; date: string; summary: string; category: string };

export function escapeXml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}

const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** "2026-11-15" to an RFC 822 date at midnight UTC, as RSS requires. */
export function rfc822(isoDate: string): string {
  const d = new Date(`${isoDate}T00:00:00Z`);
  const dd = String(d.getUTCDate()).padStart(2, "0");
  return `${days[d.getUTCDay()]}, ${dd} ${months[d.getUTCMonth()]} ${d.getUTCFullYear()} 00:00:00 GMT`;
}

export function renderFeed(channel: { title: string; url: string; description: string }, items: FeedItem[]): string {
  const body = items
    .map(
      (i) => `    <item>
      <title>${escapeXml(i.title)}</title>
      <link>${escapeXml(i.url)}</link>
      <guid isPermaLink="true">${escapeXml(i.url)}</guid>
      <pubDate>${rfc822(i.date)}</pubDate>
      <category>${escapeXml(i.category)}</category>
      <description>${escapeXml(i.summary)}</description>
    </item>`,
    )
    .join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${escapeXml(channel.title)}</title>
    <link>${escapeXml(channel.url)}</link>
    <description>${escapeXml(channel.description)}</description>
    <language>en</language>
${body}
  </channel>
</rss>
`;
}
