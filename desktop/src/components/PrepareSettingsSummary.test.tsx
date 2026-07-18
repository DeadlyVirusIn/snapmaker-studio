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
  it("renders kept, adjusted, and could-not-carry sections", () => {
    const html = renderToStaticMarkup(<PrepareSettingsSummary summary={summary} mode="preserve" />);
    expect(html).toContain("Kept from the original file");
    expect(html).toContain("Adjusted for U1 project compatibility");
    expect(html).toContain("Could not carry over");
  });

  it("hides empty could-not-carry and only shows recommendations when available", () => {
    const none = { ...summary, could_not_carry: [], recommendations_available: false };
    const html = renderToStaticMarkup(<PrepareSettingsSummary summary={none} mode="preserve" />);
    expect(html).not.toContain("Could not carry over");
    expect(html).not.toContain("Optional recommendations");
  });

  it("renders the STL starter notice", () => {
    const html = renderToStaticMarkup(<PrepareSettingsSummary summary={{ ...summary, source_has_creator_settings: false, warnings: [] }} mode="starter" isStl />);
    expect(html).toContain(STARTER_NOTICE);
  });

  it("omits empty sections and renders all starter warnings", () => {
    const html = renderToStaticMarkup(<PrepareSettingsSummary summary={{ ...summary, kept_count: 0, compat_changed: [], recommendations_available: true, recommended_changes: [] }} mode="preserve" />);
    expect(html).not.toContain("Kept from the original file");
    expect(html).not.toContain("Adjusted for U1 project compatibility");
    expect(html).not.toContain("Optional recommendations");
    const starter = renderToStaticMarkup(<PrepareSettingsSummary summary={{ ...summary, source_has_creator_settings: false, warnings: ["one", "two"] }} mode="starter" isStl={false} />);
    expect(starter).toContain("This file does not include creator slicer settings");
    expect(starter).toContain("Warnings");
    expect(starter).toContain("one");
    expect(starter).toContain("two");
  });

  it("keeps mapped temperatures out of the adjusted section", () => {
    const withMapped = {
      ...summary,
      mapped_to_u1: [
        { key: "nozzle_temperature", old: [210, 215], new: [210, 215, 215, 215] },
        { key: "nozzle_temperature_initial_layer", old: [215, 220], new: [215, 220, 220, 220] },
      ],
    };
    const html = renderToStaticMarkup(<PrepareSettingsSummary summary={withMapped} mode="preserve" />);
    expect(html).toContain("Creator temperature values were preserved and mapped to the U1 toolhead layout.");
    expect(html).toMatch(/Kept from the original file[\s\S]*nozzle_temperature[\s\S]*<\/details><\/section>/);
    const adjusted = html.slice(html.indexOf("Adjusted for U1 project compatibility"));
    expect(adjusted).not.toContain("nozzle_temperature");
  });

  it("uses plain compatibility bullets and shows unmatched keys before technical detail", () => {
    const withRawChanges = {
      ...summary,
      compat_changed: [
        { key: "compatible_printers", old: ["other"], new: ["Snapmaker U1"] },
        { key: "machine_start_gcode", old: "old", new: "new" },
        { key: "machine_end_gcode", old: "old", new: "new" },
        { key: "wipe_tower_x", old: 10, new: 20 },
      ],
    };
    const html = renderToStaticMarkup(<PrepareSettingsSummary summary={withRawChanges} mode="preserve" />);
    expect(html).toContain("Printer identity changed to Snapmaker U1");
    expect(html).toContain("U1 machine start/end G-code applied");
    expect(html).not.toContain("Project wrapper fields updated for U1");
    const adjusted = html.slice(html.indexOf("Adjusted for U1 project compatibility"));
    const technicalAt = adjusted.indexOf("<details");
    const defaultView = adjusted.slice(0, technicalAt);
    const technicalDetail = adjusted.slice(technicalAt);
    expect(defaultView).not.toContain("machine_start_gcode");
    expect(defaultView).not.toContain("machine_end_gcode");
    expect(defaultView).not.toContain("compatible_printers");
    expect(defaultView).toContain("wipe_tower_x");
    expect(technicalDetail).toContain("machine_start_gcode");
    expect(technicalDetail).toContain("machine_end_gcode");
    expect(technicalDetail).toContain("compatible_printers");
    expect(technicalDetail).toContain("wipe_tower_x");
    expect(html).not.toMatch(/<details[^>]*\sopen(?:=|\s|>)/);
  });

  it("shows only-start G-code and unmatched compatibility changes in the default view", () => {
    const html = renderToStaticMarkup(<PrepareSettingsSummary summary={{
      ...summary,
      compat_changed: [
        { key: "machine_start_gcode", old: "old", new: "new" },
        { key: "pressure_advance", old: 0.02, new: 0.035 },
      ],
    }} mode="preserve" />);
    expect(html).toContain("U1 machine start G-code applied");
    expect(html).not.toContain("U1 machine start/end G-code applied");
    const adjusted = html.slice(html.indexOf("Adjusted for U1 project compatibility"));
    const defaultView = adjusted.slice(0, adjusted.indexOf("<details"));
    expect(defaultView).toContain("pressure_advance");
  });

  it("accepts legacy summaries without mapped_to_u1", () => {
    expect(() => renderToStaticMarkup(<PrepareSettingsSummary summary={summary} mode="preserve" />)).not.toThrow();
  });
});
