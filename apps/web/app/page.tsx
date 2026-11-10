import Link from "next/link";
import { EntryList } from "@/components/entry-list";
import { getCollection } from "@/lib/content/loader";
import { site } from "@/lib/site";

export default async function Home() {
  const [log, experiments] = await Promise.all([getCollection("log"), getCollection("experiments")]);
  return (
    <div className="space-y-12">
      <section>
        <h1 className="text-2xl font-semibold">{site.name}</h1>
        <p className="mt-2 text-muted">{site.description}</p>
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
