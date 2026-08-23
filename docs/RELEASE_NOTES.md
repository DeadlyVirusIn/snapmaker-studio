# Snapmaker Studio v0.4.0-beta.24 — Verified against a real U1

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

This is the first Snapmaker Studio build checked against an actual Snapmaker U1
rather than only against tests. The printer immediately found a bug.

## Your printer already knew which filaments are loaded

Studio was telling U1 owners *"this printer does not report which filaments are
loaded"*. The printer was reporting all four, in a shape Studio was not looking
for: stock U1 firmware publishes loaded filament as parallel lists — the types in
one, the colours in another, the sub-types and vendors in others, and a
`filament_exist` flag that is the printer's own answer to "is there a spool in
this slot".

Studio now reads all four slots, colour and sub-type included, and **Before you
slice** compares the materials your project needs against what is actually on the
machine.

The same session confirmed something Studio has always claimed but had never
proved on hardware: stock firmware genuinely does not report which nozzle is
fitted. That check still reads *"Nozzle size — check this yourself"*, and it is
now known to be honest rather than assumed to be.

## Every message that names a problem now says what to do about it

- When the fidelity report cannot account for something, it now tells you to open
  the prepared copy in Snapmaker Orca, compare it against your original, and
  report it — because Studio failing to explain its own change is a bug worth
  hearing about.
- Something Studio cannot read is labelled *"Not checked — Studio can't read it"*,
  which is a different statement from "this is fine".
- The printer check pointed at a field that did not exist. It now names Printer
  Hub.
- **Toolhead** — the word all the colour planning rests on — is explained before
  it is used.

## Open a project by handing it to Studio

Studio now accepts an `.stl` or `.3mf` path on its command line and opens it on
launch, so a file can be sent to Studio from a shell, a script, or a shortcut.

## How this build was checked

Every check below ran against **this installer**, not against the source tree:
installed into a clean directory, launched, driven through the real application
window, then uninstalled.

- 21 installed-application checks passed — the project loads, the placement,
  preflight, fidelity, ledger, colour-plan and cost results all appear in the real
  UI, the input file is byte-identical afterwards, and uninstalling leaves nothing
  behind.
- The real U1 verification above was performed read-only. Studio never heats,
  moves, homes, uploads to, or configures a printer on its own.
- Full software suites, the end-to-end self-check, and the real-slicer regression
  fixtures all pass.

The exact commands, counts and evidence are in
[TRUST_STATUS.md](TRUST_STATUS.md).

## Unchanged

Local-first: no cloud, no account, nothing uploaded. Studio does not slice —
Snapmaker Orca does. Your originals are never modified. Studio never starts a
print on its own, and it gives advisory checks, not a guarantee of print success.

## Install

See [RELEASE_METADATA.md](RELEASE_METADATA.md) for the installer name, size and
SHA256, and [windows-install.md](windows-install.md) for the full instructions.
The installer is not code-signed yet, so Windows SmartScreen will show an unknown
publisher — verify the SHA256 before running it.
