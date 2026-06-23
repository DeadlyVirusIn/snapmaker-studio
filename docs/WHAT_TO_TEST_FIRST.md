# What to Test First (beta.10)

Three short beginner paths through Snapmaker Studio. Everything runs locally;
nothing is uploaded. Originals are never modified, and findings are advisory
readiness estimates, not guarantees of print success.

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

## Path 1 — Beginner U1 owner

You have a U1 and a 3MF file and want to know if it's ready before slicing.

Steps:

1. Open Snapmaker Studio.
2. Open your U1 3MF file from the Dashboard.
3. Let Studio read the real geometry and show the design-health summary.
4. Run the Compatibility Doctor for a readiness estimate against the U1.
5. Read each finding — what was found, why it matters, what to try.

Expected outcome: a plain-language readiness estimate with a short list of likely
risks and concrete next steps, so you know what (if anything) to fix before
opening the slicer.

## Path 2 — Multicolor file user

You have a multicolor or multi-plate file and want the colors/plates to come out
clean.

Steps:

1. Open Snapmaker Studio and open your multicolor 3MF.
2. Review the detected materials, colors, and plate counts.
3. Open Plate Color Remap.
4. Apply the suggested remap and review the before/after.
5. Prepare a clean copy (your original stays untouched).

Expected outcome: a tidied color/plate mapping and a clean, print-ready copy, with
the original file unchanged.

## Path 3 — Failed print user

A print failed and you want to figure out why before trying again.

Steps:

1. Open Snapmaker Studio and open the file that failed.
2. Open the Print Quality Doctor.
3. Follow the "Fails even with supports" path if supports didn't help.
4. Switch to known-good troubleshooting mode and compare against a print that
   worked.
5. Change one thing at a time based on the guidance, then re-check.

Expected outcome: a narrowed-down list of likely causes and a clear next change to
try — instead of guessing and wasting more filament.

See also: [JUDGE_OVERVIEW.md](JUDGE_OVERVIEW.md),
[DEMO_SCRIPT_BETA9.md](DEMO_SCRIPT_BETA9.md),
[windows-install.md](windows-install.md).
