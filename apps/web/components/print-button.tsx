"use client";

import { control } from "@/lib/design/controls";

/** Opens the browser's print dialog; the print stylesheet turns the page into a clean document. */
export function PrintButton() {
  return (
    <button type="button" onClick={() => window.print()} className={`${control.button} print:hidden`}>
      Print or save as PDF
    </button>
  );
}
