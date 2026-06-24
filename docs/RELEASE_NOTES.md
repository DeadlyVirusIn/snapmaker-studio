# Snapmaker Studio v0.4.0-beta.13 — Studio Model Browser

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

**The Model Browser opens approved model sites in a locked, Studio-owned browser
window — no Chrome/Edge — with trusted Studio controls to open the downloaded file
and run Project Doctor.**

## Honest note: why a Studio-owned window (not a same-page embed)
The original goal was a browser embedded directly in the main Studio page. On the
current Tauri/Wry/WebView2 stack that same-window path is **not viable**: creating a
child webview with `window.add_child(...)` — and, in fact, building any webview from a
command — **deadlocks**. The webview is created but its navigation never fires and the
command never returns (diagnosed with runtime instrumentation plus the DevTools
Protocol). The stable beta.13 path therefore uses a **Studio-owned, allowlist-locked
browser window**, created once at startup and navigated on demand. It is **not** a
same-window embedded viewport, and this release does not claim to be one.

## The headline: a Studio Model Browser with a trusted control center
Beginners stay in Studio's own UI. Click an approved site on **Find Models** and it
opens in the locked, isolated **Snapmaker Studio — Model Browser** window. A **trusted
control center** appears in Find Models — it lives in Studio's own UI, never inside the
third-party page — with everything you need:

- **"Model Browser is open — browsing <site>"** status.
- **Bring browser to front** (reliable raise).
- **Reopen the selected site** / **choose another approved site** (Printables,
  Thingiverse, MyMiniFactory, Cults3D, Thangs, MakerWorld).
- **Close Model Browser.**
- **Open downloaded file** → goes straight to Project Doctor.
- **Run Project Doctor.**
- Plain flow copy: *Browse in the Studio Model Browser. Download the STL/3MF from the
  site. Then open it here and run Project Doctor.*

The full beginner flow with no external browser: browse the approved site in
Studio → download from the site → **Open downloaded file** → Project Doctor →
prepare a validated U1 copy → **Open in Snapmaker Orca**.

## Why it's safe (security model unchanged)
- The remote approved-site page stays in an **isolated Tauri window with no IPC
  and no app capabilities** — it cannot call any Studio command.
- All controls live in **trusted Studio UI**; the Rust commands
  (`open_model_browser`, `close_model_browser`, `is_model_browser_open`,
  `focus_model_browser`) act on the window **by label**, never by talking to the
  remote page. Closing only **hides** the window (kept for reuse); the OS close
  button hides it too.
- **Allowlist enforced** (Printables, Thingiverse, MyMiniFactory, Cults3D, Thangs,
  MakerWorld); off-allowlist navigation is blocked.
- **No scraping, no DOM automation, no login/paywall bypass, no silent download
  interception, no auto-import, no API keys.** Downloads are manual, from the site.

## Carried forward (beta.12 completion)
Plate Color Remap clarity (no dead "no base colors" state), Print Quality
bed-adhesion + support-failure paths, clearer known-good comparison, the desktop
Content-Security-Policy, and one-click **Open in Snapmaker Orca**.

## Notes
- Back / Forward / Reload are intentionally **not** shown: they can't safely drive
  the isolated remote webview without granting it a command channel, so rather than
  fake them, the panel offers Close + Reopen instead.
- This is an **unsigned Windows beta** — SmartScreen may show "Unknown publisher."
  Verify the SHA256 before installing. Code signing remains planned.

## Download (unsigned beta)
Only download from the official GitHub release, and verify the checksum.

```
File:    Snapmaker.Studio_0.4.0-beta.13_x64-setup.exe
Size:    16,087,966 bytes
SHA256:  884005e020ff74d7ba3d32e9574180ac80db0ec030f3f5ca7cb4d4b1267bad4f
```

Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.13/docs/windows-install.md).

_Beta — local-first; nothing leaves your computer._
