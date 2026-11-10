import { PageHeader } from "@/components/page-header";

export const metadata = { title: "Workshops" };

export default function Page() {
  return (
    <>
      <PageHeader title="Workshops" intro="Hands-on robotics and AI workshops, kids through adults." />
      <p className="text-muted">Coming later.</p>
    </>
  );
}
