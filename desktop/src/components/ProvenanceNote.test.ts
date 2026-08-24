import { describe, expect, it } from "vitest";
import { verdictLabel, verdictTone } from "./ProvenanceNote";

describe("how sure Studio says it is about a picked-up job", () => {
  it("never presents an unsure match as the user's project", () => {
    expect(verdictLabel("confirmed")).toBe("This is your project, sliced");
    expect(verdictLabel("likely")).toBe("Looks like your project");
    expect(verdictLabel("ambiguous")).toBe("Studio can't tell");
    expect(verdictLabel("unknown")).toBe("Not enough to compare");
    expect(verdictLabel("no_match")).toBe("A different project");
  });

  it("tones an unsure match as neutral, not as success or failure", () => {
    expect(verdictTone("confirmed")).toBe("ready");
    expect(verdictTone("likely")).toBe("ready");
    expect(verdictTone("ambiguous")).toBe("muted");
    expect(verdictTone("unknown")).toBe("muted");
    expect(verdictTone("no_match")).toBe("risk");
    expect(verdictTone(undefined)).toBe("muted");
  });
});
