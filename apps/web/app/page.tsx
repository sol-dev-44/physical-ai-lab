import Link from "next/link";
import { EntryList } from "@/components/entry-list";
import { getCollection } from "@/lib/content/loader";
import { site } from "@/lib/site";

const now = [
  {
    label: "Experiment 0",
    href: "/experiments/exp000-ir-bridge",
    text: "A $30 IR blaster drives a toy robot through the harness, from the command line and from this site.",
  },
  {
    label: "Experiment 1",
    href: "/experiments/exp001-vision-observer",
    text: "An overhead webcam tracks, fences, steers and judges the robot: 29 of 29 tracked moves judged correctly.",
  },
  {
    label: "Next",
    href: "/log/2026-11-11-heading-from-motion",
    text: "Phase 1 with two LeRobot arms: a real stop path, recorded demonstrations, camera evals, a first learned policy.",
  },
];

export default async function Home() {
  const [log, experiments] = await Promise.all([getCollection("log"), getCollection("experiments")]);
  return (
    <div className="space-y-12">
      <section>
        <h1 className="text-2xl font-semibold">{site.name}</h1>
        <p className="mt-2 text-muted">{site.description}</p>
        <p className="mt-2 text-muted">
          Every experiment writes to one append-only event log, and every hardware command goes through one safety
          gate.{" "}
          <Link href="/harness" className="underline">
            How the harness works
          </Link>{" "}
          ·{" "}
          <a href={site.repo} className="underline">
            Code on GitHub
          </a>
        </p>
      </section>
      <section>
        <h2 className="mb-3 text-lg font-semibold">Where things stand</h2>
        <ul className="space-y-2">
          {now.map((item) => (
            <li key={item.label}>
              <Link href={item.href} className="font-medium">
                {item.label}
              </Link>
              <span className="text-muted">: {item.text}</span>
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2 className="mb-3 text-lg font-semibold">
          <Link href="/log">Latest from the log</Link>
        </h2>
        <EntryList entries={log.slice(0, 5)} empty="No entries yet." />
      </section>
      <section>
        <h2 className="mb-3 text-lg font-semibold">
          <Link href="/experiments">Experiments</Link>
        </h2>
        <EntryList entries={experiments.slice(0, 5)} empty="No experiments yet." />
      </section>
    </div>
  );
}
