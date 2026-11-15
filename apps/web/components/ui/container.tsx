import type { ReactNode } from "react";
import { cn } from "@/lib/design/cn";

/** Page-width or reading-width column with the site's side gutters. */
export function Container({
  children,
  size = "page",
  className,
}: {
  children: ReactNode;
  size?: "page" | "prose";
  className?: string;
}) {
  return (
    <div className={cn("mx-auto w-full px-5 sm:px-8", size === "page" ? "max-w-page" : "max-w-prose", className)}>
      {children}
    </div>
  );
}
