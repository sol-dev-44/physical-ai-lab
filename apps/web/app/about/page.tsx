import { PageHeader } from "@/components/page-header";

export const metadata = { title: "About" };

export default function Page() {
  return (
    <>
      <PageHeader title="About" intro="Who runs this lab and why." />
      <p className="text-muted">Coming soon.</p>
    </>
  );
}
