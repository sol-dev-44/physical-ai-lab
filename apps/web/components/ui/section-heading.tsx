import Link from "next/link";
import type { ReactNode } from "react";
import { Eyebrow } from "./eyebrow";

export function SectionHeading({
  eyebrow,
  title,
  intro,
  href,
  linkLabel,
}: {
  eyebrow?: string;
  title: string;
  intro?: ReactNode;
  href?: string;
  linkLabel?: string;
}) {
  return (
    <div className="mb-8 flex flex-wrap items-end justify-between gap-x-6 gap-y-3">
      <div className="max-w-2xl">
        {eyebrow ? <Eyebrow className="mb-3">{eyebrow}</Eyebrow> : null}
        <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">{title}</h2>
        {intro ? <p className="mt-3 text-muted">{intro}</p> : null}
      </div>
      {href && linkLabel ? (
        <Link
          href={href}
          className="group inline-flex min-h-11 items-center gap-1 text-sm font-medium text-accent"
        >
          {linkLabel}
          <span aria-hidden className="transition-transform duration-base ease-out-quint group-hover:translate-x-0.5">
            →
          </span>
        </Link>
      ) : null}
    </div>
  );
}
