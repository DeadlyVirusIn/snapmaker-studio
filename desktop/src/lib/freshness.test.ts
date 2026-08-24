import { describe, expect, it } from "vitest";
import { readAt } from "./sendPlan";

/**
 * Every live fact has an age.
 *
 * The send path re-reads the machine before it uploads, so a stale answer cannot
 * cause a bad send. This line exists for the other half of the problem: a person
 * looking at a page that was drawn four minutes ago should be able to see that,
 * rather than reading it as what the printer is doing now.
 */
describe("saying when the printer was read", () => {
  const now = 1_000_000;

  it("says just now only when it is just now", () => {
    expect(readAt(now - 1, now)).toBe("Read from the printer just now.");
    expect(readAt(now - 30, now)).toBe("Read from the printer 30 seconds ago.");
  });

  it("keeps minutes readable rather than counting seconds forever", () => {
    expect(readAt(now - 60 * 4, now)).toBe("Read from the printer 4 minutes ago.");
    expect(readAt(now - 60, now)).toBe("Read from the printer 60 seconds ago.");
    expect(readAt(now - 95, now)).toBe("Read from the printer 2 minutes ago.");
  });

  it("says nothing rather than something wrong when there is no reading", () => {
    expect(readAt(undefined, now)).toBe("");
    expect(readAt(0, now)).toBe("");
  });
});
