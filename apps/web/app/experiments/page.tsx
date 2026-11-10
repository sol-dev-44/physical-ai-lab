import { collectionIndex } from "@/lib/content/pages";

export const metadata = { title: "Experiments" };
export default collectionIndex(
  "experiments",
  "Experiments",
  "Each one has a hypothesis, a protocol, logged runs, and results computed from those logs.",
  "No experiments yet.",
);
