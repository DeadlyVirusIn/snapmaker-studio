# Studio and the open ecosystem

The U1 has an unusually open platform: Klipper and Moonraker on the machine,
Fluidd on the printer's own web interface, an official Orca fork, and a growing
set of community slicer forks, converters, dashboards and firmware builds.

The problem for someone who bought a printer last week is not that these tools
are missing. It is that **you have to already know all of them before any of them
can help you**. Nobody is going to read forty repositories to find out that the
model they downloaded has texture data a specific fork can print.

Studio's answer is to read the file and say so.

---

## 1. Best tool for this project

Studio extracts what a project actually contains, matches it against a registry of
the ecosystem, and names the tool that fits — with the reason drawn from the file.

| What Studio read | What it says |
|---|---|
| More than one nozzle diameter in the project | **FOrcaSlicer** — this project already uses more than one nozzle size, which is exactly what that fork is built for |
| Image-texture parts under `3D/Textures/` | **OrcaSlicer ImageMap** — this model carries texture data most slicers throw away and that fork can actually print |
| Already-sliced plate G-code | **U1 Print Hub** — the next step is a printer, not a slicer |
| Bambu-family settings plus the auxiliary folder, targeting another printer | **MakerWorld to Snapmaker U1** — converting in the browser next time keeps the creator's profile intact from the start |
| A project authored for another printer | **Snapmaker Orca**, after preparing a U1 copy in Studio |
| Nothing special | **Snapmaker Orca.** Studio does not manufacture novelty |

Three rules keep this from becoming a link farm:

1. **Earned from evidence.** A tool is only suggested when a trait Studio actually
   measured fires one of its rules, and the rule's own reason is shown next to it.
   A trait Studio could not measure never fires anything.
2. **Installed is a fact.** A tool is marked installed only when the desktop shell
   found its executable on disk. Everything else is a link with a download hint —
   under-claiming is the correct failure direction.
3. **Cautions are mandatory for preview tools.** A young or self-described
   experimental project carries a caution that is shown before the button, and a
   test refuses to let a `preview`-maturity entry ship without one.

Every entry declares its licence, and the UI shows it, so nobody installs an
AGPL fork unaware.

---

## 2. The registry is data, not code

`backend/snapstudio_core/data/ecosystem.json`:

```json
{
  "id": "forcaslicer",
  "name": "FOrcaSlicer",
  "kind": "slicer",
  "official": false,
  "maturity": "preview",
  "role": "A community Snapmaker Orca fork that lets each of the U1's four heads run a different nozzle size…",
  "url": "https://github.com/jiyang1018/FOrcaSlicer",
  "license": "AGPL-3.0",
  "caution": "A research-preview community fork, independent of Snapmaker…",
  "install_hint": "Download a build from the FOrcaSlicer releases page…",
  "handoff": "file",
  "recommend_when": [
    { "trait": "mixed_nozzle_sizes", "op": "is_true", "weight": 40,
      "reason": "This project already uses more than one nozzle size, which is exactly what this fork is built for." }
  ]
}
```

Adding a tool is a pull request against one JSON file. No code changes, no
rebuild of the engine's logic. The schema and the rules for what qualifies are in
[../EXTENDING.md](../EXTENDING.md).

---

## 3. Speaking the platform's own protocols

Studio uses documented interfaces and nothing else. No scraping, no reverse
engineering, no vendored code from a GPL or AGPL project.

**Moonraker (the printer).** Read-only by default: `/server/info`,
`/printer/info`, `/printer/objects/list`, `/printer/objects/query`,
`/server/files/metadata`, `/server/history/list`, `/server/job_queue/status`.
Control actions — pause, resume, cancel, start, emergency stop, upload — exist,
are POST, and are only ever reachable from an explicit user confirmation in the
UI. Nothing runs on a timer or as a side effect of monitoring.

**Capability detection, not model names.** `GET /printer/objects/list` is the
honest manifest of what a machine can do. Studio maps it to plain language:
`bed_mesh` → automatic bed mesh levelling, `exclude_object` → cancel one failed
object mid-print, `input_shaper` → resonance compensation, `extruder1..n` →
toolhead count, `filament_switch_sensor` → runout detection. It reports only what
the list proves is present.

**Two ports, because the U1 answers on two.** Discovery probes Klipper's standard
7125 *and* port 80, where the U1 serves Moonraker through its own nginx alongside
the built-in Fluidd page. Probing only one makes a reachable printer look offline.

**And when nothing answers, it says the real reason.** The U1's network interface
is gated behind a setting on the printer's own touchscreen. "Not found" is far
more often "the switch is off" than "the network is broken", so discovery returns
the fix: *turn on Advanced Mode in Settings → Maintenance, then use the IP address
shown there.*

**Snapmaker Orca (the slicer).** A one-way handoff. Studio prepares a file and
launches the verified executable with that file as a single argument. No shell, no
flags, no slicing commands, no control of Orca. This is a hard rule in the
codebase, not a current limitation.

**Stock firmware is first-class.** Extended Firmware publishes no version marker,
and its features are config-gated and default-off, so a negative probe does not
prove its absence. Studio therefore never requires it, never gates a core feature
on it, and never claims it is not installed — only that it did not detect it.

---

## 4. What Studio refuses to duplicate

Fluidd and Mainsail already own live temperature charts, the G-code console, the
file browser, bed-mesh visualisation, macro panels, print history, webcam and
timelapse. Rebuilding those would produce a worse second dashboard.

Studio's Printer Hub exists to answer one question a dashboard does not:
**is this printer, in its current state, ready for this specific project?**

Likewise: Studio does not slice, does not fork firmware, does not build a model
editor, and does not scrape model sites. The in-app model browser navigates only
an allowlist of approved domains, enforced in Rust at open time and on every
navigation, with no IPC channel exposed to the remote page.

---

## 5. Openness as a product feature, not a licence file

Everything the app can do is reachable without the app:

```bash
u1convert traits    project.3mf   # graded facts with evidence, as JSON
u1convert ecosystem project.3mf   # which tool suits this project, and why
u1convert cost      project.3mf   # material cost from the project's own slicing result
u1convert placement project.3mf   # where every object sits relative to the U1 plate
u1convert placement project.3mf --fix   # write a repositioned copy
```

The same operations are available over the local JSON API the desktop app itself
uses. Every response carries a `schema_version`, and an API contract test fails
the build if a documented field disappears.

That means another maker can build on Studio's analysis — a Home Assistant
integration, a CI check for a model repository, a batch pre-flight over a folder —
without touching the UI, and without Studio needing to anticipate them.

---

## 6. Where this goes

The registry currently names nine tools. It gets more useful as the ecosystem
grows, and every project named in it has a reason to care that Studio exists.
That is the intended shape: **a project whose value increases when its neighbours
succeed.**
