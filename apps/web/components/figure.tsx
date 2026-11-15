import type { ReactNode } from "react";

/** A numbered-style figure for write-ups: content, then a caption. */
export function Figure({ children, caption }: { children: ReactNode; caption: string }) {
  return (
    <figure className="not-prose my-10 lg:-mx-24">
      {children}
      <figcaption className="mt-3 text-sm text-muted">{caption}</figcaption>
    </figure>
  );
}
