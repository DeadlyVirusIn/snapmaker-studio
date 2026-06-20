import { defineConfig } from "vitest/config";

// Pure-logic unit tests (no DOM): the plate-remap wizard's validation, gating,
// and view derivation. Node environment keeps it fast and dependency-light.
export default defineConfig({
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
