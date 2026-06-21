import { describe, it, expect } from "vitest";
import {
  filterResults, linkOutUrl, importReasonLabel, DISCLAIMER,
  LINK_OUT_PROVIDERS, SANCTIONED_SOURCES,
  type ModelSearchResult,
} from "./modelSearch";

const results: ModelSearchResult[] = [
  { title: "Free CC bracket", source: "thingiverse", source_url: "https://t/1", license: "CC-BY-4.0",
    price_status: "free", file_formats: ["STL"], tags: ["bracket"], attribution: "maker_a",
    import_allowed: false, reason_import_not_allowed: "source_link_out_only" },
  { title: "Paid mini", source: "myminifactory", source_url: "https://m/2", license: "Standard",
    price_status: "paid", file_formats: ["STL", "3MF"], tags: ["multicolor"], attribution: "maker_b",
    import_allowed: false, reason_import_not_allowed: "paid" },
  { title: "Cults model", source: "cults3d", source_url: "https://c/3", license: "CC-BY-NC",
    price_status: "free", file_formats: ["3MF"], tags: [], attribution: "maker_c",
    import_allowed: false, reason_import_not_allowed: "no_download_api" },
];

describe("7. filters work", () => {
  it("free only", () => {
    expect(filterResults(results, { freeOnly: true }).map((r) => r.title)).toEqual(["Free CC bracket", "Cults model"]);
  });
  it("commercial-use excludes NC", () => {
    const out = filterResults(results, { commercialUse: true }).map((r) => r.title);
    expect(out).toContain("Free CC bracket");      // CC-BY allows commercial
    expect(out).not.toContain("Cults model");      // CC-BY-NC excluded
  });
  it("format 3MF", () => {
    expect(filterResults(results, { formats: ["3MF"] }).map((r) => r.title)).toEqual(["Paid mini", "Cults model"]);
  });
  it("multi-color tag", () => {
    expect(filterResults(results, { multiColor: true }).map((r) => r.title)).toEqual(["Paid mini"]);
  });
  it("source filter", () => {
    expect(filterResults(results, { sources: ["thingiverse"] }).map((r) => r.title)).toEqual(["Free CC bracket"]);
  });
});

describe("8. link-out URLs built correctly", () => {
  it("encodes the query per provider", () => {
    expect(linkOutUrl("printables", "cat toy")).toBe("https://www.printables.com/search/models?q=cat%20toy");
    expect(linkOutUrl("thangs", "cat toy")).toBe("https://thangs.com/search/cat%20toy");
    expect(linkOutUrl("makerworld", "cat toy")).toBe("https://makerworld.com/en/search/models?keyword=cat%20toy");
  });
});

describe("9. import disabled when not allowed", () => {
  it("every result is import-disabled in v1 with a reason label", () => {
    for (const r of results) {
      expect(r.import_allowed).toBe(false);
      expect(importReasonLabel(r.reason_import_not_allowed).length).toBeGreaterThan(0);
    }
    expect(importReasonLabel("paid")).toContain("Paid");
    expect(importReasonLabel("no_download_api")).toContain("No download API");
  });
});

describe("10. license/attribution visible", () => {
  it("results carry license + attribution to render", () => {
    for (const r of results) {
      expect(r.license).toBeTruthy();
      expect(r.attribution).toBeTruthy();
    }
  });
});

describe("11. disclaimer present", () => {
  it("has the source/license disclaimer", () => {
    expect(DISCLAIMER.toLowerCase()).toContain("respect each model");
  });
});

describe("12. link-out providers are separate from sanctioned search providers", () => {
  it("printables/thangs/makerworld are link-out only, never sanctioned", () => {
    const linkout = LINK_OUT_PROVIDERS.map((p) => p.id);
    expect(linkout).toEqual(["printables", "thangs", "makerworld"]);
    for (const id of linkout) {
      expect(SANCTIONED_SOURCES).not.toContain(id as unknown as (typeof SANCTIONED_SOURCES)[number]);
    }
  });
});
