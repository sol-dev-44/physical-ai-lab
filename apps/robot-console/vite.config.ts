import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// In dev, the page comes from Vite and the WebSocket from `lab console` on :8080.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/ws": { target: "ws://localhost:8080", ws: true } } },
  test: { environment: "jsdom", globals: true, setupFiles: ["src/test-setup.ts"] },
});
