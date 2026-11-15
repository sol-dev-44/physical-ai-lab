import { ExperimentCard } from "@/components/experiment-card";
import { RevealItem, RevealList } from "@/components/motion/reveal";
import { PageHeader } from "@/components/page-header";
import { getCollection } from "@/lib/content/loader";

export const metadata = {
  title: "Experiments",
  description: "Each experiment has a hypothesis, a protocol, logged runs, and results computed from those logs.",
};

export default async function Page() {
  const experiments = await getCollection("experiments");
  return (
    <>
      <PageHeader
        eyebrow="Experiments"
        title="What the lab is testing"
        intro="Each one has a hypothesis, a protocol, logged runs, and results computed from those logs."
      />
      {experiments.length ? (
        <RevealList className="grid gap-5 md:grid-cols-2">
          {experiments.map((e) => (
            <RevealItem key={e.slug}>
              <ExperimentCard entry={e} />
            </RevealItem>
          ))}
        </RevealList>
      ) : (
        <p className="text-muted">No experiments yet.</p>
      )}
    </>
  );
}
