/** Site-wide settings. */
const productionHost = process.env.VERCEL_PROJECT_PRODUCTION_URL;

export const site = {
  name: "Physical AI Lab",
  tagline: "Robot learning at home, built like production.",
  description:
    "A one-person robotics lab teaching low-cost robots new skills: one gated path to hardware, one append-only event log, and results computed from the logs. Failures included.",
  repo: "https://github.com/sol-dev-44/physical-ai-lab",
  /** Canonical origin: explicit override, else Vercel's production domain, else local dev. */
  url: process.env.NEXT_PUBLIC_SITE_URL ?? (productionHost ? `https://${productionHost}` : "http://localhost:3000"),
  /** Sections with published content. Pages without content stay out of the menu until they have some. */
  nav: [
    { href: "/experiments", label: "Experiments" },
    { href: "/log", label: "Log" },
    { href: "/harness", label: "Harness" },
    { href: "/about", label: "About" },
  ],
} as const;

export type NavItem = (typeof site.nav)[number];
