/** Join class names, skipping falsy values. Enough for this app; no merge semantics. */
export function cn(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}
