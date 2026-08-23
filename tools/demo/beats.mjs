// Drive the demo beats through the running application over CDP.
//
// The pacing matches docs/innovation-fund/DEMO_SCRIPT_90_SECONDS.md. Each beat
// scrolls to a real card and waits long enough for it to be readable, so the
// recording is the application working rather than a slideshow of it.
//
// Usage: node beats.mjs <cdpUrl>

import { chromium } from "playwright-core";

const [, , cdpUrl] = process.argv;
const browser = await chromium.connectOverCDP(cdpUrl);

const beat = (name, ms) => {
  console.log(`  ${name}`);
  return new Promise((r) => setTimeout(r, ms));
};

try {
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find((p) => p.url().startsWith("http://tauri.localhost"));
  if (!page) throw new Error("app window not found over CDP");

  const goto = async (path, wait = 3500) => {
    await page.evaluate((p) => {
      window.history.pushState({}, "", p);
      window.dispatchEvent(new PopStateEvent("popstate"));
    }, path);
    await page.waitForTimeout(wait);
  };

  const scrollTo = async (text, pause = 3000) => {
    await page.evaluate((needle) => {
      const el = [...document.querySelectorAll("h1,h2,h3,p,span,button")]
        .find((n) => n.textContent && n.textContent.trim().startsWith(needle));
      if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
    }, text);
    await page.waitForTimeout(pause);
  };

  // 0:00 — the dashboard, so the viewer sees what the product is.
  await beat("dashboard", 5000);

  // 0:10 — the finding no size check can produce.
  await goto("/compatibility", 5000);
  await scrollTo("Object placement", 6000);

  // 0:25 — the fix, in a new copy.
  const moveButton = page.getByRole("button", { name: /Move onto the plate/i }).first();
  if (await moveButton.count()) {
    await moveButton.click();
    await beat("placement fix applied", 6000);
  }

  // 0:40 — this project, on this printer.
  await scrollTo("Before you slice", 7000);

  // 0:52 — prepare, and every change accounted for.
  const prepare = page.getByRole("button", { name: /Prepare U1 copy/i }).first();
  if (await prepare.count()) {
    await prepare.click();
    await beat("preparing a U1 copy", 8000);
  }

  // 1:00 — proof, not a promise.
  await scrollTo("What survived preparing this copy", 7000);

  // 1:10 — the way back.
  await scrollTo("Changes Studio made", 6000);

  // 1:18 — the right tool for this file.
  await scrollTo("Best tool for this project", 5000);

  // 1:25 — six colours, four toolheads.
  await goto("/colors", 5000);
  await scrollTo("Colours and toolheads", 6000);

  console.log("beats complete");
} finally {
  await browser.close();
}
