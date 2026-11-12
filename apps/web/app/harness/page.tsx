import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { site } from "@/lib/site";

export const metadata = { title: "Harness" };

const rules = [
  {
    title: "One event contract, three languages",
    text: "Every experiment writes the same append-only event log. The format is defined in TypeScript and mirrored in Python and Rust; shared fixtures run in all three test suites, and CI checks that Python and Rust compute identical summaries from the same runs.",
  },
  {
    title: "One path to hardware",
    text: "Every command goes through a tool registry and a safety gate: STOP file, allowlist, argument checks, duration caps, confirmation, rate limits, then world-state interlocks. Every decision is logged, refusals included, with the rule that made it.",
  },
  {
    title: "Sensors report, the gate decides",
    text: "The camera only says where the robot is. Whether a move is allowed (a recent sighting? would it leave the arena?) is an interlock in the gate, tested like every other rule.",
  },
  {
    title: "This site never touches hardware",
    text: "The admin page can only queue a request. The lab machine polls for it, and its safety gate decides. Database policies, pinned by SQL tests, fill in who asked.",
  },
  {
    title: "Timed moves are played by the device",
    text: "A hold is sent once, as one frame with a repeat count, so Wi-Fi jitter can't chop up the motion and a recorded code can't outlast the time cap.",
  },
  {
    title: "Privacy by default",
    text: "Camera frames are tracked and dropped; only numbers are kept. Saving a frame needs an explicit nobody-in-frame flag and never leaves the lab machine.",
  },
];

export default function Page() {
  return (
    <>
      <PageHeader
        title="Harness"
        intro="The event-sourced harness behind every experiment: one log format, one gated path to hardware, replays and evals."
      />
      <div className="space-y-6">
        {rules.map((r) => (
          <section key={r.title}>
            <h2 className="font-semibold">{r.title}</h2>
            <p className="mt-1 text-muted">{r.text}</p>
          </section>
        ))}
      </div>
      <p className="mt-10">
        <Link className="underline" href="/harness/replay">
          Replay viewer
        </Link>
        <span className="text-muted">: open a run log and step through it in your browser.</span>
      </p>
      <p className="mt-2">
        <a className="underline" href={`${site.repo}/blob/main/docs/architecture.md`}>
          Architecture and invariants
        </a>
        <span className="text-muted">: the diagram, each rule and where it is enforced, and the known gaps.</span>
      </p>
      <p className="mt-2">
        <a className="underline" href={`${site.repo}/blob/main/docs/adr/README.md`}>
          Decision records
        </a>
        <span className="text-muted">: the decisions that shaped the lab, and why.</span>
      </p>
    </>
  );
}
