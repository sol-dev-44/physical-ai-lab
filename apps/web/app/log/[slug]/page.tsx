import Link from "next/link";
import { collectionDetail } from "@/lib/content/pages";

const { generateStaticParams, generateMetadata, Detail } = collectionDetail("log", (entry) =>
  entry.frontmatter.experiment ? (
    <p className="mb-10 text-sm">
      <span className="text-subtle">Part of </span>
      <Link href={`/experiments/${entry.frontmatter.experiment}`} className="font-mono text-accent hover:underline">
        {entry.frontmatter.experiment}
      </Link>
    </p>
  ) : null,
);
export { generateMetadata, generateStaticParams };
export default Detail;
