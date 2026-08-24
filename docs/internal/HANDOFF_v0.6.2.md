# Handoff — after the v0.6.2 stable release

Written 2026-08-24, immediately after a crash-recovery pass over the working tree.
The previous session ended abruptly; this document is the reconstruction of what
survived and the state a fresh session should start from. Read
`docs/SUBMISSION_STATUS.md`, `docs/TRUST_STATUS.md` and
`docs/internal/evidence/0.6.2.json` before trusting any number quoted anywhere
else.

Nothing was lost. The tree was clean and exactly at the release commit; only the
previous session's own conversation and its closing report were gone.

## Authority order for project state

When two sources disagree about what is true right now, believe them in this
order, and correct the loser rather than working around it:

1. Explicit current facts from the maintainer.
2. The published GitHub release and the live Innovation Fund listing.
3. Live system, account and repository state — `git`, the release API, the mailbox.
4. `docs/internal/evidence/<version>.json` for that version, and
   `docs/internal/evidence.json` for the current one.
5. `docs/SUBMISSION_STATUS.md` and `docs/TRUST_STATUS.md`.
6. Everything else, including README, CHANGELOG and any planning document.

Never turn a stale TODO into new work without first proving the task is actually
incomplete. Never resurrect finished work. A lower level never overrides a higher
one.

## Exact release state

| | |
|---|---|
| Current stable | **v0.6.2** — published, not a prerelease, not a draft |
| Tag | `v0.6.2` on commit `077bfa239661547da0876f91fbfd6fe42863cc7e` |
| Branch | `main`, at that same commit — local `main`, `origin/main` and the tag are identical |
| Published | 2026-08-24 13:52 UTC, from `main` |
| Installer | `Snapmaker.Studio_0.6.2_x64-setup.exe` |
| Size | 16,923,818 bytes |
| SHA256 | `687eabdddff714a614c94f46aa6a4a6a95d0e8a444fbc194c085d8ed9ee740de` |
| Release page | <https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.6.2> |

The asset digest on the live release matches the hash recorded in this release's
evidence snapshot; the two were checked against each other during recovery.

**`main` carries no unreleased work.** The tag is the tip. Every commit listed in
the v0.6.2 sprint is committed and pushed, and there are no stashes, no untracked
files, no extra worktrees and no dangling objects newer than 2026-08-23.

## The immutable evidence architecture

This is the load-bearing change of v0.6.2 and the thing most likely to be broken
by a future session that does not understand it.

Evidence used to be one canonical file, rewritten on every release. Because there
was only one of it, publishing silently rewrote the numbers that *every* document
quoted, including the sections describing releases that had already shipped —
TRUST_STATUS.md told readers that v0.6.0 was verified with 967 backend tests and
26 hardware checks when it shipped with 822 and 20, figures from a suite and a
harness that did not exist yet.

How it works now:

- `docs/internal/evidence/<version>.json` is one **immutable snapshot per
  release**, written when that release is published.
- `docs/internal/evidence.json` is a copy of the current release's snapshot, kept
  for callers that just want "what is true now".
- Publishing a release **adds a file and never edits one**. A value a release did
  not record comes back as `null` with a note saying so, because "not recorded" is
  a fact and a plausible number is not.
- Historical snapshots were reconstructed from the only authority available: what
  the repository recorded at that release's own tag. Nothing was copied forward.

Tooling and guards:

- `tools/evidence/snapshot.py` — writes a release's snapshot;
  `--rebuild-history` reconstructs past ones from their tags.
- `tools/evidence/update.py` — refreshes the current-state copy.
- `backend/tests/test_evidence_integrity.py` — holds the line in three
  directions: current documents against the current snapshot (down to installer
  name, size and hash), every versioned section of TRUST_STATUS.md against *that
  version's* snapshot, and every published release's snapshot re-derived from its
  own tag, so publishing cannot rewrite history.
- `backend/tests/test_release_docs.py` — version and installer-metadata
  consistency across CHANGELOG, README, RELEASE_METADATA, RELEASE_NOTES,
  TRUST_STATUS, `package.json`, `tauri.conf.json` and `Cargo.toml`.

Do not hard-code a number a snapshot already carries, and do not regenerate a
past release's snapshot to make a document pass.

## What v0.6.2 fixed

Every item was a defect in the published v0.6.1 build.

- **A release's evidence changed when a later release shipped.** Fixed by the
  architecture above; the historical sections were restored from their own tags.
- **Studio could fail to start on a machine short of ports.** The loopback service
  spoke HTTP/1.0 and closed the connection after every call, and drawing one page
  makes a dozen calls. With ~14,000 connections held open by something else, the
  service could not be reached and sometimes could not bind. It now speaks
  HTTP/1.1 so a client keeps one connection, retries the bind, and falls back to
  fixed ports below the dynamic range.
- **"This printer does not report which filaments are loaded" could be untrue.** A
  dropped connection and a printer that genuinely reports nothing both came back
  as `None`, so a momentary network failure was stated as a fact about the user's
  machine. They are distinct now, printer reads retry once when the machine cannot
  open a socket at all, and the firmware route degrades to "Studio could not ask"
  rather than returning an error.
- **A re-slice could pass as the file that was checked.** The send fingerprint
  identified a job by size and modification time, so a re-slice landing on the
  same byte count within the same timestamp tick matched both. It now also hashes
  the file's contents at three bounded windows — start, middle and end.
- **The "Extended firmware" badge appeared on stock printers**, and the acceptance
  and release-doc guards missed the README's combined row, which carried
  `822 · 284 · clean · clean` through an entire release.

Added in the same release: every item in the send confirmation can show what it
was read from, one level down, and the send card states when the printer was last
actually read.

## Verification standing at release

Canonical values live in `docs/internal/evidence/0.6.2.json`. Regenerate rather
than retyping.

- backend `pytest` — 1004 passed, 3 skipped
- desktop `npm run test` — 293 passed; `tsc --noEmit` and `npm run build` clean
- `u1convert selfcheck` — 25 of 25 over 15 documented routes
- installed-build acceptance — 30 of 30, including the v0.6.1 → v0.6.2 upgrade
- real Snapmaker U1, read-only — 26 of 26
- demo — 66 seconds, recorded from the installed build
- `cargo check` — clean, green in CI

Harnesses: `tools/acceptance/run.ps1`, `tools/hardware/verify.ps1`,
`tools/demo/record.ps1`, `tools/evidence/snapshot.py`, `tools/evidence/update.py`.

This work is complete and must not be re-run to "confirm" the release.

## Known limitations — currently true, stated publicly

- **Windows only** — see `internal/CROSS_PLATFORM_ASSESSMENT.md`.
- **The installer is not code-signed.** Verify the SHA256 before installing.
- **Purge cannot be separated from printed filament** in Snapmaker Orca output.
- **The fitted nozzle cannot be read** from stock firmware.
- **Free storage is not reported** by stock firmware — traced, not assumed.
- **Painted colour cannot be classified** without slicing.
- **Provenance is evidence, not proof.** A job carrying neither object names nor
  colour data can only be `unknown`, and Studio says so rather than matching on
  the filename.
- **Remaining filament is only known when something tracks it.** A stock U1
  cannot, so sufficiency is unknown unless a provider such as Spoolman is
  configured.
- **One machine, one firmware version.** The read-only harness generalises; the
  sample does not.

## Deliberately not started

- **Extended firmware enrichment.** Detection exists and is positive-only. There
  is nothing Studio does with the answer yet, and inventing a use would be worse
  than leaving it.
- **Prusa preparation beyond the settings whose meaning survives the crossing.**
  What is carried and what deliberately is not lives in `prusa.CARRIED` and
  `not_carried`.
- **A U1Hub adapter.** It exposes no interface it means to offer. The proposal is
  in `docs/interop/U1HUB_INTEROP_PROPOSAL.md`; until it exists, Studio depends on
  nothing of U1Hub's and reads none of its files.

## The real remaining human gates

All three carry forward from the v0.6.1 handoff and were re-checked during this
recovery rather than copied. Everything up to each gate is already prepared.

1. **Send the drafted listing correction to community@snapmaker.com.**
   *Verified still open:* the confirmation thread of 29 June 2026 contains exactly
   one message — the confirmation itself. No reply has been sent. The draft is
   written and sits in the thread. Sending mail under the maintainer's name, to
   the people judging their entry, is theirs. Context and the investigation of why
   this is the only available route are in
   `docs/innovation-fund/LISTING_UPDATE.md`.
2. **Post the community update.** Written and reviewed in
   `docs/innovation-fund/COMMUNITY_POST.md`. Posting happens under the
   maintainer's identity. No request for stars, no request for votes, no
   Innovation Fund lobbying. *Not independently verifiable from this machine* —
   the project's own records say it has never been posted; if the maintainer has
   since posted it, that fact outranks this document.
3. **Submit the SignPath application** for a signed installer. The form accepts
   legal terms on the maintainer's behalf. Still open: the release asset is
   unsigned, and `docs/CODE_SIGNING_POLICY.md` still states that no signing
   service account exists and that MFA must be confirmed on GitHub and enabled on
   SignPath at account creation.

Nothing about *entering* the Innovation Fund is outstanding. The entry was
submitted 24 June 2026, confirmed 29 June by community@snapmaker.com, and is
publicly listed among the 41 projects in the running. Evaluation closes
22 September 2026; 20 win. **Do not submit the form again.**

## Genuine unreleased work

**None.** `main`, `origin/main` and `v0.6.2` are the same commit. No stashes, no
untracked files, no uncommitted changes, no second worktree, and no dangling
commit newer than the v0.6.1-era amend of 2026-08-23. There is no partially
finished feature to recover, resume or re-land.

## Next technically valuable work — not started, and not to be started without direction

Ordered by what would most change what a user can verify. These are candidates,
not a plan, and none of them should begin before the maintainer chooses one.

1. **Painted-colour enumeration.** `color_plan` reports painted colours as
   unclassified because per-triangle paint data is encoded and Studio will not
   guess. Decoding it properly turns "cannot classify" into a real answer on the
   hardest multi-colour projects. Biggest remaining accuracy gain, and genuinely
   difficult.
2. **Diagnostic packs as data.** The ecosystem registry proved a rule set can live
   in JSON with a schema and a test that rejects rules referencing facts the
   engine cannot measure. The same shape for *diagnostics* would let the community
   contribute checks without touching engine code — the strongest long-term answer
   to the openness criterion.
3. **Broaden the hardware surface.** More machines and more firmware builds would
   turn "verified on hardware" into "verified across hardware".
4. **A second printer.** "Not U1-only by construction" is unproven. One more
   machine — profile plus capability detection, no per-check branching — would
   prove it and expose every hard-coded U1 assumption.
5. **Project reproducibility manifest.** A versioned JSON summary emitted beside a
   prepared copy: provenance, graded traits, changes applied, fidelity result.
   Most of the content already exists across `traits`, `fidelity` and the ledger;
   this is the assembly.

Explicitly not doing: slicing or forking a slicer, a second printer dashboard, a
browser extension, or requiring Extended Firmware.

## Standing rules that bite most often

- Studio never slices, never takes autonomous control of a printer, never uploads
  anything anywhere, and never modifies an original file.
- Never force-kill a slicer, printer or user GUI process. Only processes this
  session started, tracked by PID.
- No local paths, usernames, hostnames, printer addresses or private model names
  in tracked files or screenshots. Anonymise evidence at the source.
- Unknown stays unknown. Withdraw an unprovable claim rather than patching it.
- Do not publish a prerelease to show progress, and do not hard-code a number an
  evidence snapshot already carries.
- Publishing adds an evidence snapshot. It never edits one.
