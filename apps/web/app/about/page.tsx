import { PageHeader } from "@/components/page-header";
import { site } from "@/lib/site";

export const metadata = { title: "About" };

export default function Page() {
  return (
    <>
      <PageHeader title="About" intro="What this lab is and how it works." />
      <div className="space-y-4">
        <p>
          A one-person physical AI lab, run from home and built the way production systems are: one event format, one
          gated path to hardware, tests for every safety rule, and a public record of what worked and what didn&apos;t.
        </p>
        <p>
          It starts small on purpose. A toy robot, a $30 IR blaster and a webcam proved the harness; two LeRobot arms
          are next, on the same harness, with recorded demonstrations, camera evals and a first learned policy.
        </p>
        <p className="text-muted">
          The stack: Next.js and TypeScript for this site, Python for the lab agent and vision, Rust where it measurably
          earns its place, Supabase for published data.{" "}
          <a href={site.repo} className="underline">
            The code is on GitHub
          </a>
          .
        </p>
      </div>
    </>
  );
}
