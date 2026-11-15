import { ButtonLink } from "@/components/ui/button-link";
import { Eyebrow } from "@/components/ui/eyebrow";

export default function NotFound() {
  return (
    <div className="max-w-xl py-12">
      <Eyebrow className="mb-4">404</Eyebrow>
      <h1 className="text-title font-semibold">Nothing logged here.</h1>
      <p className="mt-4 text-muted">The page moved, or never existed. Every real result is linked from the experiments.</p>
      <div className="mt-8 flex flex-wrap gap-3">
        <ButtonLink href="/experiments">See the experiments</ButtonLink>
        <ButtonLink href="/" variant="secondary">
          Back home
        </ButtonLink>
      </div>
    </div>
  );
}
