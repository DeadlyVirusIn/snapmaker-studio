# Screenshots Checklist (beta.13 — Model Browser UX)

Captured from the live beta.13 UI. Everything is local; nothing is uploaded.

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

## New in beta.13

- [x] **Find Models with the trusted Model Browser control panel** — "Model Browser
  is open — browsing <site>", Open downloaded file, Run Project Doctor, Close, and
  reopen any approved site, all in Studio's own UI. ![Model Browser controls](screenshots/beta13/model-browser-controls-beta13.png)

## Carried over (visuals unchanged apart from the version footer)

The Open-in-Snapmaker-Orca handoff, Project Doctor result, Scale Options Ladder,
Print Quality Doctor, and Plate Color Remap are captured in
[SCREENSHOTS_BETA11.md](SCREENSHOTS_BETA11.md).

## The remote approved-site window itself

The site loads in a separate, **locked Studio-owned window** (no IPC, allowlist
enforced). To capture it manually: open Find Models in the installed app, click an
approved site, and use the OS window screenshot on the "Snapmaker Studio — Model
Browser" window.
The control-panel screenshot above is the canonical capture of the workflow.

See also: [JUDGE_OVERVIEW.md](JUDGE_OVERVIEW.md), [WHAT_TO_TEST_FIRST.md](WHAT_TO_TEST_FIRST.md).
