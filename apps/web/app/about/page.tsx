import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { site } from "@/lib/site";

export const metadata = { title: "About", description: "What this lab is, how it works, and where it is going." };

const stack = [
  ["Site", "Next.js 16, React, TypeScript, Tailwind, Motion"],
  ["Lab agent and vision", "Python: tool registry, safety gate, interlocks, camera tracking"],
  ["Shared core", "Rust: the event library behind the CLI and the in-browser replay engine"],
  ["Arm learning", "LeRobot and ACT on a Seeed SO-ARM101 Pro pair"],
  ["Published data", "Supabase with row-level security, pinned by SQL tests"],
] as const;

export default function Page() {
  return (
    <div className="max-w-prose">
      <PageHeader
        eyebrow="About"
        title="A one-person physical AI lab"
        intro="Run from home and built the way production systems are: one event format, one gated path to hardware, tests for every safety rule, and a public record of what worked and what didn't."
      />
      <div className="space-y-5 text-fg">
        <p>
          It starts small on purpose. A toy robot, a $30 IR blaster and a webcam proved the harness. A leader and follower
          arm pair is next on the same harness, with recorded demonstrations, camera evals and learned policies.
        </p>
        <p>
          The writing is part of the work. Every experiment states a hypothesis before it runs, and every post reports
          the failures next to the wins: the Rust engine that lost its benchmark, the stickers that couldn&apos;t track
          heading, the calibration that rewrote the wrong file.
        </p>
        <p>
          The <Link href="/research/safe-logged-robot-learning" className="text-accent underline underline-offset-2">research
          write-up</Link> pulls it together.
        </p>
      </div>
      <h2 className="mt-14 font-mono text-xs tracking-[0.14em] text-subtle uppercase">Stack</h2>
      <dl className="mt-4 divide-y divide-line border-y border-line">
        {stack.map(([k, v]) => (
          <div key={k} className="grid gap-1 py-4 sm:grid-cols-[11rem_1fr]">
            <dt className="text-sm font-medium">{k}</dt>
            <dd className="text-sm text-muted">{v}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-8 text-sm">
        <a href={site.repo} className="font-medium text-accent hover:underline">
          The code, decision records and bench notes are on GitHub →
        </a>
      </p>
    </div>
  );
}
