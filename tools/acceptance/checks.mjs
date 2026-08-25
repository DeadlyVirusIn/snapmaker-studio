// Installed-build acceptance checks, driven over the Chrome DevTools Protocol
// against the *installed* Snapmaker Studio — not the dev server.
//
// Tauri renders the UI in WebView2, and WebView2 accepts browser arguments via
// WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS. Launching the installed app with
// `--remote-debugging-port` therefore exposes the real, shipped webview to a
// standard CDP client. That is what makes this a genuine installed-build test
// rather than pixel-poking: every assertion reads the DOM the user sees, and the
// API calls run inside the app's own origin against the frozen sidecar.
//
// Run one phase per invocation so the PowerShell driver can interleave native
// steps (the file dialog) that CDP cannot reach.
//
// Usage: node checks.mjs <phase> <cdpUrl> <outDir> [samplePath] [gcodePath] [paintedPath]

import { chromium } from "playwright-core";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const [, , phase, cdpUrl, outDir, samplePath, gcodePath, paintedPath] = process.argv;
mkdirSync(outDir, { recursive: true });

const results = [];
const record = (name, ok, detail = "") => {
  results.push({ name, ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? `  — ${detail}` : ""}`);
};

async function appPage(browser) {
  const ctx = browser.contexts()[0];
  for (const page of ctx.pages()) {
    if (page.url().startsWith("http://tauri.localhost")) return page;
  }
  throw new Error("the app window was not found over CDP");
}

/** Call a documented route from inside the app's own origin. */
async function callRoute(page, route, body) {
  return page.evaluate(
    async ([route, body]) => {
      const info = await window.__TAURI_INTERNALS__.invoke("get_api_info");
      const res = await fetch(`http://127.0.0.1:${info.port}${route}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Auth-Token": info.token },
        body: JSON.stringify(body),
      });
      return { status: res.status, body: await res.json() };
    },
    [route, body],
  );
}

const shot = async (page, name) => {
  await page.screenshot({ path: join(outDir, `${name}.png`) });
};

async function phaseStartup(page) {
  record("App window present", (await page.title()) === "Snapmaker Studio", await page.title());

  const info = await page.evaluate(() =>
    window.__TAURI_INTERNALS__.invoke("get_api_info"));
  record("Sidecar handshake", Boolean(info?.port && info?.token),
    `port ${info?.port}`);

  const health = await page.evaluate(async () => {
    const i = await window.__TAURI_INTERNALS__.invoke("get_api_info");
    const r = await fetch(`http://127.0.0.1:${i.port}/health`);
    return { status: r.status, body: await r.json() };
  });
  record("Engine /health from the app origin", health.status === 200,
    JSON.stringify(health.body).slice(0, 90));

  // The shipped Rust command table, exercised against the real machine.
  const tools = await page.evaluate(() =>
    window.__TAURI_INTERNALS__.invoke("detect_tools"));
  record("Ecosystem tool detection (shell)", typeof tools === "object",
    `${Object.keys(tools || {}).length} installed tool(s) found: ${Object.keys(tools || {}).join(", ") || "none"}`);

  const orca = await page.evaluate(() =>
    window.__TAURI_INTERNALS__.invoke("detect_orca"));
  record("Snapmaker Orca detection", orca === null || typeof orca === "string",
    orca ? "installed" : "not installed on this machine");

  await shot(page, "01-dashboard");
}

async function phaseRoutes(page) {
  const routes = [
    ["/project_traits", { path: samplePath }, (b) => b.readable === true],
    ["/placement_check", { path: samplePath }, (b) => b.available === true && b.off_plate.length === 1],
    ["/color_plan", { path: samplePath }, (b) => b.color_count === 6 && b.verdict === "possible_with_swaps"],
    // Painted colour, read by the engine this installer actually ships. The
    // project is painted with filament 2 at the bottom and filament 3 thirty
    // millimetres up, so the answers are known before the app is asked: two
    // slots, and a separation the geometry proves.
    ["/project_traits", { path: paintedPath }, (b) => b.has_painted_color?.value === true],
    ["/color_plan", { path: paintedPath },
      (b) => b.painted?.painted === true
        && JSON.stringify(b.painted?.slots) === "[2,3]"
        && b.painted?.painted_facets === 2],
    // The flagship answer: two painted colours whose objects cannot meet on a
    // layer are offered as a planned swap rather than each demanding a toolhead.
    ["/color_plan", { path: paintedPath },
      (b) => b.layer_based.some((c) => c.slot === 3 && c.painted === true
        && Math.abs((c.from_z_mm ?? 0) - 30) < 0.01)],
    ["/color_plan", { path: paintedPath },
      (b) => (b.painted?.coexistence?.pairs ?? []).length > 0
        && (b.painted?.coexistence?.pairs ?? []).every((p) => p.verdict === "separate")],
    ["/project_cost", { path: samplePath }, (b) => b.available === false && Boolean(b.reason)],
    ["/ecosystem_advice", { path: samplePath }, (b) => Boolean(b.primary?.why?.length)],
    ["/preflight", { path: samplePath, host: "", port: 7125 }, (b) => Array.isArray(b.checks) && b.checks.length > 0],
    ["/fix_history", {}, (b) => Array.isArray(b.entries)],
    // The post-slice half. gcodePath is written by the PowerShell driver next to
    // the sample, because a sliced job is the one input the installed build
    // cannot produce for itself — Studio does not slice.
    ["/gcode_facts", { path: gcodePath },
      (b) => b.available === true && b.printer_model === "Snapmaker U1" && b.layer_count === 12],
    ["/post_slice", { path: gcodePath, host: "", port: 7125 },
      (b) => b.available === true && Array.isArray(b.checks) && b.checks.length > 0
             && !b.checks.some((c) => c.result === "blocked" || c.result === "attention")],
    ["/sliced_cost", { path: gcodePath },
      (b) => b.available === true && b.total_grams === 0.36 && b.waste.separable === false],
    ["/diagnostics_preview", {},
      (b) => typeof b.text === "string" && b.text.length > 0 && /Nothing has been sent/.test(b.note)],
    ["/print_plan", { path: gcodePath },
      (b) => b.available === true && b.layers_seen > 0 && Array.isArray(b.narration)
             && b.narration.every((line) => Boolean(line.evidence))],
    ["/material_plan", { path: gcodePath, host: "", port: 7125 },
      (b) => b.available === true && b.printer_known === false],
    ["/send_check", { path: gcodePath, host: "", port: 7125 },
      (b) => b.available === true && b.counts.blocker === 0
             && b.items.some((i) => i.kind === "unknown")],
    // The round-trip: the folder holding the job is watched, and a job that did
    // not come from the open project must never be claimed as a match.
    ["/watch_folder", { folder: outDir },
      (b) => b.available === true && Array.isArray(b.candidates)],
    ["/slice_provenance", { project_path: samplePath, gcode_path: gcodePath },
      (b) => ["confirmed", "likely", "ambiguous", "no_match", "unknown"].includes(b.verdict)],
  ];
  for (const [route, body, verify] of routes) {
    try {
      const { status, body: payload } = await callRoute(page, route, body);
      record(`Engine route ${route}`, status === 200 && verify(payload),
        status === 200 ? "" : `HTTP ${status}`);
    } catch (e) {
      record(`Engine route ${route}`, false, String(e).slice(0, 90));
    }
  }
}

async function phasePostSlice(page) {
  await page.evaluate(() => {
    window.history.pushState({}, "", "/after-slicing");
    window.dispatchEvent(new PopStateEvent("popstate"));
  });
  await page.waitForTimeout(1500);

  let body = await page.locator("body").innerText();
  record("After Slicing page renders", body.includes("After slicing"), "");

  // Type the sliced job's path in, the way a user without a file association would.
  const field = page.locator('input[aria-label="Path to a sliced G-code file"]').first();
  if (await field.count()) {
    await field.fill(gcodePath);
    await page.getByRole("button", { name: /Check this job/i }).first().click();
    // Four cards each read the file and ask the printer. A fixed three seconds
    // asserted against spinners when the printer was slow to answer, which reads
    // as "the app does not render this" and is not what happened.
    for (let waited = 0; waited < 40000; waited += 1000) {
      const text = await page.locator("body").innerText();
      const settling = /checking whether this job is ready|reading the sliced file|checking what is loaded/i;
      if (!settling.test(text)) break;
      await page.waitForTimeout(1000);
    }
  }
  body = await page.locator("body").innerText();
  const has = (s) => body.includes(s);

  record("Sliced job read in the installed app",
    has("What the printer will actually do") && has("Snapmaker Orca"), "");
  // The labels are uppercased by CSS, and innerText returns the transformed
  // text, so this compares case-insensitively rather than against the source.
  const lower = body.toLowerCase();
  record("Job facts rendered from the file",
    lower.includes("prints from") && lower.includes("layers")
    && lower.includes("estimated time"), "");
  record("Post-slice honest unknown present",
    has("Studio can’t tell") || has("Studio can't tell"), "");
  record("Purge is not split when the file does not split it",
    /not separate|will not split|no tool-change purge/i.test(body), "");
  record("No print-success promise after slicing",
    !/will print successfully|guaranteed/i.test(body), "");

  // The three answers that only exist after slicing.
  record("Ready-to-send verdict rendered", lower.includes("ready to send?"), "");
  record("What to load rendered", lower.includes("what to load"), "");
  record("Send confirmation blocks nothing without a printer",
    !/will stop the print/i.test(body), "");

  const planButton = page.getByRole("button", { name: /Read the whole job/i }).first();
  if (await planButton.count()) {
    await planButton.click();
    await page.waitForTimeout(2500);
  }
  const withPlan = await page.locator("body").innerText();
  record("Print plan timeline rendered on request",
    /what happens during this print/i.test(withPlan) && /prints with slot/i.test(withPlan), "");
  record("Timeline keeps its evidence", /evidence/i.test(withPlan), "");
  record("The round-trip watcher is offered", /pick up sliced jobs automatically/i.test(withPlan)
    || /watching for sliced jobs/i.test(withPlan), "");

  // The send button lives with the checks it is based on, and says what it does —
  // or says why it is not there, which is the case a novice hits first.
  record("Sending is offered, or its absence is explained",
    /send this job to the printer/i.test(withPlan)
    || /connect your u1 in printer hub/i.test(withPlan)
    || /cannot reach your printer/i.test(withPlan), "");
  record("Sending never claims to start a print",
    !/start (the|this) print automatically/i.test(withPlan), "");

  await shot(page, "05-after-slicing");
}

async function phaseCockpit(page) {
  await page.evaluate(() => {
    window.history.pushState({}, "", "/this-print");
    window.dispatchEvent(new PopStateEvent("popstate"));
  });
  await page.waitForTimeout(4000);
  const body = await page.locator("body").innerText();
  const lower = body.toLowerCase();

  record("Cockpit renders the job's stages",
    lower.includes("this print") && lower.includes("before slicing")
    && lower.includes("after slicing"), "");
  record("Cockpit shows the real findings, not placeholders",
    /hangs [\d.]+ mm past the \w+ edge/i.test(body), "");
  record("Cockpit keeps the honest unknown",
    lower.includes("studio can’t tell") || lower.includes("studio can't tell"), "");
  record("Cockpit still says Orca slices", /snapmaker orca/i.test(body), "");
  await shot(page, "06-cockpit");
}

/**
 * The half of provenance a person actually reads.
 *
 * The engine can be right about a job and still leave someone unable to act on
 * it. This drives the real page and asserts that the verdict is stated, that the
 * reasoning is reachable, and that a model's object names never appear in it.
 */
async function phaseProvenance(page) {
  await page.evaluate(() => {
    window.history.pushState({}, "", "/after-slicing");
    window.dispatchEvent(new PopStateEvent("popstate"));
  });
  await page.waitForTimeout(1500);
  const field = page.locator('input[aria-label="Path to a sliced G-code file"]').first();
  if (await field.count()) {
    await field.fill(gcodePath);
    await page.getByRole("button", { name: /Check this job/i }).first().click();
    await page.waitForTimeout(3000);
  }

  // The send card gathers a G-code read, a printer probe and a provenance
  // comparison before it can say anything. Waiting a fixed three seconds caught
  // it mid-thought and read the spinner as an empty answer.
  const settled = /what studio compared|no project is open, so studio cannot tell/i;
  for (let waited = 0; waited < 30000; waited += 1000) {
    const text = await page.locator("body").innerText();
    if (settled.test(text)) break;
    await page.waitForTimeout(1000);
  }

  const details = page.getByText(/What Studio compared/i).first();
  const offered = (await details.count()) > 0;
  if (offered) {
    await details.click();
    await page.waitForTimeout(600);
  }
  const body = await page.locator("body").innerText();
  // Opened without a project there is nothing to compare, and that must be said
  // rather than left blank: silence on this page reads as "fine".
  record("Why Studio reads a job as it does is reachable",
    offered || /no project is open, so studio cannot tell/i.test(body),
    offered ? "" : "compared against no open project");
  if (offered) {
    record("The two kinds of evidence are kept apart",
      /identifies the model/i.test(body) && /describes the setup/i.test(body), "");
    record("Object names stay out of the explanation",
      /fingerprints of the object names/i.test(body), "");
  }

  // The expert half: every simplified verdict can show what it was read from,
  // and the page says how old the printer reading is.
  const wheres = page.getByText(/Where this came from/i);
  const count = await wheres.count();
  record("Every verdict can show what it was read from", count > 0, `${count} item(s)`);
  if (count > 0) {
    for (let index = 0; index < Math.min(count, 4); index += 1) {
      await wheres.nth(index).click();
    }
    await page.waitForTimeout(500);
    const expanded = await page.locator("body").innerText();
    record("The disclosure names a source, not a placeholder",
      /g-code|printer|project and job|firmware|traced on a real u1/i.test(expanded), "");
    // The sliced job in this harness is named for the sample project; a source
    // line must never carry a file or model name.
    const model = gcodePath.split(/[\\/]/).pop().replace(/\.gcode$/i, "");
    const sources = expanded.split(/Where this came from/i).slice(1)
      .map((chunk) => chunk.split(/\r?\n/).slice(0, 3).join(" ")).join(" ");
    record("Expert evidence carries no file or model name",
      !sources.toLowerCase().includes(model.toLowerCase()),
      sources.slice(0, 80));
  }
  record("The age of the printer reading is stated, or there is no reading",
    /read from the printer|no printer to check against|cannot reach your printer|connect your u1/i
      .test(body), "");

  await shot(page, "07-provenance");
}

/**
 * The states a person hits on their first evening, driven through the shipped UI.
 *
 * Each one is a place where Studio could say nothing and leave someone stuck. The
 * assertions are not about wording; they are that *something* is said, in the
 * place the person is looking, naming what happened and what to do next.
 *
 * These are the cases reachable without a printer. The rest — an empty slot, the
 * wrong material, not enough filament, a pending upload — are checked against a
 * real U1 by tools/hardware/verify.ps1.
 */
async function phaseNovice(page) {
  await page.evaluate(() => {
    window.history.pushState({}, "", "/after-slicing");
    window.dispatchEvent(new PopStateEvent("popstate"));
  });
  await page.waitForTimeout(1200);

  const field = () => page.locator('input[aria-label="Path to a sliced G-code file"]').first();
  const check = async (path) => {
    // With a job already open the page shows that job; swapping files is what
    // "Choose another file" is for, and it is the route a person takes too.
    if (!(await field().count())) {
      const another = page.getByRole("button", { name: /Choose another file/i }).first();
      if (await another.count()) {
        await another.click();
        await page.waitForTimeout(800);
      }
    }
    if (!(await field().count())) return "";
    await field().fill(path);
    await page.getByRole("button", { name: /Check this job/i }).first().click();
    // Reading a file, probing the printer and comparing to the project all
    // happen before there is anything to read. A fixed wait caught the spinner.
    for (let waited = 0; waited < 20000; waited += 1000) {
      const text = await page.locator("body").innerText();
      if (!/checking whether this job is ready/i.test(text)) return text;
      await page.waitForTimeout(1000);
    }
    return page.locator("body").innerText();
  };

  // The likeliest first mistake: handing Studio the project instead of the slice.
  let body = await check(samplePath);
  record("A project file handed in as a sliced job is named, not shrugged at",
    /project file, not a sliced/i.test(body), body ? "" : "no path field on the page");

  // Something that is not a job at all.
  const notAJob = join(outDir, "notes.gcode");
  writeFileSync(notAJob, "these are my notes about the print, not a program");
  body = await check(notAJob);
  record("A file that is not a sliced job says so",
    /does not look like a sliced g-code file/i.test(body), "");

  // A watched folder with nothing in it yet.
  const emptyFolder = join(outDir, "watch-empty");
  mkdirSync(emptyFolder, { recursive: true });
  const empty = await callRoute(page, "/watch_folder", { folder: emptyFolder });
  record("An empty export folder says what will happen next",
    /nothing new in that folder yet/i.test(empty.body.summary || ""),
    empty.body.summary || "");

  // Two candidates that cannot be told apart must be a question, not a pick.
  const twoFolder = join(outDir, "watch-two");
  mkdirSync(twoFolder, { recursive: true });
  const job = readFileSync(gcodePath);
  writeFileSync(join(twoFolder, "job-a.gcode"), job);
  writeFileSync(join(twoFolder, "job-b.gcode"), job);
  await page.waitForTimeout(2500);            // let both settle
  const two = await callRoute(page, "/watch_folder",
    { folder: twoFolder, project_path: samplePath });
  const seen = (two.body.candidates || []).length;
  record("Two indistinguishable jobs are a question, not a guess",
    seen === 2 && !two.body.best,
    `${seen} candidate(s), best=${two.body.best ?? "none"}`);

  await shot(page, "08-novice");
}

async function phaseUi(page) {
  // The placement finding, read from the DOM the user sees.
  const body = await page.locator("body").innerText();
  const has = (s) => body.includes(s);

  record("Placement finding rendered", has("Object placement") && has("outside the U1"),
    (body.match(/Hangs [\d.]+ mm past the \w+ edge/) || ["no overhang line"])[0]);
  record("Preflight card rendered", has("Before you slice"), "");
  record("Preflight reports an honest unknown", has("Studio can’t tell") || has("Studio can't tell"),
    "");
  record("Not-detected is never called unsupported",
    !/not supported|unsupported/i.test(body), "");
  await shot(page, "02-project-open");
}

async function phasePrepared(page) {
  const body = await page.locator("body").innerText();
  const has = (s) => body.includes(s);
  record("Prepared copy reported", has("Saved as") || has("U1 profile copy"), "");
  record("Fidelity report rendered", has("What survived preparing this copy"), "");
  record("Fidelity lists what was not carried over",
    has("What Studio could not carry over"), "");
  record("Fix ledger rendered", has("Changes Studio made"), "");
  record("Return-to-original offered", has("Return to the original"), "");
  record("Original-untouched wording present",
    has("never modified") || has("was not changed"), "");
  record("Best-tool panel rendered", has("Best tool for this project"), "");
  record("No print-success promise in the prepared view",
    !/guaranteed|will print successfully|100% success/i.test(body), "");
  await shot(page, "03-prepared");
}

const browser = await chromium.connectOverCDP(cdpUrl);
try {
  const page = await appPage(browser);
  if (phase === "startup") await phaseStartup(page);
  else if (phase === "routes") await phaseRoutes(page);
  else if (phase === "ui") await phaseUi(page);
else if (phase === "post-slice") await phasePostSlice(page);
else if (phase === "cockpit") await phaseCockpit(page);
else if (phase === "provenance") await phaseProvenance(page);
else if (phase === "novice") await phaseNovice(page);
  else if (phase === "prepared") await phasePrepared(page);
  else if (phase === "launch-file") {
    // The app was started with the project as an argument; the shell reports it
    // through get_launch_file and the session opens it at startup. The native
    // picker is deliberately not used — see run.ps1 for why it is unreachable.
    const launched = await page.evaluate(() =>
      window.__TAURI_INTERNALS__.invoke("get_launch_file"));
    record("Shell reports the launch file", typeof launched === "string",
      String(launched).split(/[\/]/).pop());
    await page.waitForTimeout(2000);
    // Assert against a surface that names the *open* file, not the dashboard's
    // recent list — a recent list can be populated by an earlier run, so it was
    // proving the wrong thing on a machine that had one.
    await page.evaluate(() => {
      window.history.pushState({}, "", "/compatibility");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
    await page.waitForTimeout(3500);
    const body = await page.locator("body").innerText();
    record("Session opened the launch file",
      body.includes("demo_u1_showcase") && /using your open 3mf/i.test(body), "");
  } else if (phase === "colours") {
    await page.evaluate(() => {
      window.history.pushState({}, "", "/colors");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
    await page.waitForTimeout(4000);
    const body = await page.locator("body").innerText();
    record("Colour plan rendered", body.includes("Colours and toolheads"), "");
    const verdictLine = body
      .split(/\r?\n/)
      .find((line) => /\d+ colours?, \d+ toolheads?/.test(line));
    record("Colour verdict stated", Boolean(verdictLine), (verdictLine || "").slice(0, 70));
    record("Toolhead count says where it came from",
      body.includes("did not read this from a printer") || body.includes("your printer reported"),
      "");
    await shot(page, "04-colours");
  } else if (phase === "painted") {
    // The flagship of this release, in the installed build: a painted project is
    // open, and the colours card has to lead with a sentence a beginner can act
    // on and keep the measurements behind it.
    await page.evaluate(() => {
      window.history.pushState({}, "", "/colors");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
    await page.waitForTimeout(4000);
    const body = await page.locator("body").innerText();
    record("Painted colour is stated in one sentence",
      /painted with \d+ filament colours?/i.test(body),
      (body.split("\n").find((l) => /painted with \d+ filament/i.test(l)) || "").slice(0, 80));
    record("The painting's measurements are available, not shown by default",
      body.includes("What Studio read from the painting"), "");
    record("No raw paint data reaches the page",
      !/paint_color="|mmu_segmentation="/.test(body), "");
    // Bring the painting itself into the frame. The screenshot from this run is
    // what the README shows, and a picture of the claim has to contain it.
    const framed = await page.evaluate(() => {
      const wanted = /painted with \d+ filament/i;
      const leaf = Array.from(document.querySelectorAll("p, span, div"))
        .find((node) => node.children.length === 0 && wanted.test(node.textContent || ""));
      const card = leaf?.closest("div.rounded-md") || leaf;
      card?.scrollIntoView({ block: "center" });
      return Boolean(card);
    });
    record("The painted sentence is on screen, not below the fold", framed, "");
    await page.waitForTimeout(800);
    await shot(page, "09-painted");
  } else if (phase === "goto-compatibility") {
    await page.evaluate(() => {
      window.history.pushState({}, "", "/compatibility");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
    await page.waitForTimeout(2500);
    console.log("navigated");
  } else if (phase === "prepare") {
    await page.getByRole("button", { name: /Prepare U1 copy/i }).first().click();
    await page.waitForTimeout(6000);
    console.log("prepared");
  } else {
    throw new Error(`unknown phase ${phase}`);
  }
} finally {
  writeFileSync(join(outDir, `results-${phase}.json`), JSON.stringify(results, null, 2));
  await browser.close();
}

if (results.some((r) => !r.ok)) process.exit(1);
