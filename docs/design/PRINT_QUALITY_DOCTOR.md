# Print Quality Doctor — Design Plan (not implemented)

> Status: **plan only.** No code yet. Troubleshooting categories below are common,
> well-known 3D-printing concepts used as a symptom taxonomy — not a reproduction
> of any article. Snapmaker is not affiliated with or endorsing this project; we
> link to official docs rather than copying text. Inspiration / further reading:
> Snapmaker, "How to Improve 3D Print Quality"
> (https://www.snapmaker.com/blog/how-to-improve-3d-print-quality/).

## 1. Feature definition

Print Quality Doctor helps a beginner diagnose a **bad result after slicing or
printing**. The user picks a plain-language symptom; Studio shows likely causes,
the safest first checks, which Snapmaker Orca settings to inspect, and
hardware/material checks — in advisory language only. It never auto-changes
settings and never edits g-code or profiles.

## 2. How it differs from the other Doctors

- **Project Doctor** — *before* printing: will this model likely print? (geometry,
  bed fit, overhangs, material estimate).
- **Compatibility Doctor** — *before slicing*: file/profile problems (foreign or
  out-of-range project settings, relative-E without G92 E0). Already implemented,
  read-only.
- **Print Quality Doctor** — *after* a bad print or bad preview: what likely
  caused this and what should I check first?
- **Printer Doctor** — live, read-only printer health signals.

Print Quality Doctor is the only one keyed off an **observed bad outcome**; the
others are pre-flight or live-health. It can *cite evidence* from Project Doctor
(model geometry) and Printer Doctor (telemetry) when available, but works
standalone from a user-picked symptom.

## 3. Symptom-to-cause matrix

Columns: symptom · likely causes · first checks (safest first) · Orca setting path
(if known) · evidence needed (Observation / Model geometry / Printer telemetry).

| Symptom | Likely causes | First checks (safe order) | Orca setting path | Evidence |
|---|---|---|---|---|
| Stringing / wisps | wet filament; retraction too low; temp too high | dry filament; lower nozzle temp a little; check retraction distance/speed | Filament → temperature; Quality → retraction | Observation (+ telemetry: nozzle temp) |
| Ringing / ghosting | high speed/accel; loose belts; vibration/resonance | reduce speed/accel & jerk; check belt tension; confirm input shaping configured | Speed → accel/jerk | Observation (+ telemetry: accel/input-shaping if exposed) |
| Layer shift | belt/pulley slip; stepper skipping; collisions; too-high accel | inspect belts/pulleys; check motor current; clear obstructions; lower accel | Speed → accel | Observation (+ telemetry/maintenance) |
| Warping | poor bed adhesion; cold bed; uneven cooling/draft; no brim | clean/level bed, set Z-offset; raise bed temp; enclosure; add brim/raft | Plate → adhesion (brim/raft); Filament → bed temp | Observation (+ telemetry: bed temp) |
| Missing / poor first layer | Z-offset too high; unlevel bed; dirty plate; flow low | re-level / adjust Z-offset; clean plate; slow first layer | Quality → first layer; Printer → Z-offset | Observation + Model (first-layer contact) |
| Blobs / zits | pressure mismatch; retraction/coasting; Z-seam; over-extrusion | calibrate flow; adjust seam alignment; tune retraction | Quality → seam; Quality → retraction | Observation |
| Under-extrusion | clog; wet/low-temp filament; extruder slipping; nozzle wear | clean nozzle; dry filament; raise temp slightly; verify flow | Filament → flow; Filament → temperature | Observation (+ telemetry: nozzle temp) |
| Rough / inconsistent surface (incl. coarse layer lines) | wet filament; temp instability; layer height too large; mechanical play | dry filament; stabilize temp; reduce layer height; check frame/belts | Quality → layer height; Filament → flow | Observation |
| Poor bridging / overhangs | insufficient cooling; too-steep overhang; speed | set part fan to 100%; reduce overhang/speed; add supports | Cooling → fan; Support | Observation + Model (overhang risk) |
| Color bleeding / waste (multi-material) | purge/flush too low; wrong filament mapping; ooze | raise flush volumes; verify slot mapping; check prime tower | Multi-material → flush; prime tower | Observation + Model (multi-material) |

Notes: paths are indicative of where to look in Snapmaker Orca, not exact strings
(they vary by version). U1 strengths worth surfacing as context (never as
auto-actions): Dynamic Flow Calibration (K-factor), Input Shaping (resonance
cancellation), CoreXY (lower moving mass), Adaptive Variable Layer Height, and
SnapSwap™ independent dual extruders — relevant to ringing, surface, and
multi-material symptoms.

## 4. Safe wording rules

- Always say **"likely"** / "common causes" — never assert the single cause.
- **Never guarantee** a fix or print success; checks reduce risk, not certainty.
- **Never auto-edit** settings, profiles, or g-code — advisory only.
- **Never tell the user to ignore a bad slice preview** — a wrong preview is a
  stop-and-fix signal.
- Order checks **safest/cheapest first** (e.g. dry filament before disassembly).
- Distinguish "check" (inspect) from "change" (only if understood).

## 5. MVP scope

- Manual symptom picker (the 10 symptoms above).
- Advisory checklist per symptom: likely causes, first checks, Orca paths,
  hardware/material checks, "what not to change blindly".
- Pure, static knowledge base (no network, no telemetry required for MVP).
- No printer control, no automatic g-code/profile changes, no settings writes.
- Optional links to the U1 compatibility checklist and official Snapmaker docs.

Later (post-MVP): pull live evidence from Printer Doctor (bed/nozzle temp, fan,
accel/input-shaping, maintenance reminders) and Project Doctor (overhang risk,
first-layer contact, tall/narrow instability, material estimate, bed fit) to rank
causes; never to auto-apply changes.

## 6. RC+1 vs later recommendation

- **RC+1 (now-ish):** ship the MVP — a static, symptom-driven advisory checklist.
  It's pure-logic, read-only, low-risk, and high beginner value, mirroring the
  Compatibility Doctor pattern already in the codebase.
- **RC+2 / later:** evidence integration (Printer Doctor telemetry + Project Doctor
  geometry) to prioritise causes per symptom.
- Do not bundle into beta.3 (already released). Target a future prerelease.

## 7. Required tests (for implementation)

Backend (or shared knowledge base):
1. Each symptom returns a non-empty causes + first-checks list.
2. Every finding uses hedged language (contains "likely"/"check"; no "guarantee").
3. No entry instructs auto-editing or ignoring a bad preview.
4. Knowledge base has no paid/commercial model names.
5. Lookup of an unknown symptom returns a safe empty/explanatory result.

Frontend:
6. Symptom picker renders all symptoms; selecting one shows its checklist.
7. "What not to change blindly" section is present per symptom.
8. Copy contains no "auto-fix"/"guaranteed" claims.
9. Orca setting paths and evidence-needed labels are visible.

## 8. Exact implementation prompt (if approved) — MVP

> SNAPMAKER STUDIO — PRINT QUALITY DOCTOR MVP (advisory, read-only)
>
> Implement the Print Quality Doctor MVP per docs/design/PRINT_QUALITY_DOCTOR.md.
> Scope: manual symptom picker + static advisory checklist. No printer control, no
> telemetry dependency, no automatic g-code/profile/setting changes, no writes.
>
> Backend: add a static knowledge base + `quality.lookup(symptom)` returning
> {symptom, likely_causes[], first_checks[], orca_paths[], hardware_checks[],
> avoid[], evidence_needed[]}. Expose `POST /quality_check {symptom}`. No network.
> Tests: every symptom non-empty; hedged language ("likely"); no "guarantee"; no
> auto-edit/ignore-preview wording; no paid model names; unknown symptom → safe.
>
> Frontend: add "Print Quality Doctor" route + sidebar entry; symptom picker;
> per-symptom checklist with likely causes, safe first checks, Orca paths,
> hardware/material checks, and a clear "what not to change blindly" section;
> hedged copy only. Pure-logic tests for the picker + copy guards.
>
> Run backend pytest + frontend vitest + tsc + build. Do not tag/release. Report
> files changed, tests, and what's deferred to the evidence-integration phase.
