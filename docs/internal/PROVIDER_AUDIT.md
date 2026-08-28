# Material provider reality audit — the result

Run 2026-08-25 on `main`, after v0.7.2 and after the second-printer work.
**No release was made.**

## The question

Not "how should Studio support material providers" — that was built. The narrower
one:

> Does the provider capability that already exists actually work end-to-end for a
> normal desktop user, and does it affect the final send decision correctly?

## Answer in one line

The engine worked. Nothing shipped could reach it, the semantics were wrong in two
ways that could refuse a send, the address field was arbitrary internet egress,
and three of its behaviours against a real Spoolman were not Spoolman's.

## Phase 0 — what actually shipped

Traced by following call paths, not by reading module names.

| Piece | State |
|---|---|
| Provider implementation (`material_providers.py`) | **SHIPPED**, thorough, 29 adversarial tests |
| Service layer (`_with_providers`, three callers) | **SHIPPED BUT INTERNAL ONLY** |
| HTTP surface (`spoolman` + `slot_map` on `/material_plan`, `/send_check`, `/printer/upload_gcode`) | **SHIPPED BUT INTERNAL ONLY** |
| `slot_base` at the HTTP surface | **MISSING** — the engine accepted it, no route could send it |
| Desktop API client | **MISSING** — `materialPlan` and `sendCheck` had no provider parameter at all |
| Settings / configuration UI | **MISSING** |
| Slot mapping UI | **MISSING** |
| Configuration persistence | **MISSING** |
| Freshness handling | **PARTIAL** — a timestamp was pasted into a sentence and never used in a decision |
| Conflict presentation | **SHIPPED** and correct |
| Support-bundle handling | **SHIPPED** — no provider section, whole bundle redacted |
| Restart persistence | **MISSING** (nothing to persist) |
| Frozen sidecar contains it | **SHIPPED** — the code was frozen in; no caller existed |

So the honest classification: **the capability was real and unreachable.** Zero
users of v0.7.2 could configure a provider, which is also why none of the defects
below affected a shipped user.

## Phase 3 — real Spoolman, and what it contradicted

A Spoolman 0.26.1 was run locally in Docker (session-owned, removed afterwards)
and seeded through its own REST API with eight controlled cases: enough, clearly
short, no weight, derived weight, stale weight, archived, wrong material, and a
mapping pointing at a spool that does not exist.

Three behaviours every mocked test agreed with turned out not to be Spoolman's:

1. **Archived spools are invisible.** `GET /api/v1/spool` omits them unless
   `allow_archived=true`. Studio's careful archived-spool handling had never seen
   one, and a slot mapped to an archived spool reported "no spool with id N",
   which reads as deleted.
2. **A remaining weight is always present**, computed from the spool's declared
   size minus what has been recorded used. Its presence proved nothing, and Studio
   labelled every figure `tracked` — the label a blocker is built on — including a
   spool registered a minute ago that reports a full kilogram.
3. **There is no `updated` field.** Studio read `last_used or updated`. `updated`
   does not exist; `registered` is creation time, not when the weight was true;
   and `last_used` is absent until something has printed. So **no date is the
   common case**, and it was the case the old code handled least.

The captured response is kept at
`backend/tests/fixtures/providers/spoolman_0_26_1.json` with its own provenance
block, so the findings stay pinned without Docker.

## Phase 4 — sufficiency semantics

Two rules disagreed with the project's own stated policy, and both could **refuse
a send**:

| Evidence | Was | Now |
|---|---|---|
| Tracked, fresh, clearly short | blocker | blocker (unchanged) |
| Tracked, fresh, enough | enough | enough (unchanged) |
| **Tracked but stale** | **blocker** | warning, with how old |
| **Derived** | **blocker** | warning, saying it is arithmetic |
| No timestamp | blocker | warning |
| Unknown / no provider | unknown | unknown (unchanged) |
| Provider unreachable | unknown | unknown (unchanged) |
| Negative / impossible quantity | unknown + note | unchanged |

Freshness became its own module with a **documented threshold and a stated
consequence**: past a week a figure may warn and may never be the sole reason a
send is refused. Missing, malformed and future-dated timestamps are `unknown` or
`unusable`, never fresh. A few minutes of clock skew between two machines on one
network is not a broken date.

The U1 behaviour that matters was preserved and is tested: a tracked, recent
shortfall still blocks.

## Phase 5 — printer against provider

Unchanged and correct, now covered explicitly: the printer stays authoritative
about what is physically loaded; the disagreement is shown rather than resolved;
the provider's remaining weight survives a material disagreement, because "which
material" and "how much is left" are two claims and only one of them was contested.

## Phase 6 — the multi-printer payoff

Slots now record **who saw them**. A printer reporting its own filament has
looked; a provider mapping is the user's note. On a machine reporting no filament
state — the VORON profile, and most Klipper printers — a provider is the only
source, and Studio says:

> …that is your mapping rather than something the machine has confirmed.

Provider bookkeeping is still used, because a spool you said has 43 g on it is a
real reason to expect an 87 g job to run out. It is simply never promoted to a
hardware observation. This was also a latent bug: `confirmed_by` was set only on
the compared path, so it was absent on every unused, empty and unknown slot.

## Phase 7 — U1Hub, re-audited rather than assumed

`dlgambill/u1hub` `main` was read on 2026-08-25 (MIT, last pushed 2026-08-17).

**A deliberate external API: NO.** `GET /api/spools` and `GET /api/slots` do
exist in `rfid.js` — close to what the proposal asked for, and worth saying. But
they carry no schema or version, spread internal state straight into the response,
are undocumented for external use, sit behind the same password gate as every
page, and are described in the code in terms of "the UI" they serve. An Express
route a project's own frontend calls is not a promise to anyone else.

**And decisively, U1Hub tracks no remaining weight.** Its registry is an RFID/QR
*identity* store — brand, material, colour. The words `remaining`, `weight` and
`grams` do not appear in that module. The three fields the proposal named as
carrying the value have nothing to map to, so even a blessed versioned API would
not answer the question.

**Decision: deliberately NOT integrated.** The proposal stays open, updated with
the date and evidence. No internal file of U1Hub's has ever been read.

## Phase 11 — security and privacy

A provider address went straight to `urllib.request.urlopen`. Demonstrated against
that code, not imagined:

- `file:///…` opened a local path;
- `ftp://…` opened an FTP connection;
- `http://example.com` resolved and fetched a page from the public internet,
  returning a 404 — the request genuinely left the machine.

That is a direct contradiction of Studio's first hard rule. Addresses are now
validated to http/https on the user's own network — loopback, RFC1918,
link-local, CGNAT/tailnet, and `.local`-style names — with credentials, paths,
queries and fragments refused, **before anything is opened**. 39 tests cover it.

Not reachable from the shipped app, because nothing sent an address. It was about
to become reachable, which is why the check landed before the settings page.

Privacy: the provider address is not echoed into any result, the diagnostics
bundle has no provider section and is redacted whole, and the connection-test
response deliberately omits the address because it is rendered on screen and can
end up in a screenshot.

## Phase 12 — installed-build acceptance

Run against a **locally built** v0.7.2 installer from `main` — not the published
asset — driving the frozen sidecar over CDP.

**31/31 passed**, including the in-place upgrade from v0.7.1, and including five
new provider checks: the route exists in the frozen build; an empty address is
refused; a public address is refused with the local-network reason; a `file://`
address is refused; an unreachable provider answers rather than crashing; with no
provider every sufficiency verdict is `unknown`; and — with a live Spoolman — a
real spool mapped to the slot the job actually uses comes back with a remaining
weight, `confirmed_by: provider` and `printer_confirmed: false`.

The first run was **26/27**: the live-provider check mapped a spool into slot 1
when the sample job prints from slot 2. That was the assertion being wrong, and it
surfaced the `confirmed_by` gap above — which is what an installed-build check is
for.

## Phase 14 — real U1

**NOT re-run.** `U1.local` and `snapmaker-u1.local` do not resolve on this network
— checked again this session, `getaddrinfo failed` on both — and Studio does not
scan the LAN. `tools/hardware/verify.ps1` needs `-PrinterHost <ip>`, which is not
in tracked files and must not be.

**`main` is therefore not hardware verified.** It now changes Moonraker, printer
profiles, preflight, post-slice, send-check and material planning. v0.7.2's 26/26
is evidence about v0.7.2 and must not be cited for `main`. Before any future
release, the harness has to be re-run with the printer powered on and its address
supplied. This is recorded at the top of `docs/TRUST_STATUS.md`.

## Tests

| | Before | After |
|---|---|---|
| Backend | 1326 collected / 1326 passed | **1342 passed / 4 skipped** |
| Desktop | 311 | **321** |
| selfcheck | 27/27 | **27/27** |
| Installed acceptance | not run this sprint | **31/31** (locally built installer) |
| Real U1 | 26/26 against v0.7.2 | **not re-run** |

New: `test_provider_reality.py` (9), `test_provider_address_safety.py` (39),
`test_freshness.py` (29), `test_provider_printer_conflicts.py` (16), and
`provider.test.ts` (10) on the desktop.

## Release decision

**No release.** Every defect found is in a path no v0.7.2 user could reach,
because no shipped surface sent a provider address. Nothing here fixes a shipped
defect, so a patch is not justified. `main` carries the work, unreleased, along
with the second-printer architecture.

A future minor release can carry both — and must re-run the U1 harness first.

## Reranked priorities

1. **Re-run the real-U1 harness against `main`.** Now the gate on everything else:
   two sprints of unreleased runtime change sit on top of the last hardware
   verification. Needs the printer and its address — a human gate, not work.
2. **Remaining Prusa semantics** — instances and copies, multi-volume objects,
   per-object overrides, `extruder="0"` for unassigned. Unchanged in rank, and now
   the largest piece of *code* outstanding.
3. **A second material provider through the seam** — small, and it would prove the
   provider abstraction the way the VORON proved the printer one. Spoolman is the
   only implementation, so "generic seam" is currently one example. OpenSpool or a
   firmware that exposes weight would do; U1Hub cannot until it tracks one.
4. **OBJ/GLB input** — unchanged, still below the others.

Material-provider interoperability leaves the top of the list: it is done to the
extent the ecosystem allows. What remains is verification, not capability.

---

# Second provider, and what one implementation was hiding

Run 2026-08-28 on `main` at `0bdcf18`, after the U1 project contract work.
**No release was made.**

## The question

Not "should Studio support more providers" — the seam existed. The narrower one:

> Is the material-provider seam actually provider-generic, or does it only look
> generic because there has never been anything to compare Spoolman against?

## Answer in one line

The business logic was already generic and the proof stands; the plumbing above
it was named after one product, and the address check had a hole one hop past the
address.

## Candidate research

Seven candidates were examined against the live projects, not from memory.

| Candidate | Integration API | Remaining quantity | Local | Licence | Verdict |
|---|---|---|---|---|---|
| **Bambuddy** (`maziggy/bambuddy`) | **Yes** — OpenAPI 3.1, `/api/v1`, versioned, documented for third parties | **Yes** — `label_weight` and `weight_used`, subtraction by the caller | Docker, port 8000 | AGPL-3.0 (server; Studio is an HTTP client, no linking) | **SELECTED** |
| U1Hub (`dlgambill/u1hub`) | No — Express routes its own UI calls, behind a password gate | **No** — RFID/QR *identity* only | Yes | MIT | Still ineligible |
| OpenSpool (`spuder/OpenSpool`) | An NFC tag format, not a service API | **No** — the format has no remaining field | Firmware | — | Ineligible |
| OctoPrint-SpoolManager (`OllisGit`) | No — a Python event bus for other plugins | Yes | Plugin | — | Ineligible: no third-party HTTP API |
| SpoolEase (`yanshay`) | Not documented | Yes (scale) | Yes | Apache-2.0 **+ Commons Clause** | Ineligible: no documented API, and a licence rider |
| SpoolBuddy (`macpit/spoolbuddy`) | Yes, but it is a *client* of Bambuddy's inventory | Via Bambuddy | Yes | MIT | Not an independent inventory |
| FilaMan (`ManuelW77/Filaman`) | ESP32 firmware; writes into Spoolman | Via Spoolman | Yes | MIT | Not an independent inventory |

**Why Bambuddy and not something Spoolman-compatible.** A clone would exercise the
same wire format and prove almost nothing. Bambuddy agrees with Spoolman about
almost nothing: `/api/v1/inventory/spools` against `/api/v1/spool`,
`include_archived` against `allow_archived`, `brand` against a nested
`vendor.name`, `rgba` (RRGGBBAA) against `color_hex` (RRGGBB), `material` and
`subtype` as separate fields against one `"PLA Matte"` string to split — and,
decisively, **no remaining-weight field at all**.

Bambuddy is a Bambu Lab printer manager, which is worth saying plainly: it is not
a tool a U1 owner necessarily runs. It was chosen as an inventory, on the
strength of its API and the distance between its schema and Spoolman's, and the
integration reads its spool inventory and nothing else.

## Authentication — a design gate, resolved without weakening anything

Bambuddy's API accepts an `X-API-Key`. Studio persists provider configuration in
`localStorage` and has **no secure credential store**, so keeping a bearer token
would have meant storing a secret in the clear.

Resolved by option B of the gate: Bambuddy supports auth-disabled deployments,
and a fresh instance answers `GET /api/v1/inventory/spools` unauthenticated —
measured, HTTP 200 with a JSON array. Studio reads that and sends no credential,
ever. An instance with authentication on answers 401/403, and Studio says so
plainly rather than asking for a secret it has nowhere to put. No security
property was traded for the feature.

## Real instance

**Bambuddy 1.2.5.3**, `ghcr.io/maziggy/bambuddy:latest`
(`sha256:c670164a…`), run in a session-owned Docker container on a session-owned
port, seeded through its own documented REST API, removed afterwards. No
pre-existing container was touched. The captured response is at
`backend/tests/fixtures/providers/bambuddy_1_2_5_3.json` with its own provenance
block, so the findings stay pinned without Docker.

## What the real instance contradicted

1. **Archived spools are omitted from the default listing** — 10 with
   `include_archived=true`, 9 without. The same trap Spoolman set, spelled
   differently. Studio asks for them.
2. **`remaining` is not a field.** Bambuddy's own interface computes
   `label_weight − weight_used`; over the API Studio does that subtraction, so
   the figure is arithmetic and is labelled as such.
3. **`last_used` was null on every spool**, including one whose weight had just
   been set through the scale endpoint — it is written by print consumption only.
   So an undated figure is the common case here too, reached through an entirely
   different schema. `last_weighed_at` is a real date for a real figure and is
   used; `created_at` is when the row was written and is not.
4. **It stores weights that cannot be true** — `weight_used: -500`, a used weight
   five times the label weight, and a 99,000,000 g spool were all accepted and
   returned unchanged. Each becomes `unknown` with a note, never "enough".

## Remaining weight, and how it is labelled

| Evidence | Label | `remaining_as_of` |
|---|---|---|
| Weighed — `last_scale_weight` and `last_weighed_at` present | **tracked** | `last_weighed_at` |
| Consumption recorded — `last_used` and a non-zero `weight_used` | **tracked** | `last_used` |
| A label weight minus a used figure nothing has touched | **derived** | none |
| No label weight, or none usable | **unknown** | none |

The middle rule is deliberately the same evidence test Spoolman's `_quality`
uses. That is what makes the equivalence below meaningful rather than arranged.

`core_weight` and `last_scale_weight` are deliberately **not** used to compute a
remaining figure. A scale reading is gross weight and `core_weight` defaults to
250 g whether or not anyone set it, so subtracting one from the other would
manufacture a number that looks measured and is not.

## The abstraction debt one implementation was hiding

Mapped before anything was written. The **business logic was already clean**:
`material_plan`, `send_check`, `freshness`, `combine` and `post_slice` name no
provider in any decision — `freshness.phrase` even takes the name as a parameter.

The **plumbing was not**. The wire field, the service keyword and the desktop
type were all literally `spoolman`, so the seam looked generic and read as an
integration. They are now `provider` and `provider_url`; `spoolman=` still works
and means exactly what it did, so nothing that already calls it has to change.

## The generic-seam proof

`test_provider_seam_equivalence.py`. Each scenario is built from **the raw
payload each provider really returns**, pushed through that provider's real
adapter, and the whole result compared after scrubbing the two names to one
token — equal, not similar.

Twelve situations: enough tracked recent · clearly short tracked recent · stale
short · derived short · undated short · remaining unknown · archived · a
different material · provider unavailable · a mapping pointing at nothing · a
printer/provider material conflict · a printer that agrees · a machine that
reports no filament at all.

All identical. One divergence was found and fixed rather than excused: Bambuddy
explained an unknown quantity and Spoolman said nothing at all, so the sentence
became shared. No verdict changed.

A source guard walks the syntax tree of every generic consumer and fails on a
comparison against a provider name. Prose is exempt; `if source == "spoolman"`
is not.

## Security: a real existing defect, fixed centrally

`validate_provider_url` checks the address the user types. That was not the whole
journey. **A local address answering `302 Location: http://example.com` was
followed, and the request left the machine** — demonstrated against this module,
not imagined: a local server that redirected every request produced example.com's
404 inside Studio's own error message.

This affected **Spoolman today**, not only the new provider. It is fixed at the
shared transport, with one opener for every provider, so the rule cannot be true
of one and not another. A redirect that stays on the local network is still
followed.

Also closed: `float()` accepts full-width Unicode digits, so `"１０００"` became
1000.0 and a malformed field quietly became a weight Studio might reason from.
`_number` now requires a plain ASCII number. This codebase has been caught by
Unicode digits twice before, both times through a regex `\d`.

## What did not change

Spoolman's semantics are untouched — archived handling, tracked against derived,
staleness, explicit mapping, conflicts, provider `None`, address validation. Its
suites pass unchanged. The one shared sentence added an explanation where there
had been silence, and changed no verdict.

## Real downstream evidence

Against the live instance, over the network, through combine → material plan →
send check:

| Case | Verdict | Send check |
|---|---|---|
| Weighed spool, 420 g, job 200 g | `enough`, trusted, fresh | no blocker |
| Weighed spool, 420 g, job 1200 g | `insufficient`, trusted | **blocker** — "It will run out part-way through. Last updated 18 minutes ago." |
| Declared kilo, nothing recorded, job 1200 g | `probably_short`, **not** trusted | warning, never a blocker |
| Label weight 0 | `unknown` | unknown, with the reason said out loud |
| Printer PLA against a mapping saying PETG | printer wins; the 700 g still used | disagreement shown, not resolved |
| Mapping at a spool that does not exist | slot absent, confidence unknown | reported |
| No provider at all | `unknown` | unchanged — a stock setup stays first-class |

A **stale** case could not be produced on the live instance: `last_weighed_at` is
stamped by Bambuddy at the moment of weighing, and no documented route sets it in
the past. Staleness is covered by fixture replay and by the equivalence table,
and that limit is stated rather than papered over.

## Tests

| | Before | After |
|---|---|---|
| Backend | 1731 passed / 4 skipped | **1804 passed / 4 skipped** |
| Desktop | 335 | **340** |
| selfcheck | 27/27 | **27/27** |
| Provider suites | 125 | **189** |
| Installed acceptance | not run against `main` | **still not run** |
| Real U1 | not run against `main` | **still not run** |

New: `test_provider_bambuddy.py` (41), `test_provider_seam_equivalence.py` (23),
and nine more in `test_provider_address_safety.py` for the redirect rule.

## Not run

Installed-build acceptance and the real-U1 hardware harness, neither of which has
been run against current `main`. `main` remains **not hardware verified**.

## Release decision

**No release.** Nothing here fixes a defect a released user can reach: no shipped
installer can select a provider at all. The redirect hole is real and is fixed on
`main`, and it was never reachable from a released build for the same reason the
last audit's defects were not.

## Reranked priorities

1. **Re-run the real-U1 harness against `main`.** Unchanged at the top, and now
   three sprints of unreleased runtime change deep. Needs the printer and its
   address — a human gate, not work.
2. **Installed-build acceptance against `main`.** Also not run since the local
   v0.7.2 build.
3. **Individual per-object placement**, if the product ever wants it.
4. **OBJ/GLB input** — unchanged, still last.

A third material provider is **not** on this list. The seam is proved by two
implementations that share no wire format; a third would cost the same and prove
much less.
