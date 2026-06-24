// Runtime probe for the embedded Model Browser (beta-13 diagnosis).
//
// Requires the app launched with WebView2 remote debugging on port 9222:
//   set WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9222
//   npm run tauri dev
//
// It drives the MAIN Studio webview via CDP to navigate to Find Models and click
// "Printables", then looks for the child "model-embed" webview as a SEPARATE CDP
// target and screenshots its actually-painted page (this bypasses the PrintWindow
// native-layer blindspot). Zero dependencies — Node 18+ built-in fetch + WebSocket.
//
// Output: ./scripts/embed-proof.png + a verdict on stdout. Read-only on the app.

import { writeFileSync } from "node:fs";

const PORT = process.env.EMBED_PROBE_PORT || "9222";
const BASE = `http://127.0.0.1:${PORT}`;
const APPROVED = ["printables.com", "thingiverse.com", "myminifactory.com", "cults3d.com", "thangs.com", "makerworld.com"];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function list() {
  const res = await fetch(`${BASE}/json/list`);
  return res.json();
}

// Minimal CDP-over-WebSocket client.
function cdp(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    let id = 0;
    const pending = new Map();
    ws.addEventListener("message", (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id != null && pending.has(msg.id)) {
        const { ok, err } = pending.get(msg.id);
        pending.delete(msg.id);
        msg.error ? err(new Error(JSON.stringify(msg.error))) : ok(msg.result);
      }
    });
    ws.addEventListener("error", (e) => reject(e));
    ws.addEventListener("open", () =>
      resolve({
        send(method, params = {}) {
          return new Promise((ok, err) => {
            const myId = ++id;
            pending.set(myId, { ok, err });
            ws.send(JSON.stringify({ id: myId, method, params }));
          });
        },
        close: () => ws.close(),
      })
    );
  });
}

async function waitForPort(timeoutMs = 60000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try { await fetch(`${BASE}/json/version`); return true; } catch {}
    await sleep(1000);
  }
  return false;
}

const hostOf = (u) => { try { return new URL(u).host.toLowerCase(); } catch { return ""; } };
const isApproved = (u) => { const h = hostOf(u); return APPROVED.some((d) => h === d || h.endsWith(`.${d}`)); };

async function main() {
  console.log(`[probe] waiting for CDP on ${BASE} ...`);
  if (!(await waitForPort())) { console.error("[probe] FAIL: CDP port never came up. Was WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS set?"); process.exit(2); }

  let targets = await list();
  console.log("[probe] initial targets:");
  for (const t of targets) console.log(`  - type=${t.type} title=${JSON.stringify(t.title)} url=${t.url}`);

  // Pick the Studio main UI (vite dev server or tauri scheme; never an approved model host yet).
  const main = targets.find((t) => t.type === "page" && !isApproved(t.url) && (t.url.includes("localhost") || t.url.startsWith("tauri://") || t.url.startsWith("http")));
  if (!main) { console.error("[probe] FAIL: could not find main Studio webview target."); process.exit(3); }
  console.log(`[probe] main target: ${main.url}`);

  const c = await cdp(main.webSocketDebuggerUrl);
  await c.send("Runtime.enable");

  const evalJs = (expression) => c.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });

  // 1) Go to Find Models.
  await evalJs(`(() => {
    const hit = [...document.querySelectorAll('a,button')].find(e => (e.textContent||'').trim().toLowerCase().includes('find models'));
    if (hit) { hit.click(); return 'clicked-nav'; }
    return 'nav-not-found';
  })()`).then((r) => console.log("[probe] nav:", r.result.value));
  await sleep(1200);

  // 2) Click the Printables browse button.
  const clicked = await evalJs(`(() => {
    const hit = [...document.querySelectorAll('a,button')].find(e => (e.textContent||'').trim().toLowerCase().includes('printables'));
    if (hit) { hit.click(); return 'clicked-printables'; }
    return 'printables-not-found:' + document.body.innerText.slice(0,120);
  })()`);
  console.log("[probe] browse:", clicked.result.value);

  // 3) Wait for the child model-embed webview to appear + load an approved host.
  let child = null;
  for (let i = 0; i < 25; i++) {
    await sleep(800);
    targets = await list();
    child = targets.find((t) => isApproved(t.url));
    if (child) break;
  }

  if (!child) {
    console.log("[probe] targets after click:");
    for (const t of targets) console.log(`  - type=${t.type} title=${JSON.stringify(t.title)} url=${t.url}`);
    console.error("[probe] VERDICT: NO child webview on an approved host appeared. Embedded site did NOT load.");
    c.close();
    process.exit(4);
  }

  console.log(`[probe] CHILD FOUND: type=${child.type} title=${JSON.stringify(child.title)} url=${child.url}`);

  // 4) Screenshot the child's actually-painted page (bypasses PrintWindow blindspot).
  const cc = await cdp(child.webSocketDebuggerUrl);
  await cc.send("Page.enable");
  await sleep(1500);
  const shot = await cc.send("Page.captureScreenshot", { format: "png" });
  const out = new URL("./embed-proof.png", import.meta.url);
  writeFileSync(out, Buffer.from(shot.data, "base64"));
  console.log(`[probe] SAVED proof screenshot: ${out.pathname}`);
  console.log(`[probe] VERDICT: PASS — embedded webview loaded ${hostOf(child.url)} inside Studio.`);
  cc.close();
  c.close();
}

main().catch((e) => { console.error("[probe] ERROR:", e); process.exit(1); });
