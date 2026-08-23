# Snapmaker Studio v0.4.0 — the loop closes, and the beta ends

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

This is the first stable release of Snapmaker Studio, and it finishes the job the
project set out to do.

## Studio can now see the other half

Until today Studio stopped at the slicer. It read your project, explained the
risks, compared the project against your printer, prepared a corrected copy, and
handed that copy to Snapmaker Orca. What Orca produced was somebody else's
problem — which meant the most expensive failures were the ones Studio could not
see:

* the job prints from slot 3, and slot 3 is empty;
* the job was sliced for PETG, and PLA is loaded;
* the job was sliced for a different printer entirely.

None of those are visible in the project file. None are visible on the printer
alone. **Open the `.gcode` your slicer produced and Studio now reads it**, then
compares it to the printer as it is right now.

Drag it onto the window, or hand it to Studio on the command line — a sliced job
is not treated as a project, and goes straight to the new **After Slicing** page.

Studio still does not slice. Snapmaker Orca does.

## What it reads, and what it refuses to

From the file itself: which machine it was sliced for, the slicer and version,
layer count and height, estimated time, filament per slot, which tools it
actually prints from, the nozzle it expects, whether it defines excludable
objects.

Against your printer: every tool it needs exists; every slot it uses has a spool;
the loaded material matches, compared by family so "PLA Matte" is not a false
alarm against "PLA"; the sliced bed fits the real bed; the firmware supports the
object exclusion the job assumes; the printer is free.

And the refusals, which matter just as much. **Purge is never split out of a
total the slicer did not split.** Snapmaker Orca reports one filament figure per
slot and does not separate purged filament from printed filament, so Studio
reports the total, says the split is not available from this file, and leaves it
there. The nozzle check is still an honest unknown, because stock firmware does
not report which nozzle is fitted.

## Costing from measurements instead of estimates

Once a file is sliced, guessing stops being necessary. Filament by slot and print
time are read from the file. Every line says where its number came from —
measured by the slicer, derived from your prices, an assumption you can change,
or not stated at all. A figure the file does not contain reads as unknown, never
as zero.

## A bug report worth sending

Studio asks people to tell it when it gets an analysis wrong. That report needs
facts behind it, and gathering those by hand is exactly what nobody does. **Help →
Reporting something Studio got wrong** now assembles them: your project's traits,
the Doctor's findings, the sliced job, what your printer reported, and the fix
ledger.

Your username, home folder, file paths, machine name and printer address are
replaced *before* the bundle is assembled, and you can read the entire thing
before it is written to disk. Studio never sends it anywhere.

## Upgrading from a beta

Install over the top. Your settings and library are kept, and the upgrade is
checked as part of the release: a beta.24 installation is created, used, then
upgraded, and the resulting state is verified.

## What was fixed

- `u1convert selfcheck` crashed at the very end on a default Windows console —
  the results table contained a character `cp1252` cannot encode. The one command
  Studio tells strangers to run now prints its own results on a stock console.
- The support bundle leaked a model's file name: redacting a username inside a
  path inserted characters that stopped the path redaction dead. Paths are
  redacted first now. Caught by its own test before the feature ever shipped.
- A slicer that reports filament per slot without a total now has the total added
  up rather than left blank.

## Unchanged

Local-first: no cloud, no account, no telemetry, nothing uploaded. Studio does not
slice. Your originals are never modified. Studio never starts a print on its own.
Every check is advisory — it does not promise a successful print.

## Known limitations

- **Windows only.** macOS and Linux builds are not built or tested.
- **The installer is not code-signed.** SmartScreen will show an unknown
  publisher; verify the SHA256 below before running it.
- **Purge cannot be separated** from printed filament in Snapmaker Orca output.
- **The fitted nozzle cannot be read** from stock firmware.
- **Painted colour cannot be classified** without slicing, and is reported as
  unclassified rather than guessed.

## Install

Installer name, size and SHA256: [RELEASE_METADATA.md](RELEASE_METADATA.md).
Full instructions and uninstall: [windows-install.md](windows-install.md).
What was verified and how: [TRUST_STATUS.md](TRUST_STATUS.md).
