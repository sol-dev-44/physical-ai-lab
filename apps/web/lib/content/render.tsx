import { MDXRemote, type MDXRemoteProps } from "next-mdx-remote/rsc";
import remarkGfm from "remark-gfm";
import { mdxComponents } from "@/components/mdx";
import { cn } from "@/lib/design/cn";

export type MdxComponents = NonNullable<MDXRemoteProps["components"]>;

/** Render an MDX body, with GitHub-flavoured Markdown (tables). JS expressions in MDX are
 * blocked; use components instead (props arrive as strings).
 *
 * `components` adds to or overrides the shared map for one page (the Builds page passes
 * components closed over its build data); `className` adds layout classes to the wrapper. */
export function Mdx({ source, components, className }: { source: string; components?: MdxComponents; className?: string }) {
  return (
    <div
      className={cn(
        "prose prose-lab max-w-none prose-headings:tracking-tight prose-a:underline-offset-2 prose-code:rounded prose-code:bg-surface-2 prose-code:px-1 prose-code:py-0.5 prose-code:font-normal prose-code:before:content-none prose-code:after:content-none prose-table:block prose-table:overflow-x-auto prose-th:whitespace-nowrap",
        className,
      )}
    >
      <MDXRemote
        source={source}
        components={components ? { ...mdxComponents, ...components } : mdxComponents}
        options={{ mdxOptions: { remarkPlugins: [remarkGfm] } }}
      />
    </div>
  );
}
