import Link from "next/link";
import { PageHeader } from "@/components/page-header";

export const metadata = { title: "Harness" };

export default function Page() {
  return (
    <>
      <PageHeader title="Harness" intro="The event-sourced harness behind every experiment: one log format, replays, forks, evals and null tests." />
      <p className="text-muted">Architecture write-up coming with Experiment 0.</p>
      <p className="mt-4">
        <Link className="underline" href="/harness/replay">
          Replay viewer
        </Link>
        <span className="text-muted">: open a run log and step through it in your browser.</span>
      </p>
    </>
  );
}
