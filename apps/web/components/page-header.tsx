import type { ReactNode } from "react";
import { Eyebrow } from "./ui/eyebrow";

export function PageHeader({ title, intro, eyebrow }: { title: string; intro?: ReactNode; eyebrow?: string }) {
  return (
    <header className="mb-12 max-w-3xl">
      {eyebrow ? <Eyebrow className="mb-4">{eyebrow}</Eyebrow> : null}
      <h1 className="text-title font-semibold">{title}</h1>
      {intro ? <p className="mt-4 text-lg text-muted">{intro}</p> : null}
    </header>
  );
}
