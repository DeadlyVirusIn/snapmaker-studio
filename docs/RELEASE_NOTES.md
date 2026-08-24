# Snapmaker Studio v0.6.2 — evidence that stays true

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

A patch release. Four defects, three of them found by attacking the project's own
verification rather than its features.

## A release's evidence changed when a later release shipped

Studio's public argument is "check it yourself", so its counts are load-bearing.
There was one canonical evidence file, rewritten on every release — and because
there was only one of it, publishing quietly restated the numbers that *every*
document quoted, including the sections describing releases that had already
shipped.

The trust record said v0.6.0 had been verified with 967 backend tests, 290 desktop
tests, a 30-check acceptance run and 26 hardware checks. v0.6.0 shipped with 822,
284, 28 and 20. The larger figures come from a suite and a harness that did not
exist when it was published. v0.5.0 and v0.4.0 had their hardware counts
overwritten the same way.

Evidence is now one immutable snapshot per release. Past releases were
reconstructed from what each release's own tag recorded — and where a release
recorded nothing, the snapshot says so rather than carrying a plausible number
backwards. Publishing adds a file; it never edits one. A test re-derives every
published release's evidence from its own tag, so a future release cannot rewrite
what an earlier one was verified with.

## Studio could fail to start on a machine that is short of ports

The loopback service spoke HTTP/1.0, which closes the connection after every
response, and drawing a single page makes a dozen calls. Each one took a fresh
source port and left it in TIME_WAIT.

That is invisible on a quiet machine and fatal on a busy one. The machine this was
found on had 14,000 connections held open by Docker Desktop; Studio's own service
could not be reached, and sometimes could not even bind — the app simply did not
start, for a reason that had nothing to do with Studio.

It speaks HTTP/1.1 now, so a client keeps one connection. Binding retries and falls
back to fixed ports below the dynamic range, and if even that fails the message
says what is actually wrong.

## "This printer does not report which filaments are loaded" could be untrue

A dropped connection and a printer that genuinely reports nothing came back the
same way, so a momentary network failure was reported as a fact about the user's
machine. They are told apart now, printer reads retry before giving up, and the
firmware page degrades to "Studio could not ask" rather than an error.

## A re-slice could pass as the file that was checked

The send fingerprint identified a job by size and modification time. A re-slice
that lands on the same byte count, written inside the same timestamp tick, matched
both — which is exactly the case the fingerprint exists for. It now fingerprints
the contents as well, at three bounded windows: the start, the middle and the end.

## Also in this release

Every item in the send confirmation can show what it was read from, one level down
— the beginner never opens it, and an expert who doubts a verdict should not have
to ask. The card says when the printer was last actually read. And the guard that
checks public counts now reads the README's combined row, which said
`822 · 284 · clean · clean` through an entire release because the old check only
recognised a count next to the word "passed".

## What has not changed

Studio still does not slice — Snapmaker Orca does. It still never starts a print,
never modifies your original file, and never sends anything anywhere: no cloud, no
account, no telemetry.

## Verified against this installer

- Installed-build acceptance: **30/30**, including upgrading in place from v0.6.1
- Real Snapmaker U1, read-only: **26/26**
- `u1convert selfcheck`: **25/25** over 15 documented routes
- `pytest`: **1004 passed, 3 skipped** · `npm run test`: **293 passed**

Verification detail: [docs/TRUST_STATUS.md](TRUST_STATUS.md). Installer name, size
and hash: [docs/RELEASE_METADATA.md](RELEASE_METADATA.md). Each release's evidence
is kept separately under `docs/internal/evidence/`.

## Still true, and stated plainly

Windows only. The installer is not code-signed — verify the SHA256. Purge cannot be
separated from printed filament in Orca's output. The fitted nozzle cannot be read
from the printer, and stays unknown. Free storage is not exposed by stock firmware.
Painted colour cannot be classified without slicing. Remaining filament is known
only where something tracks it.
