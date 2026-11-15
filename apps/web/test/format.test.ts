import { expect, it } from "vitest";
import { formatDate } from "../lib/format";

it("formats an ISO date without time zone shifts", () => {
  expect(formatDate("2026-11-01")).toBe("1 Nov 2026");
  expect(formatDate("2026-12-31")).toBe("31 Dec 2026");
});

it("returns anything unexpected unchanged", () => {
  expect(formatDate("not a date")).toBe("not a date");
});
