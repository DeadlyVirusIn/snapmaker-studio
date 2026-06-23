import { describe, it, expect } from "vitest";
import {
  filterResults, linkOutUrl, importReasonLabel, DISCLAIMER,
  LINK_OUT_PROVIDERS, SANCTIONED_SOURCES, BROWSE_PROVIDERS, siteHomeUrl,
  APPROVED_MODEL_DOMAINS, isApprovedModelUrl,
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

describe("13. Model Browser: all six approved sites are browsable (link-out)", () => {
  it("lists the six approved sites", () => {
    expect(BROWSE_PROVIDERS.map((p) => p.id)).toEqual([
      "printables", "thingiverse", "myminifactory", "cults3d", "thangs", "makerworld",
    ]);
  });
  it("builds a search URL per site for a query", () => {
    expect(linkOutUrl("thingiverse", "cat toy")).toContain("thingiverse.com/search?q=cat%20toy");
    expect(linkOutUrl("myminifactory", "cat toy")).toContain("myminifactory.com/search?query=cat%20toy");
    expect(linkOutUrl("cults3d", "cat toy")).toContain("cults3d.com/en/search?q=cat%20toy");
    for (const p of BROWSE_PROVIDERS) {
      expect(linkOutUrl(p.id, "cat toy").startsWith("https://")).toBe(true);
    }
  });
  it("falls back to the site home when there is no query (browse, not API)", () => {
    for (const p of BROWSE_PROVIDERS) {
      expect(linkOutUrl(p.id, "")).toBe(siteHomeUrl(p.id));
      expect(siteHomeUrl(p.id).startsWith("https://")).toBe(true);
    }
  });
});

describe("14. Model Browser allowlist (in-app browser security boundary)", () => {
  it("covers the six approved sites", () => {
    expect([...APPROVED_MODEL_DOMAINS]).toEqual([
      "printables.com", "thingiverse.com", "myminifactory.com",
      "cults3d.com", "thangs.com", "makerworld.com",
    ]);
  });
  it("approves every browse provider's start URL (and its subdomains)", () => {
    for (const p of BROWSE_PROVIDERS) {
      expect(isApprovedModelUrl(linkOutUrl(p.id, "cube"))).toBe(true);
      expect(isApprovedModelUrl(siteHomeUrl(p.id))).toBe(true);
    }
    expect(isApprovedModelUrl("https://account.makerworld.com/login")).toBe(true);
  });
  it("blocks off-allowlist, non-https, and junk URLs", () => {
    expect(isApprovedModelUrl("https://evil.com/malware")).toBe(false);
    expect(isApprovedModelUrl("https://google.com")).toBe(false);
    expect(isApprovedModelUrl("http://printables.com")).toBe(false);   // not https
    expect(isApprovedModelUrl("https://notprintables.com")).toBe(false);
    expect(isApprovedModelUrl("javascript:alert(1)")).toBe(false);
    expect(isApprovedModelUrl("not a url")).toBe(false);
  });
});
