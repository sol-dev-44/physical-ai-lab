import Link from "next/link";
import { BuildCard } from "@/components/builds/build-card";
import { Reveal } from "@/components/motion/reveal";
import { PageHeader } from "@/components/page-header";
import { getBuildData } from "@/lib/builds/data";
import { getCollection } from "@/lib/content/loader";
import { site } from "@/lib/site";

const intro =
  "The hardware behind the experiments: what each machine is, how its parts were designed and printed, what they cost in filament, and what is still to do.";

export const metadata = { title: "Builds", description: intro };

export default async function Page() {
  const builds = await getCollection("builds");
  const data = await Promise.all(builds.map((b) => getBuildData(b.slug)));

  return (
    <>
      <PageHeader eyebrow="Builds" title="What the lab is building" intro={intro} />
      {builds.length ? (
        <ul className="grid gap-6 md:grid-cols-2">
          {builds.map((b, i) => (
            <li key={b.slug} className={i === 0 ? "md:col-span-2" : undefined}>
              <BuildCard entry={b} data={data[i] ?? null} featured={i === 0} />
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-muted">No builds yet.</p>
      )}

      <Reveal className="mt-16 sm:mt-24">
        <section className="grid gap-8 rounded-card border border-line bg-surface-2 p-8 sm:p-10 md:grid-cols-3">
          <h2 className="text-xl font-semibold tracking-tight md:col-span-3">How a build page stays true</h2>
          <div>
            <p className="font-mono text-xs text-accent">01</p>
            <p className="mt-2 font-medium">Numbers come from the CAD</p>
            <p className="mt-1 text-sm text-muted">
              A script next to the models exports every dimension, mass and count the page shows. Nothing is typed in.
            </p>
          </div>
          <div>
            <p className="font-mono text-xs text-accent">02</p>
            <p className="mt-2 font-medium">Stale data fails the build</p>
            <p className="mt-1 text-sm text-muted">
              A test fails when the export is out of date, and a schema fails the site build when its shape changes.
            </p>
          </div>
          <div>
            <p className="font-mono text-xs text-accent">03</p>
            <p className="mt-2 font-medium">Misses stay in</p>
            <p className="mt-1 text-sm text-muted">
              Each build log keeps what did not fit and what changed because of it.{" "}
              <Link href={site.repo} className="text-accent hover:underline">
                The CAD is on GitHub
              </Link>
              .
            </p>
          </div>
        </section>
      </Reveal>
    </>
  );
}
