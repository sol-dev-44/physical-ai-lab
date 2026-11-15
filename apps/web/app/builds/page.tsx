import { collectionIndex } from "@/lib/content/pages";

// Not in the menu or the sitemap until it has content.
export const metadata = { title: "Builds", robots: { index: false } };
export default collectionIndex("builds", "Builds", "Hardware: arms, rigs, sensors and printed parts.", "No builds yet.");
