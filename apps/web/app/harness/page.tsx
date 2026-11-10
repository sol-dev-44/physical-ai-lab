import { PageHeader } from "@/components/page-header";

export const metadata = { title: "Harness" };

export default function Page() {
  return (
    <>
      <PageHeader title="Harness" intro="The event-sourced harness behind every experiment: one log format, replays, forks, evals and null tests." />
      <p className="text-muted">Architecture write-up coming with Experiment 0.</p>
    </>
  );
}
