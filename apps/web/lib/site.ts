/** Site-wide settings. The domain is a placeholder until decided. */
export const site = {
  name: "Physical AI Lab",
  description:
    "A home robotics lab built like production infrastructure, documented from day one: experiments, harness, and results.",
  repo: "https://github.com/sol-dev-44/physical-ai-lab",
  url: process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
  nav: [
    { href: "/log", label: "Log" },
    { href: "/experiments", label: "Experiments" },
    { href: "/builds", label: "Builds" },
    { href: "/harness", label: "Harness" },
    { href: "/learning", label: "Learning Together" },
    { href: "/workshops", label: "Workshops" },
    { href: "/about", label: "About" },
  ],
} as const;
