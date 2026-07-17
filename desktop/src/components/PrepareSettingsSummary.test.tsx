import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { PrepareSettingsSummary, STARTER_NOTICE } from "./PrepareSettingsSummary";

const summary = {
  source_has_creator_settings: true, kept_count: 4,
  compat_changed: [{ key: "printer", old: "other", new: "U1" }],
  could_not_carry: [{ key: "vendor.option", reason: "Unsupported" }],
  warnings: ["Print order kept"], recommendations_available: true,
  recommended_changes: [{ key: "speed", old: 20, new: 40 }],
};

describe("PrepareSettingsSummary", () => {
  it("renders kept, changed, and could-not-carry sections", () => {
    const html = renderToStaticMarkup(<PrepareSettingsSummary summary={summary} mode="preserve" />);
    expect(html).toContain("Kept from the original file");
    expect(html).toContain("Changed for U1 compatibility");
    expect(html).toContain("Could not carry over");
  });

  it("hides empty could-not-carry and only shows recommendations when available", () => {
    const none = { ...summary, could_not_carry: [], recommendations_available: false };
    const html = renderToStaticMarkup(<PrepareSettingsSummary summary={none} mode="preserve" />);
    expect(html).not.toContain("Could not carry over");
    expect(html).not.toContain("Optional recommendations");
  });

  it("renders the STL starter notice", () => {
    const html = renderToStaticMarkup(<PrepareSettingsSummary summary={{ ...summary, source_has_creator_settings: false, warnings: [] }} mode="starter" />);
    expect(html).toContain(STARTER_NOTICE);
  });
});
