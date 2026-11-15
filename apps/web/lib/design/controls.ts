/**
 * Shared class strings for form controls and panels, so buttons and inputs look the same on every
 * page (including the admin console) without a component per element.
 */
export const control = {
  button:
    "inline-flex min-h-11 items-center justify-center rounded-control border border-line-strong bg-surface px-4 text-sm font-medium transition-colors duration-fast hover:border-fg disabled:opacity-50",
  input:
    "min-h-11 rounded-control border border-line-strong bg-surface px-3 text-sm text-fg placeholder:text-subtle focus:border-accent",
  textLink: "font-medium text-accent underline underline-offset-2",
  panel: "rounded-card border border-line bg-surface p-5 shadow-card",
} as const;
