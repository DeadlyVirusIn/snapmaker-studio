# Printer Hub — Feasibility Report (design only, no implementation)

**Date:** 2026-06-18 · **Status:** research/design only — no printer code written.

## Context
Snapmaker open-sourced the U1 firmware as **standard forks** of Klipper / Moonraker /
Fluidd:
- Klipper — https://github.com/Snapmaker/u1-klipper
- Moonraker — https://github.com/Snapmaker/u1-moonraker
- Fluidd — https://github.com/Snapmaker/u1-fluidd
- Blog — https://www.snapmaker.com/blog/snapmaker-u1-firmware-now-on-github/

The modifications (~20% Klipper, ~15% Moonraker) are **Snapmaker Cloud + MQTT
bridging** — *not* changes to the local HTTP API.

## Headline
The U1 runs **stock Moonraker on port 7125, listening on all interfaces, with the
entire LAN marked trusted (no API key needed)**, advertising mDNS hostname **`U1`**.
A **local-first Printer Hub is highly feasible and largely de-risked.**

## Evidence (from the repos / live config)
- **u1-moonraker**: standard Moonraker tree (`moonraker/`, `docs/`, readthedocs) +
  a `lava/` overlay. Stock README → the full standard REST/WebSocket API is present.
- **`lava/moonraker.conf`** (the live U1 config):
  - `host: all`, **`port: 7125`** (stock).
  - **`trusted_clients`** = private LAN ranges (`10/8`, `172.16/12`, `192.0/8`,
    `127/8`, `169.254/16`, IPv6 link-local) → **any same-LAN client is trusted; no
    auth/token required for local apps.**
  - `cors_domains` = `*.lan *.local localhost mainsail/fluidd` → browser CORS is
    limited, but a **server-side client (our sidecar) bypasses CORS entirely.**
  - `[snapmakercloud]` + MQTT `localhost:1883` → the Snapmaker additions are the
    cloud bridge; the **local API is untouched.**
  - **mDNS hostname `U1`** → discoverable as `U1.local`.
- **u1-klipper**: stock Klipper; firmware burns **4 extruders `head0`–`head3`** →
  the U1 is a **4-toolhead multi-material** machine (the "4 colors" = 4 physical
  toolheads). Klipper exposes per-toolhead objects.
- **u1-fluidd**: stock Fluidd (a standard Moonraker client) → confirms the standard
  Moonraker API is live on the LAN.

## Capability feasibility (all via standard Moonraker)
| # | Capability | Endpoint(s) | Verdict |
|---|---|---|---|
| 1 | Local U1 discovery | mDNS `U1.local` / `_moonraker._tcp`; or scan `:7125` + `GET /server/info` | High |
| 2 | Moonraker connection | `GET /server/info`, `/printer/info`; LAN-trusted (no key) | High |
| 3 | File upload | `POST /server/files/upload` (multipart → gcodes) | High *(gcode)* |
| 4 | Send a prepared print | `POST /printer/print/start?filename=` (+ pause/resume/cancel) | Needs **sliced gcode** (see gap) |
| 5 | Printer status | `/printer/objects/query?print_stats&idle_timeout`; WS `printer.objects.subscribe` | High |
| 6 | Print queue / job status | `/server/job_queue/*`; `print_stats`, `virtual_sdcard` (progress) | High |
| 7 | Error / diagnostics | `print_stats.state=error`, `webhooks`, `/server/gcode_store`, `notify_gcode_response` (WS) | High |
| 8 | Material / toolhead awareness | `/printer/objects/query` per `extruder`/`extruder1..3`, `toolhead`, filament sensors | High (4 toolheads) |
| 9 | Future Printer Hub | `PrinterAdapter` interface; Moonraker first, Bambu/Prusa later | Strong |

## The one real gap — slicing
Klipper prints **gcode**; Studio produces a **U1 *project* (3MF)**. So "send a
prepared print" end to end needs a slice step Studio doesn't own. Options: (a) Studio
prepares the project → user slices in Snapmaker Orca → Studio uploads the gcode +
starts (low effort, honest); (b) integrate/embed a slicer (large). **Monitor +
control + upload-already-sliced needs no slicing.**

## Risks / unknowns
- No published API docs for the Snapmaker layer; standard Moonraker API assumed
  (well-founded — Fluidd ships and the conf is stock). Verify on real hardware.
- Exact Klipper object names for the 4 toolheads / filament sensors — confirm on a U1.
- Firmware-version drift / cloud-mode (MQTT) interactions with local control.
- Slicing dependency (above) for the full one-click loop.
- Findings are from the repos/config, not a probed physical U1.

## MVP architecture — "Send to U1"
- **Sidecar** `snapstudio_core/printers/`: `MoonrakerClient` (REST `:7125` + WS)
  behind a generic `PrinterAdapter`. All printer traffic server-side (no browser
  CORS). No auth needed on-LAN.
- **Discovery:** mDNS `U1.local` + `_moonraker._tcp`, plus manual IP and a `:7125`
  subnet probe.
- **Endpoints:** `/server/info`, `/printer/objects/query|subscribe`,
  `/server/files/upload`, `/printer/print/start|pause|cancel`, `/server/job_queue/*`.
- **Desktop:** a "Printers" tab — discover/add U1 → live status + per-toolhead
  telemetry → upload + start (gcode) → job/queue/diagnostics.
- **Phasing:** A) Monitor (discover + live status/telemetry/job — zero slicing) →
  B) Control + upload (start/pause/cancel a gcode) → C) Slice-and-send (Orca handoff
  or embedded slicer).

## Recommended next step (no product code)
A **read-only spike** against a real U1 (or stock Moonraker): discover `U1.local:7125`,
`GET /server/info` + `/printer/info`, `/printer/objects/query` for the 4 toolheads +
`print_stats`, WS-subscribe to live status. Deliver: confirmed endpoints, real
toolhead/object names, LAN-no-auth confirmation. ~1 week; de-risks the whole Hub
before any product integration.

> Design only — nothing here is implemented. See `../ROADMAP.md` (v0.5/v0.6) for how
> this phases into the product.
