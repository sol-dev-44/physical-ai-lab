const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** "2026-11-11" to "11 Nov 2026". Pure string work: no Date, so no time zone shifts. */
export function formatDate(iso: string): string {
  const [y, m, d] = iso.split("-");
  const month = months[Number(m) - 1];
  return month ? `${Number(d)} ${month} ${y}` : iso;
}
