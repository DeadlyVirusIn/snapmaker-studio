# Snapmaker Studio — Demo Script (ARCHIVED — beta.9, not current beta.10)

> **ARCHIVED — beta.9, not current beta.10.** May not match the current beta.10 UI.
> See [JUDGE_OVERVIEW.md](JUDGE_OVERVIEW.md) for the current demo flow.

A 5–7 minute walkthrough for judges and first-time viewers. Everything runs
locally; nothing is uploaded. Findings are advisory readiness estimates, not
guarantees of print success.

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

## Before you start

- Have Snapmaker Studio (beta.10) installed and open.
- Have a sample U1 3MF file ready (the repo's `examples/` folder has sample cubes).
- Optionally have one known-good print result on hand for the comparison step.

## The flow

### 1. Open Studio (~30s)

Launch Snapmaker Studio. Point out that it runs entirely on the local machine —
no account, no cloud, no upload. This is the pre-print intelligence layer, not a
slicer or a printer controller.

### 2. Show the Dashboard / Doctors (~45s)

Show the Dashboard and the available Doctors. Frame the idea: each Doctor is a
read-only check that reports what was found, why it matters, and what to try.
Originals are never modified.

### 3. Open a U1 3MF (~45s)

Open a U1 3MF file and let Studio read its real geometry — colors, size, volume,
complexity, and a design-health read on the actual mesh, in plain language. Stress
that this is the real mesh, not a guess from the file name.

### 4. Run the Scale Doctor size options (~60s)

Open the Scale Doctor and walk the Scale Options Ladder. Show how it presents
clear size options when a model needs rescaling or doesn't fit, and encourage
trying one change at a time rather than several at once.

### 5. Print Quality Doctor → "Fails even with supports" (~75s)

Open the Print Quality Doctor and follow the "Fails even with supports" path.
Show how Studio walks through likely causes when a print fails despite supports,
explaining each in plain language so the user can decide what to fix.

### 6. Known-good troubleshooting mode (~60s)

Switch to the known-good troubleshooting mode and compare the problem file against
a print that worked. Show how the comparison helps narrow down what changed
instead of guessing.

### 7. Compatibility Doctor or Plate Color Remap (~45s)

Show either the Compatibility Doctor (readiness against the U1, with reasons) or
the Plate Color Remap (sorting multicolor plates/colors cleanly). Pick whichever
best fits the sample file on screen.

### 8. Close (~20s)

End on the core message:

> Studio helps decide what to fix before wasting filament.

## Notes for presenters

- Keep it advisory: say "readiness estimate" and "likely risk," never "guaranteed."
- Reinforce local-first: nothing leaves the machine.
- If asked about the install warning: the beta installer is not code-signed yet,
  so SmartScreen may show "Unknown publisher"; verify the SHA256 from the official
  release.

See also: [JUDGE_OVERVIEW.md](JUDGE_OVERVIEW.md),
[WHAT_TO_TEST_FIRST.md](WHAT_TO_TEST_FIRST.md),
[SCREENSHOTS_BETA9.md](SCREENSHOTS_BETA9.md).
