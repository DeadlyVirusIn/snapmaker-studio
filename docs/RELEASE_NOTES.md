# Snapmaker Studio v0.6.0 — the workflow becomes one thing

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

v0.5.0 could read a sliced job, plan the materials and decide whether to send it.
It still made you carry the file back from Snapmaker Orca by hand, and it could
not tell whether that file was the slice of the project you had just checked.

Both are fixed, and they are the same fix: Studio now follows one job through its
whole life instead of answering questions about files.

## The sliced job comes back on its own

Tell Studio once where Snapmaker Orca saves its exports. While you are on the page
that cares, it notices finished jobs appearing there and picks up the one that
belongs to your project.

It will not offer a half-written file: a candidate has to have stopped growing
*and* end the way a finished job ends. One folder, chosen by you. No background
service, no watching your disk, nothing uploaded anywhere.

## "Is this actually the slice of my project?"

Everything after slicing depends on that answer, and nothing in a G-code file
points back at the 3MF it came from. So Studio weighs what evidence exists — the
set of object names, the filament colours and materials in each slot, how many
slots, the target machine, the object count — and tells you how sure it is:

* **This is your project, sliced** — evidence hard to produce by coincidence
* **Looks like your project** — several signals agree, none decisive
* **Studio can't tell** — the evidence points both ways
* **A different project** — something that cannot be true of the same file

**A matching filename is never proof.** Two files can share a name and nothing
else, and Studio treats that as the weak hint it is. Object names are compared as
a fingerprint, so your model names never leave the file. If two candidates are
equally good, you get a question rather than a guess.

## What is loaded can come from more than the printer

The printer knows which spool is in a slot. It does not know how much is left on
it — no printer does. Studio now accepts optional read-only sources for that, over
your local network, starting with **Spoolman**.

The printer stays the authority on what is in a slot; another source may only add
what the machine cannot see. Nothing is required, nothing is written back to
anyone else's records, and when two sources disagree Studio says so rather than
picking one.

## "Do I have enough filament?"

With a source that tracks remaining weight:

> Slot 2 needs 87 g. The tracked spool has 43 g left — it will run out part-way
> through.

That is a blocker on the send check, because running out mid-print is not a
warning. Where a spool's weight is not tracked — which is every stock U1 — the
answer is *unknown*, and Studio says so instead of staying quiet.

## One surface for the whole job

**This print** shows the stages in the order they happen: before slicing,
prepared, after slicing. It is the same work as before, without needing to know
which page to open next. Every individual page still exists and still works — in
Simple mode the cockpit takes the place of "Check my model", which moves to More
tools.

## Fixed: uploads that were not finished

Moonraker accepts an upload and parses its metadata afterwards, so Studio used to
report success while the printer could not yet describe the file — the failure
the U1 Toolkit documented. Uploads are now confirmed against the printer's own
metadata, with one polite rescan request if it has not appeared, and a file of the
same name but a different size is caught. "Uploaded" now means the printer has it
*and* has read it.

Also fixed: handing Studio a `.3mf` where a `.gcode` was expected used to produce
a report that looked empty for no stated reason. It now names the mistake.

## Checked, and still honestly unknown

Free space on the printer. Traced properly this time rather than assumed:
`/machine/system_info` reports `total_bytes: 0`, `/server/files/roots` reports no
sizes, and nothing else on stock firmware exposes disk usage. Studio says it
cannot tell you whether a job will fit, and now says exactly what it looked at.

## Unchanged

Local-first: no cloud, no account, no telemetry, nothing uploaded. **Studio does
not slice** — Snapmaker Orca does. Your originals are never modified. Studio never
starts a print on its own, and every check is advisory rather than a promise.

## Upgrading

Install over the top. Settings and library are kept, and the upgrade path is part
of the release checks.

## Known limitations

- Windows only.
- The installer is not code-signed; verify the SHA256.
- Purge cannot be separated from printed filament in Snapmaker Orca output.
- The fitted nozzle cannot be read from stock firmware.
- Free storage is not reported by stock firmware.
- Painted colour cannot be classified without slicing.
- PrusaSlicer projects are read in full but not yet fully carried into a U1 copy;
  what cannot be carried is named in the fidelity report.

## Install

Installer name, size and SHA256: [RELEASE_METADATA.md](RELEASE_METADATA.md).
What was verified and how: [TRUST_STATUS.md](TRUST_STATUS.md).
