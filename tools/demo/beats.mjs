// Drive the demo beats through the running application over CDP.
//
// The pacing matches docs/innovation-fund/DEMO_SCRIPT_90_SECONDS.md. Each beat
// scrolls to a real card and waits long enough for it to be readable, so the
// recording is the application working rather than a slideshow of it.
//
// Two cuts exist. The default is the full walkthrough. `short` is the cut used as
// the primary proof: it reaches the actual problem in about four seconds, because
// a viewer deciding whether this project is worth their attention gives it
// roughly that long, and an opening shot of a dashboard answers none of their
// questions.
//
// Usage: node beats.mjs <cdpUrl> [short]

import { chromium } from "playwright-core";

const [, , cdpUrl, cut] = process.argv;
const short = cut === "short";

/** Hold times in milliseconds, per cut. */
const T = short
  ? { open: 1500, nav: 2500, problem: 5000, fix: 4500, preflight: 5500,
      prepare: 6000, fidelity: 5500, ledger: 4000, tool: 3500,
      coloursNav: 2500, colours: 5000 }
  : { open: 5000, nav: 5000, problem: 6000, fix: 6000, preflight: 7000,
      prepare: 8000, fidelity: 7000, ledger: 6000, tool: 5000,
      coloursNav: 5000, colours: 6000 };
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

  // The app, briefly — long enough to see it is a real desktop application.
  await beat("open", T.open);

  // The problem, as early as possible: one object hangs off the plate, named to
  // the millimetre. This is the beat everything else depends on.
  await goto("/compatibility", T.nav);
  await scrollTo("Object placement", T.problem);

  // The fix, in a new copy — the original is untouched and the card says so.
  const moveButton = page.getByRole("button", { name: /Move onto the plate/i }).first();
  if (await moveButton.count()) {
    await moveButton.click();
    await beat("placement fix applied", T.fix);
  }

  // This project, against this printer — including the honest unknowns.
  await scrollTo("Before you slice", T.preflight);

  // Prepare, and account for every change.
  const prepare = page.getByRole("button", { name: /Prepare U1 copy/i }).first();
  if (await prepare.count()) {
    await prepare.click();
    await beat("preparing a U1 copy", T.prepare);
  }

  // Proof, not a promise.
  await scrollTo("What survived preparing this copy", T.fidelity);

  // The way back.
  await scrollTo("Changes Studio made", T.ledger);

  // The right tool for this file, even when it is not this one.
  await scrollTo("Best tool for this project", T.tool);

  // Six colours, four toolheads.
  await goto("/colors", T.coloursNav);
  await scrollTo("Colours and toolheads", T.colours);

  console.log("beats complete");
} finally {
  await browser.close();
}
