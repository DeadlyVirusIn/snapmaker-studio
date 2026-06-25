# Screenshots — beta.18 (manual capture checklist)

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

The beta.18 line cleaned up page copy (shorter subtitles, repeated disclaimers moved into
collapses). A fresh screenshot set should be captured **manually from the installed app** —
automated headless capture is not reliable in the build/CI environment, and we do not ship
faked screenshots.

## Capture these (sanitized)

Dashboard · Find Models · Source Check · Project Doctor · Compatibility Doctor ·
Scale Doctor · First Layer Doctor · Plate Color Remap · Print Quality Doctor ·
Business / Cost calculator (open the assumptions panel) · Pricing / Profit result ·
Printer Hub (disconnected is fine) · Library · Batch · Settings · Help.

## For each, confirm

- One clear page purpose, one obvious next action.
- No wall of text; no repeated read-only/advisory disclaimers on the surface.
- Warnings are specific and actionable; technical/legal detail is collapsed.
- Polished spacing/alignment.

## Redact before sharing

No private IPs, hostnames, local paths, print history, or private/copyrighted model names.
For Printer Hub, use the disconnected state or blur the IP. For Business/Doctor file states,
open a sample model (e.g. the repo's `examples/sample_cube.stl`), not a personal file.
