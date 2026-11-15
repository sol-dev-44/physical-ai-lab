import Link from "next/link";
import { EntryList } from "@/components/entry-list";
import { EventStream } from "@/components/event-stream";
import { ExperimentCard } from "@/components/experiment-card";
import { Reveal, RevealItem, RevealList } from "@/components/motion/reveal";
import { ButtonLink } from "@/components/ui/button-link";
import { Eyebrow } from "@/components/ui/eyebrow";
import { SectionHeading } from "@/components/ui/section-heading";
import { getCollection } from "@/lib/content/loader";
import { getSampleLines } from "@/lib/sample-run";
import { site } from "@/lib/site";

const principles = [
  {
    title: "One path to hardware",
    text: "Every command goes through one tool registry and one safety gate. Refusals are logged with the rule that made them.",
  },
  {
    title: "Everything is an event",
    text: "Each run is an append-only log in one format, shared by TypeScript, Python and Rust. Results are computed from it, never typed in.",
  },
  {
    title: "Measured, including failures",
    text: "Write-ups report what broke and what lost. Rust in the browser was benchmarked, lost, and the post says so.",
  },
];

const order = { running: 0, planned: 1, done: 2, abandoned: 3 } as const;

export default async function Home() {
  const [log, experiments, research, lines] = await Promise.all([
    getCollection("log"),
    getCollection("experiments"),
    getCollection("research"),
    getSampleLines(),
  ]);
  const paper = research[0];
  // Work in progress first, then newest. The first one is the lab's current focus.
  const ranked = [...experiments].sort((a, b) => order[a.frontmatter.status] - order[b.frontmatter.status]);

  return (
    <div className="space-y-28 sm:space-y-36">
      <section className="relative grid items-center gap-12 lg:grid-cols-[1.1fr_1fr]">
        <div aria-hidden className="bg-graph pointer-events-none absolute -inset-x-8 -top-16 -bottom-10 -z-10 sm:-inset-x-16" />
        <div>
          <Eyebrow className="mb-5">{site.name}</Eyebrow>
          <h1 className="text-display font-semibold">{site.tagline}</h1>
          <p className="mt-6 max-w-xl text-lg text-muted">{site.description}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <ButtonLink href="/research/safe-logged-robot-learning">Read the research write-up</ButtonLink>
            <ButtonLink href="/experiments" variant="secondary">
              See the experiments
            </ButtonLink>
          </div>
        </div>
        <EventStream lines={lines} />
      </section>

      <section aria-labelledby="principles">
        <h2 id="principles" className="sr-only">
          How the lab works
        </h2>
        <RevealList className="grid gap-8 sm:grid-cols-3">
          {principles.map((p, i) => (
            <RevealItem key={p.title} className="border-t border-line-strong pt-5">
              <p className="font-mono text-xs text-accent">0{i + 1}</p>
              <h3 className="mt-3 font-semibold tracking-tight">{p.title}</h3>
              <p className="mt-2 text-sm text-muted">{p.text}</p>
            </RevealItem>
          ))}
        </RevealList>
      </section>

      {paper ? (
        <Reveal>
          <Link
            href={`/research/${paper.slug}`}
            className="group grid gap-8 rounded-card border border-line bg-surface p-8 shadow-card transition duration-base ease-out-quint hover:-translate-y-0.5 hover:shadow-lift sm:p-12 lg:grid-cols-[1fr_auto] lg:items-end"
          >
            <div className="max-w-3xl">
              <Eyebrow className="mb-4">
                Research{paper.frontmatter.status === "working-draft" ? " · working draft" : ""}
              </Eyebrow>
              <h2 className="text-title font-semibold">{paper.frontmatter.title}</h2>
              <p className="mt-4 text-muted">{paper.frontmatter.summary}</p>
            </div>
            <span className="inline-flex items-center gap-1 text-sm font-medium whitespace-nowrap text-accent">
              Read the write-up
              <span aria-hidden className="transition-transform duration-base ease-out-quint group-hover:translate-x-0.5">
                →
              </span>
            </span>
          </Link>
        </Reveal>
      ) : null}

      <section>
        <SectionHeading
          eyebrow="Experiments"
          title="What the lab is testing"
          intro="Each experiment states a hypothesis and a protocol, logs every run, and reports what happened."
          href="/experiments"
          linkLabel="All experiments"
        />
        <RevealList className="grid gap-5 md:grid-cols-2">
          {ranked.slice(0, 4).map((e, i) => (
            <RevealItem key={e.slug} className={i === 0 ? "md:col-span-2" : undefined}>
              <ExperimentCard entry={e} featured={i === 0} />
            </RevealItem>
          ))}
        </RevealList>
      </section>

      <section>
        <SectionHeading
          eyebrow="Lab log"
          title="Latest from the bench"
          intro="A build diary in order: wins, failures and dead ends."
          href="/log"
          linkLabel="Full log"
        />
        <Reveal>
          <EntryList entries={log.slice(0, 5)} empty="No entries yet." />
        </Reveal>
      </section>

      <Reveal>
        <section className="rounded-card border border-line bg-surface-2 p-8 sm:p-12">
          <div className="max-w-2xl">
            <Eyebrow className="mb-4">Open by default</Eyebrow>
            <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              The code, the decisions and the safety rules are public.
            </h2>
            <p className="mt-4 text-muted">
              The decision records explain why the lab is built the way it is. The architecture page lists every
              safety rule and where it is enforced, including the known gaps.
            </p>
            <div className="mt-6 flex flex-wrap gap-x-6 gap-y-2 text-sm font-medium">
              <Link href={`${site.repo}/blob/main/docs/architecture.md`} className="text-accent hover:underline">
                Architecture →
              </Link>
              <Link href={`${site.repo}/blob/main/docs/adr/README.md`} className="text-accent hover:underline">
                Decision records →
              </Link>
              <Link href={site.repo} className="text-accent hover:underline">
                Code on GitHub →
              </Link>
            </div>
          </div>
        </section>
      </Reveal>
    </div>
  );
}
