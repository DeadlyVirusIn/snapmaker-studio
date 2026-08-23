// Read-only verification of the *installed* Snapmaker Studio against a real
// Snapmaker U1, driven over the Chrome DevTools Protocol.
//
// Why this exists: everything Studio says about a printer was, until beta.24,
// verified only against tests the project wrote itself. The first session against
// a real machine found a genuine bug — the U1 reports loaded filament as parallel
// arrays, and Studio was looking for a list of objects, so it told owners their
// printer does not report loaded filament while the printer was reporting all
// four spools. This script proves the shipped installer reads that firmware
// correctly, and that the honest unknowns are still honest.
//
// SAFETY. This script is read-only by construction:
//  * Only the routes in READ_ONLY_ROUTES are ever called, and the list is
//    asserted against a deny-list of every control route the engine exposes.
//  * Nothing is uploaded, nothing is queued, no temperature, motion, homing,
//    pause, resume, cancel, start, emergency stop or configuration call is made.
//
// PRIVACY. The printer's address never reaches the evidence file: it is replaced
// with a placeholder before anything is written to disk.
//
// Usage: node checks.mjs <cdpUrl> <outDir> <printerHost> <samplePath>

import { chromium } from "playwright-core";
import { writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const [, , cdpUrl, outDir, printerHost, samplePath] = process.argv;
mkdirSync(outDir, { recursive: true });

const READ_ONLY_ROUTES = [
  "/printer/status",
  "/printer/capabilities",
  "/printer/firmware",
  "/preflight",
];

// Anything that could change the machine's state. Asserted, not assumed.
const FORBIDDEN = [
  "control", "start", "pause", "resume", "cancel", "emergency",
  "upload", "queue", "gcode", "config", "firmware_update", "restart",
];
for (const route of READ_ONLY_ROUTES) {
  const tail = route.split("/").pop();
  if (FORBIDDEN.some((f) => tail.includes(f) && tail !== "firmware")) {
    throw new Error(`refusing to run: ${route} is not read-only`);
  }
}

const results = [];
const record = (name, ok, detail = "") => {
  results.push({ name, ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? `  — ${detail}` : ""}`);
};

/** Replace the printer's address wherever it appears, at any depth. */
const anonymise = (value) =>
  JSON.parse(JSON.stringify(value).split(printerHost).join("<printer-on-lan>"));

async function appPage(browser) {
  const ctx = browser.contexts()[0];
  for (const page of ctx.pages()) {
    if (page.url().startsWith("http://tauri.localhost")) return page;
  }
  throw new Error("the app window was not found over CDP");
}

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

const browser = await chromium.connectOverCDP(cdpUrl);
const page = await appPage(browser);
const evidence = {};

// --- the printer answers -----------------------------------------------------

const status = await callRoute(page, "/printer/status", { host: printerHost, port: 7125 });
evidence.status = anonymise(status.body);
const reachable = status.status === 200 && !status.body?.error;
record("Printer discovered and answering", reachable,
  `print state: ${status.body?.print_state ?? "unknown"}`);

const caps = await callRoute(page, "/printer/capabilities", { host: printerHost, port: 7125 });
evidence.capabilities = anonymise(caps.body);
const objects = caps.body?.klipper_objects ?? [];
record("Firmware object list enumerated", objects.length > 50, `${objects.length} objects`);

const bed = caps.body?.bed_mm ?? {};
record("Printer reports its own bed size",
  Number(bed.x) > 100 && Number(bed.y) > 100 && Number(bed.z) > 100,
  `${bed.x} × ${bed.y} × ${bed.z} mm`);
record("Printer reports its toolhead count", caps.body?.toolhead_count === 4,
  `${caps.body?.toolhead_count} toolheads`);

// --- the bug this release fixes ---------------------------------------------
//
// Stock U1 firmware publishes loaded filament as parallel arrays. Studio was
// looking for a list of objects, found nothing, and told the owner the printer
// does not report loaded filament. This is the shipped code path reading a real
// machine.

const pre = await callRoute(page, "/preflight",
  { path: samplePath, host: printerHost, port: 7125 });
evidence.preflight = anonymise(pre.body);
record("Preflight ran against the real machine", pre.status === 200 && !pre.body?.error);

const loaded = pre.body?.printer?.loaded_filaments ?? [];
record("Loaded filament read from the real firmware", loaded.length === 4,
  loaded.map((f) => `${f.color ?? "?"} ${f.material ?? "?"}`).join(", ") || "none");
record("Each loaded slot carries a material and a colour",
  loaded.length > 0 && loaded.every((f) =>
    typeof f.material === "string" && f.material.length > 0 &&
    typeof f.color === "string" && /^#[0-9a-f]{6}$/i.test(f.color)));

// --- the honest unknowns still hold ------------------------------------------

const rows = pre.body?.checks ?? [];
const text = JSON.stringify(rows).toLowerCase();

const nozzle = rows.find((r) => r.id === "nozzle.match");
record("Fitted nozzle is reported as unknown, not unsupported",
  nozzle?.result === "unknown"
    && !JSON.stringify(nozzle).toLowerCase().includes("unsupported"),
  nozzle?.title ?? "no nozzle check");

record("Nothing undetected is called unsupported", !text.includes("unsupported"));

const bedCheck = rows.find((r) => r.id === "bed.fit");
record("The printer's own bed size was used in the bed check",
  Boolean(bedCheck) && bedCheck.evidence.includes(String(bed.x)),
  bedCheck?.evidence ?? "");

const toolheads = rows.find((r) => r.id === "materials.toolheads");
record("Project materials compared against the machine's toolheads",
  Boolean(toolheads) && toolheads.confidence === "confirmed",
  toolheads?.evidence ?? "");

const materials = rows.find((r) => r.id === "materials.loaded");
record("Project materials compared against what is actually loaded",
  Boolean(materials) && materials.evidence.includes("4 loaded"),
  materials?.evidence ?? "");

const reachable2 = rows.find((r) => r.id === "printer.reachable");
record("Preflight recorded the printer as found", reachable2?.result === "ok");

// --- report -------------------------------------------------------------------

const passed = results.filter((r) => r.ok).length;
writeFileSync(join(outDir, "hardware.json"), JSON.stringify({
  schema_version: "hardware/1",
  printer: "<printer-on-lan>",
  read_only_routes: READ_ONLY_ROUTES,
  checks: results,
  passed,
  total: results.length,
  evidence,
}, null, 2));
await page.screenshot({ path: join(outDir, "hardware.png") });

console.log(`\n${passed}/${results.length} hardware checks passed`);
await browser.close();
process.exit(passed === results.length ? 0 : 1);
