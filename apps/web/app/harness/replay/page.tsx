import { readFile } from "node:fs/promises";
import path from "node:path";
import { cacheLife } from "next/cache";
import { PageHeader } from "@/components/page-header";
import { ReplayViewer } from "./replay-viewer";

export const metadata = { title: "Replay viewer" };

// A contract fixture, not a real run. Read at build time; the page is static.
const SAMPLE = path.join(/*turbopackIgnore: true*/ process.cwd(), "../../packages/schema/fixtures/logs/valid/full_run.jsonl");

async function getSample(): Promise<string> {
  "use cache";
  cacheLife("max");
  return readFile(SAMPLE, "utf8");
}

export default async function Page() {
  const sample = await getSample();
  return (
    <>
      <PageHeader
        title="Replay viewer"
        intro="Step through a run log event by event: what was asked, what the safety gate decided, what was sent, and what happened. The log is checked against the event contract in your browser and never uploaded."
      />
      <ReplayViewer sample={sample} />
    </>
  );
}
