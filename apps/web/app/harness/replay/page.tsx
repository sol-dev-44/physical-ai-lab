import { PageHeader } from "@/components/page-header";
import { getSampleLog } from "@/lib/sample-run";
import { ReplayViewer } from "./replay-viewer";

export const metadata = {
  title: "Replay viewer",
  description: "Step through a lab run log event by event, validated against the event contract in your browser.",
};

export default async function Page() {
  const sample = await getSampleLog();
  return (
    <>
      <PageHeader
        eyebrow="Harness"
        title="Replay viewer"
        intro="Step through a run log event by event: what was asked, what the safety gate decided, what was sent, and what happened. The log is checked against the event contract in your browser and never uploaded."
      />
      <ReplayViewer sample={sample} />
    </>
  );
}
