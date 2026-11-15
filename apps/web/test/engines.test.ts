/** A failed WASM download must not poison the engine for the rest of the visit. */
import { expect, it, vi } from "vitest";

let failNext = true;

vi.mock("@lab/events-wasm", () => ({
  loadLab: async () => {
    if (failNext) {
      failNext = false;
      throw new Error("network error");
    }
    return { openRun: () => ({}) };
  },
}));

const { loadWasmEngine } = await import("../lib/replay/engines");

it("retries the WASM engine after a failed load", async () => {
  await expect(loadWasmEngine()).rejects.toThrow("network error");
  await expect(loadWasmEngine()).resolves.toMatchObject({ name: "wasm" });
});
