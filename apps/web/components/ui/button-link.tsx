import Link from "next/link";
import type { ReactNode } from "react";
import { cn } from "@/lib/design/cn";

const variants = {
  primary: "bg-accent-solid text-accent-contrast shadow-card hover:shadow-lift hover:-translate-y-px",
  secondary: "border border-line-strong bg-surface text-fg hover:border-fg",
} as const;

/** A link styled as a button. External URLs open in the same tab, like every other link here. */
export function ButtonLink({
  href,
  children,
  variant = "primary",
  className,
}: {
  href: string;
  children: ReactNode;
  variant?: keyof typeof variants;
  className?: string;
}) {
  return (
    <Link
      href={href}
      className={cn(
        "inline-flex min-h-11 items-center justify-center gap-2 rounded-control px-5 text-sm font-medium",
        "transition duration-base ease-out-quint",
        variants[variant],
        className,
      )}
    >
      {children}
    </Link>
  );
}
