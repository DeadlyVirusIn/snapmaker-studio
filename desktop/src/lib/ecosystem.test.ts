import { describe, expect, it } from "vitest";
import type { EcosystemAdvice, EcosystemTool } from "@/api";
import {
  extraSuggestions,
  needsCaution,
  orcaReason,
  toolAction,
  toolErrorMessage,
} from "./ecosystem";

const tool = (over: Partial<EcosystemTool> = {}): EcosystemTool => ({
  id: "fork",
  name: "Nozzle Fork",
  kind: "slicer",
  official: false,
  role: "does a thing",
  url: "https://example.invalid/fork",
  license: "AGPL-3.0",
  install_hint: "download it",
  caution: "Community fork.",
  maturity: "preview",
  handoff: "file",
  stage: "before-slicing",
  score: 40,
  why: ["Mixed nozzle sizes."],
  installed: false,
  path: null,
  ...over,
});

const advice = (over: Partial<EcosystemAdvice> = {}): EcosystemAdvice => ({
  schema_version: "ecosystem/1",
  primary: null,
  alternatives: [],
  discover: [],
  summary: "",
  traits: {},
  ...over,
});

describe("toolAction", () => {
  it("offers a launch only for an installed tool that takes a file", () => {
    expect(toolAction(tool({ installed: true, path: "C:/x.exe" }))).toEqual({
      kind: "open",
      label: "Open in Nozzle Fork",
    });
  });

  it("never offers a launch for a tool that was not found on disk", () => {
    expect(toolAction(tool({ installed: false })).kind).toBe("link");
  });

  it("never offers a launch for a link-only tool even when installed", () => {
    // A browser extension or a web dashboard has no file handoff; offering
    // "Open in…" would be a button that cannot work.
    expect(toolAction(tool({ installed: true, handoff: "link" })).kind).toBe("link");
  });
});

describe("needsCaution", () => {
  it("is true for a preview tool that carries a caution", () => {
    expect(needsCaution(tool())).toBe(true);
  });

  it("is false for a stable tool", () => {
    expect(needsCaution(tool({ maturity: "stable" }))).toBe(false);
  });

  it("is false when there is no caution text to show", () => {
    expect(needsCaution(tool({ caution: null }))).toBe(false);
  });
});

describe("extraSuggestions", () => {
  it("is empty when nothing was advised", () => {
    expect(extraSuggestions(null)).toEqual([]);
    expect(extraSuggestions(advice())).toEqual([]);
  });

  it("drops Snapmaker Orca, which already has its own button", () => {
    const orca = tool({ id: "snapmaker-orca", name: "Snapmaker Orca", why: ["because"] });
    expect(extraSuggestions(advice({ primary: orca }))).toEqual([]);
  });

  it("drops anything the engine gave no reason for", () => {
    expect(extraSuggestions(advice({ alternatives: [tool({ why: [] })] }))).toEqual([]);
  });

  it("keeps a reasoned non-Orca suggestion", () => {
    const out = extraSuggestions(advice({ alternatives: [tool()] }));
    expect(out).toHaveLength(1);
    expect(out[0].id).toBe("fork");
  });

  it("does not list the same tool twice", () => {
    const out = extraSuggestions(advice({ primary: tool(), alternatives: [tool()] }));
    expect(out).toHaveLength(1);
  });
});

describe("orcaReason", () => {
  it("returns the engine's reason when Orca was recommended", () => {
    const orca = tool({ id: "snapmaker-orca", why: ["Already a U1 project."] });
    expect(orcaReason(advice({ primary: orca }))).toBe("Already a U1 project.");
  });

  it("stays quiet rather than inventing a reason", () => {
    expect(orcaReason(advice({ primary: tool({ id: "snapmaker-orca", why: [] }) }))).toBeNull();
    expect(orcaReason(advice())).toBeNull();
    expect(orcaReason(null)).toBeNull();
  });
});

describe("toolErrorMessage", () => {
  it("explains a missing install", () => {
    expect(toolErrorMessage(new Error("tool-not-found"), "Nozzle Fork")).toContain("isn’t installed");
  });

  it("explains an unsupported tool", () => {
    expect(toolErrorMessage(new Error("tool-not-supported"), "Nozzle Fork")).toContain("can’t open");
  });

  it("explains a missing file", () => {
    expect(toolErrorMessage(new Error("prepared-file-missing"), "X")).toContain("prepared file");
  });

  it("never leaks a path or a stack trace", () => {
    const msg = toolErrorMessage(new Error("launch-failed: C:\\Users\\someone\\secret\\x.exe"), "X");
    expect(msg).not.toContain("C:\\");
    expect(msg).not.toContain("someone");
  });
});
