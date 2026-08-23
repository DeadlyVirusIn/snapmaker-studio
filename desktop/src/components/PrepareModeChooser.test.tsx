import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { PrepareModeChooser } from "./PrepareModeChooser";

describe("PrepareModeChooser", () => {
  it("renders three choices with preserve selected", () => {
    const html = renderToStaticMarkup(<PrepareModeChooser mode="preserve" onModeChange={vi.fn()} onCustom={vi.fn()} />);
    expect(html).toContain("Preserve creator settings");
    expect(html).toContain("Use Studio&#x27;s U1 starter settings instead");
    // The default has to be marked, or a beginner is handed a coin flip.
    expect(html).toContain("Recommended");
    expect(html).toContain("Custom");
    expect(html).toContain('checked=""');
  });
});
