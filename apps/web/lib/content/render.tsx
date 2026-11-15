import { MDXRemote } from "next-mdx-remote/rsc";
import remarkGfm from "remark-gfm";
import { mdxComponents } from "@/components/mdx";

/** Render an MDX body, with GitHub-flavoured Markdown (tables). JS expressions in MDX are
 * blocked; use components instead. */
export function Mdx({ source }: { source: string }) {
  return (
    <div className="prose prose-lab max-w-none prose-headings:tracking-tight prose-a:underline-offset-2 prose-code:rounded prose-code:bg-surface-2 prose-code:px-1 prose-code:py-0.5 prose-code:font-normal prose-code:before:content-none prose-code:after:content-none prose-table:block prose-table:overflow-x-auto prose-th:whitespace-nowrap">
      <MDXRemote source={source} components={mdxComponents} options={{ mdxOptions: { remarkPlugins: [remarkGfm] } }} />
    </div>
  );
}
