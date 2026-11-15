import { PageHeader } from "@/components/page-header";

// Not in the menu or the sitemap until it has content.
export const metadata = { title: "Learning Together", robots: { index: false } };

export default function Page() {
  return (
    <>
      <PageHeader title="Learning Together" intro="How a robot and a kid learn side by side." />
      <p className="text-muted">Published as aggregates only. No names, faces or identifying detail of any child.</p>
    </>
  );
}
