/** Site-wide settings. Name and domain are placeholders until decided. */
export const site = {
  name: "Lab",
  description: "A physical AI lab, documented from day one: experiments, builds, harness, and results.",
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
