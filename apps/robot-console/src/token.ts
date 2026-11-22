const KEY = "robot-token";

/** The pairing token: from the link `lab console` printed (in the URL fragment, so it never
 * reaches a server log; then stored and stripped from the address bar), or from local storage on
 * later visits. Null if never paired. */
export function takeToken(href: string, replace: (url: string) => void): string | null {
  const url = new URL(href);
  const fromLink = new URLSearchParams(url.hash.slice(1)).get("token");
  if (fromLink) {
    localStorage.setItem(KEY, fromLink);
    url.hash = "";
    replace(url.toString().replace(/#$/, ""));
    return fromLink;
  }
  return localStorage.getItem(KEY);
}

/** Forget a token the robot rejected, so the next visit asks for a fresh pairing link. */
export function forgetToken(): void {
  localStorage.removeItem(KEY);
}
