# Snapmaker Studio — project guidance

Snapmaker Studio is the local-first **pre-print intelligence layer** for the Snapmaker U1.
Independent open-source project — not affiliated with or endorsed by Snapmaker.

## What it is

Reads a 3D model's real geometry, runs read-only "Doctors" that explain likely print risks
in plain language, prepares a U1 profile copy (review in Orca before slicing) without
modifying the original, hands that copy to Snapmaker Orca to slice, and monitors / sends
to the U1 via Printer Hub.

## Hard rules (do not break these in code, copy, or docs)

- **Studio does not slice** — Snapmaker Orca does. One-way handoff only.
- **Studio never takes autonomous control.** Printer Hub provides local, user-confirmed
  actions (monitor, send, pause, resume, cancel); it never auto-starts a print.
- **Local-first.** No cloud, no account, nothing uploaded.
- **Originals are never modified** — preparing a model always writes a new copy.
- **Advisory, not guarantees.** Never claim "100% print success" or a guaranteed print.
- **No secrets** in the repo (tokens, keys, credentials). **No private data** (real IPs,
  hostnames, local paths, usernames, or private/copyrighted model names) in tracked files
  or screenshots — anonymize proof data.
- **Release safety: never force-kill `snapmaker-orca`, printer, slicer, or user GUI
  processes without explicit approval from the maintainer.** Only terminate processes you
  started yourself (track the PID); check a process's start time / owner before
  touching anything else.

## Three-bucket rule for any task

Before handing work back to the maintainer, classify it. "I don't have a tool for
this" is a tool-discovery task, not a human task.

**A — autonomous.** The capability exists. Do it. Code, tests, builds, git, docs,
screenshots, research, releases, API calls, installers, CLI runs.

**B — tool acquisition.** Software could probably do it. Find the tool: project
skills, MCP servers, installed applications, package managers, GitHub, the web.
Evaluate it for safety and licence, install it, verify it on something harmless,
then do the task. Examples that are bucket B, not C: GUI automation, screen
recording, installing and testing an installer, driving the app, querying
repository metrics, publishing a release.

**C — a true human gate.** Only: payment, accepting legal terms, identity
verification, credentials that do not exist, physical access to hardware, or a
judgement reserved for the maintainer. **Do everything up to the gate first** —
research the options, prepare the scripts, write the policy page, validate the
surrounding flow — and hand back only the irreducible action.

What this looks like in practice, from the 2026-08-23 sprint: the installed-build
acceptance checks became `tools/acceptance/run.ps1` (21 checks, WebView2 remote
debugging); the demo became `tools/demo/record.ps1` (FFmpeg + CDP); the "needs a
real printer" item became a read-only LAN session that found a real bug. See
`docs/internal/AUTOMATION_CAPABILITY_AUDIT.md`.

The safety rules are unchanged and absolute: never start a print, heat or move
hardware, flash firmware, modify an original file, force-kill a process this
session did not start, purchase anything, or accept terms on the maintainer's
behalf. Those constrain *what* is automated, never *whether* to try.

## Positioning & priorities

Positioning: **"The Intelligence Layer for Open 3D Printing."**
Priorities: Project Doctor, Printer Doctor, Cost Doctor, beginner clarity, judge-ready polish.
UI work must be verified with real screenshots (anonymized per hard rules) — never claim UI works unseen.

## Commands (verified against manifests 2026-07-05)

```bash
# desktop/ (Tauri 2 + React 18 + Vite 5 + TS)
npm run dev              # vite dev server
npm run build            # tsc && vite build
npm run test             # vitest run
npm run build:sidecar    # pwsh ./scripts/build-sidecar.ps1
npm run release:windows  # build:sidecar && tauri build

# backend/ (Python >=3.13, pytest, CLI: u1convert)
pytest                   # testpaths: tests
```

Run `npm run test` (desktop) and `pytest` (backend) before declaring any change done.

## Layout

- `desktop/` — Tauri + React app (UI, Printer Hub, Doctors).
- `backend/` — Python engine + local service (`snapstudio_core`, `snapstudio_api`).
- `docs/` — public docs, judge/submission package, verification records.

Current release: see the GitHub Releases page (latest is the submitted beta).
