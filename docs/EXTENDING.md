# Extending Snapmaker Studio

Studio is built so the useful parts are reachable without the app, and so the
most commonly-needed contribution — teaching Studio about another tool in the
ecosystem — is a data change rather than a code change.

Three seams, in order of how easy they are to use.

---

## 1. Add a tool to the ecosystem registry (no code)

`backend/snapstudio_core/data/ecosystem.json` is the list of open-source tools
Studio can recommend. Adding one is a pull request against that file.

### Schema

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable, lowercase, hyphenated. Used as the key everywhere else |
| `name` | yes | What a person calls it |
| `kind` | yes | `slicer`, `converter`, `printer-dashboard`, `browser-extension`, `utility`, `firmware` |
| `official` | no | `true` only for Snapmaker's own tools and what ships on the printer |
| `maturity` | yes | `stable` or `preview` |
| `role` | yes | One sentence, plain language, no jargon. This is shown to a beginner |
| `url` | yes | `https://` only |
| `license` | yes | SPDX identifier where possible. Shown in the UI |
| `install_hint` | yes | What the user has to do to get it |
| `caution` | when `maturity` is `preview` | Shown before the button. A test fails the build without it |
| `handoff` | no | `file` if Studio can launch it with a file, `link` otherwise. Default `link` |
| `stage` | no | `before-slicing` (default) or `after-slicing` |
| `base_score` | no | Baseline rank. Leave at 0 unless the tool is a default destination |
| `recommend_when` | yes | The rules below. May be empty, in which case the tool is never suggested |

### Rules

```json
{ "trait": "mixed_nozzle_sizes", "op": "is_true", "weight": 40,
  "reason": "This project already uses more than one nozzle size, which is exactly what this fork is built for." }
```

- `trait` — a key from `project_traits.TRAIT_KEYS`. A test rejects any rule
  keyed on a trait Studio does not measure, because such a rule would silently
  never fire.
- `op` — `is_true`, `is_false`, `equals` (with `value`), or `at_least` (with a
  numeric `value`). Deliberately small; a contributor should be able to read the
  whole vocabulary in one sitting.
- `weight` — integer. Roughly: 40+ means "this tool is the point of this file",
  10–25 means "worth mentioning", under 10 means "only if nothing else fits".
- `reason` — required, and shown verbatim to the user. Write it as an explanation
  of *this file*, not an advert for the tool.

### What qualifies

A tool belongs in the registry if it is open source or freely available, is
actively usable today, and there is a **trait Studio can actually measure** that
distinguishes when it helps. "This tool is good" is not a rule. "This project
contains texture data and this tool prints texture data" is.

A tool does **not** belong if suggesting it would require Studio to claim
something it cannot see, if it needs a paid account for its core function, or if
it would put a beginner one click away from an irreversible action on their
printer.

### Rules Studio applies to itself

- A trait Studio could not measure never fires a rule.
- A tool is "installed" only when the desktop shell found its executable.
- With nothing special detected, the answer is the official Snapmaker Orca.

---

## 2. Use the engine directly (CLI and local API)

Everything the desktop app can do is reachable without it. All output is JSON
with a `schema_version`.

```bash
u1convert traits    project.3mf              # graded facts with evidence
u1convert ecosystem project.3mf              # tool recommendation and why
u1convert ecosystem project.3mf --installed '{"snapmaker-orca":"C:/.../snapmaker-orca.exe"}'
u1convert cost      project.3mf --price-per-kg 24
u1convert placement project.3mf              # per-object placement vs the U1 plate
u1convert placement project.3mf --fix        # write a repositioned copy
u1convert inspect   project.3mf              # source, objects, plates, filaments
```

The desktop app talks to a loopback JSON service that exposes the same
operations. It binds `127.0.0.1` only, prints `{"port": N, "token": "…"}` on
stdout at startup, and requires that token on every POST:

```
POST /project_traits      {"path": "..."}
POST /ecosystem_advice    {"path": "...", "installed": {"tool-id": "path"}}
POST /project_cost        {"path": "...", "price_per_kg": 20, "prices": {"PETG": 28}}
POST /placement_check     {"path": "..."}
POST /prepare_placed      {"path": "...", "out_dir": "..."}
POST /doctor              {"path": "..."}
POST /convert             {"path": "...", "prepare_mode": "preserve"}
GET  /health
```

`backend/tests/test_api_contract.py` fails the build if a documented top-level
field disappears from a response. If you depend on a field, add it there.

---

## 3. Add analysis to the engine (code)

Engine modules live in `backend/snapstudio_core/` and are pure: they take a path
or a parsed structure and return a JSON-ready dict. Side effects — timestamps,
the library index, writing files — belong in `backend/snapstudio_api/service.py`.

### The rules a new analysis module must follow

1. **Never raise out to a caller.** The caller is a UI. Return
   `{"available": False, "reason": "..."}` with a message a person can act on.
2. **Grade what you claim.** If a value is inferred rather than read, say so.
   Reuse the tiers in `project_traits`: `confirmed`, `likely`, `informational`,
   `unknown`. An unmeasured value is `None` at `unknown`, never `False`.
3. **Carry the evidence.** Name the part of the file or the endpoint that proved
   it. A finding a user cannot check is a finding they cannot trust.
4. **Never modify the original.** Anything that changes a project writes a new
   file, reports every change with its old value, and validates the result it
   actually wrote.
5. **Refuse rather than half-do.** If a fix cannot be completed correctly, do not
   apply part of it. Say what is wrong and what the user should do instead.
6. **No print-success guarantees.** Studio is advisory. "Ready", "safe",
   "validated" and "will print" are not available words.
7. **Bound your reads.** Assume the file is hostile: cap what you decode, and
   never extract to disk.

### Where things go

| Concern | Location |
|---|---|
| Reading facts from a project | `snapstudio_core/project_traits.py` |
| Rules over those facts | a new module, plus a data file if the rules are a list |
| Reference values for the U1 | `data/profiles/`, `data/templates/` — never hard-code |
| Printer communication | `snapstudio_core/moonraker.py` (all requests go through `validate_host`) |
| HTTP route | `snapstudio_api/server.py` + a thin adapter in `service.py` |
| CLI command | `u1convert/cli.py` |
| Front-end presentation logic | `desktop/src/lib/*.ts` — keep it free of JSX so it is testable |
| Front-end component | `desktop/src/components/` |

### Tests

`pytest` in `backend/`, `npm run test` in `desktop/`. Both must pass before a
change is done.

Write tests that assert what Studio *refuses* to say, not only what it says. The
tests that matter most in this codebase are the ones named like
`test_unmeasured_traits_never_fire_a_rule`,
`test_a_brim_the_creator_chose_is_left_alone` and
`test_fix_never_modifies_the_original`. They are what keeps the product honest as
it grows.

---

## 4. Adding a printer

Nothing in the engine is U1-only by construction, but Studio has one printer
target today and the honest way to add a second is:

1. Add a profile under `data/profiles/` with its machine keys and printable area.
   Checks read the bed rectangle from the profile — see
   `plate_placement.u1_bed_rect()` — rather than hard-coding it.
2. Prefer capability detection over model names. `GET /printer/objects/list`
   already tells Studio what a Klipper machine can do; extend
   `firmware_caps.interpret()` rather than branching on a model string.
3. Add the printer's own quirks as a rule module like `orca_import.py`, with each
   rule documented by the symptom it fixes.

If you find yourself writing `if printer == "..."` inside a Doctor, that is the
signal the capability is missing from the profile or the detection layer.

---

## 5. Contributing

See [../CONTRIBUTING.md](../CONTRIBUTING.md). In short: small commits, a real
test, and no claim the code cannot prove.
