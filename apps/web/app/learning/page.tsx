import { PageHeader } from "@/components/page-header";

export const metadata = { title: "Learning Together" };

export default function Page() {
  return (
    <>
      <PageHeader title="Learning Together" intro="How a robot and a kid learn side by side." />
      <p className="text-muted">Published as aggregates only. No names, faces or identifying detail of any child.</p>
    </>
  );
}
