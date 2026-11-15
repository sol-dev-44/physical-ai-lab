import { PageHeader } from "@/components/page-header";

// Not in the menu or the sitemap until it has content.
export const metadata = { title: "Workshops", robots: { index: false } };

export default function Page() {
  return (
    <>
      <PageHeader title="Workshops" intro="Hands-on robotics and AI workshops, kids through adults." />
      <p className="text-muted">Coming later.</p>
    </>
  );
}
