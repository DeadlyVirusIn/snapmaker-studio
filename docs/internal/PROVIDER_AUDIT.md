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
