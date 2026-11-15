import Link from "next/link";
import { HarnessDiagram } from "@/components/harness-diagram";
import { RevealItem, RevealList } from "@/components/motion/reveal";
import { PageHeader } from "@/components/page-header";
import { contractRows } from "@/lib/contract";
import { site } from "@/lib/site";

export const metadata = {
  title: "Harness",
  description: "The event-sourced harness behind every experiment: one log format, one gated path to hardware, replays and evals.",
};

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
    text: "Camera frames are tracked and dropped; only numbers are kept. Saving a frame needs an explicit nobody-in-frame flag and never leaves the lab machine. Published arm clips are hand-reviewed (ADR 0011).",
  },
];

const more = [
  { href: "/harness/replay", title: "Replay viewer", text: "Open a run log and step through it in your browser." },
  {
    href: `${site.repo}/blob/main/docs/architecture.md`,
    title: "Architecture and invariants",
    text: "The diagram, each rule and where it is enforced, and the known gaps.",
  },
  {
    href: `${site.repo}/blob/main/docs/adr/README.md`,
    title: "Decision records",
    text: "The decisions that shaped the lab, and why.",
  },
];

export default function Page() {
  return (
    <>
      <PageHeader
        eyebrow="Harness"
        title="One way in, one log, every decision on the record"
        intro="The event-sourced harness behind every experiment: one log format, one gated path to hardware, replays and evals."
      />
      <HarnessDiagram />
      <RevealList className="mt-16 grid gap-x-10 gap-y-10 md:grid-cols-2">
        {rules.map((r, i) => (
          <RevealItem key={r.title} className="border-t border-line-strong pt-5">
            <p className="font-mono text-xs text-accent">{String(i + 1).padStart(2, "0")}</p>
            <h2 className="mt-3 text-lg font-semibold tracking-tight">{r.title}</h2>
            <p className="mt-2 text-sm text-muted">{r.text}</p>
          </RevealItem>
        ))}
      </RevealList>
      <section aria-labelledby="contract" className="mt-20">
        <h2 id="contract" className="text-2xl font-semibold tracking-tight">The event contract</h2>
        <p className="mt-3 max-w-2xl text-muted">
          Every event shares an envelope (run, sequence number, timestamp, actor, optional parent) and adds one of these
          types. This table is read from the schema the lab runs on, so it can&apos;t drift from the code.
        </p>
        <div className="mt-6 overflow-x-auto rounded-card border border-line bg-surface shadow-card">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-line bg-surface-2 font-mono text-xs tracking-wider text-subtle uppercase">
              <tr>
                <th scope="col" className="px-4 py-3 font-medium">Type</th>
                <th scope="col" className="px-4 py-3 font-medium">Written when</th>
                <th scope="col" className="px-4 py-3 font-medium">Payload</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {contractRows().map((r) => (
                <tr key={r.type} className="align-top">
                  <td className="px-4 py-3 font-mono text-xs whitespace-nowrap text-fg">
                    {r.type}
                    {r.toolCall ? <span className="block text-subtle">+ tool, args</span> : null}
                  </td>
                  <td className="min-w-56 px-4 py-3 text-muted">{r.description}</td>
                  <td className="px-4 py-3 font-mono text-xs text-muted">{r.fields.length ? r.fields.join(", ") : "none"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="mt-16 grid gap-4 md:grid-cols-3">
        {more.map((m) => (
          <Link
            key={m.href}
            href={m.href}
            className="group rounded-card border border-line bg-surface p-6 shadow-card transition duration-base ease-out-quint hover:-translate-y-0.5 hover:shadow-lift"
          >
            <p className="font-semibold tracking-tight group-hover:text-accent">{m.title} →</p>
            <p className="mt-2 text-sm text-muted">{m.text}</p>
          </Link>
        ))}
      </div>
    </>
  );
}
