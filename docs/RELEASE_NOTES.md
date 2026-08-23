# Snapmaker Studio v0.5.0 — the loop gets intelligent

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

v0.4.0 taught Studio to read the job your slicer produced and check it against
your printer. This release answers the three questions that come next.

## What happens during this print?

Studio reads the whole job in one pass and tells you, in order:

* it starts on slot 3, loaded with your yellow PLA;
* the bed goes to 65 °C;
* slots 1, 2 and 4 join in at layer 1;
* **slot 3 is finished with at layer 239** — that spool can come out;
* it pauses at layer 88 and waits for you;
* 764 tool changes in total, each one purging some filament;
* 281 layers, ending on slot 4.

Every line carries the G-code that proves it, folded away until you want it. This
was verified against a real 89 MB four-colour job: read in half a second, using
eight megabytes of memory.

## What should I load?

Once a job is sliced its tool assignments are fixed — slot 3 prints what the
slicer decided slot 3 prints. So Studio answers the question you actually have,
slot by slot: this one is ready; this one is empty and the job needs it; this one
has PETG and the job wants PLA; this one the job never touches, so leave it alone.

Colour is advisory and says so. Material is compared by family, so "PLA Matte"
loaded against a job sliced for "PLA" is not reported as wrong.

Studio does not track your filament and does not want to — U1Hub, Spoolman and
OpenSpool already do that well. This is the intelligence over whatever spool state
your printer reports.

## Ready to send?

Three buckets, kept strictly apart:

* **Will stop the print** — provable. A slot the job uses is empty. A tool the
  printer does not have.
* **Worth settling first** — real, but not proof. A different colour is loaded.
  The printer is busy. The job pauses and nobody is standing there.
* **Studio can't check this** — the fitted nozzle, which stock firmware does not
  report; free space, which this firmware does not report either.

An unknown is never promoted to look thorough, or demoted to look clean. And the
send button is not disabled when there is a blocker — it is your printer, and
Studio says why instead of deciding for you.

## PrusaSlicer projects are read, not just recognised

Studio used to detect a PrusaSlicer `.3mf` and read its printer model, and
nothing else — so an ordinary Prusa project came out as "0 filaments, no layer
height" and every check downstream had nothing to work with.

It now reads the project's own configuration: printer model and bed size, every
filament slot with its type, colour, vendor and diameter, layer and first-layer
heights, supports, temperatures, per-object extruder assignments and overrides,
and variable layer-height profiles. What a U1 copy cannot keep — variable layer
height, per-object overrides, support styling — is named in the fidelity report
instead of quietly disappearing.

## One button that talks to the internet, and only when you press it

**Help → Check for a newer version** asks GitHub which release is newest. That is
the only outbound request Studio makes. It sends nothing about you, your files or
your printer, it never runs on its own, and it never downloads or installs
anything — the answer is a version number and a link.

It is built into the desktop shell rather than the page, so the web view keeps its
lock-down, and a test fails the build if that ever changes.

## Fixed

- The timeline scanner missed everything in a job written on Windows: lines end
  with CR LF there, and the stray carriage return sat between the marker and the
  end of the line. Found by its own test.
- A quoted filament name containing a comma invented an extra extruder.
- The public evidence counts had drifted from what the harnesses produce — 21/21
  where it is 27, 15/15 where it is 18, 495 backend tests where there are 766.
  There is now one canonical source and a test that fails the build when a
  document disagrees with it.

## Upgrading

Install over the top. Settings and library are kept, and the upgrade path is part
of the release checks: v0.4.0 is installed, used, then upgraded, and the resulting
state is verified.

## Unchanged

Local-first: no cloud, no account, no telemetry, nothing uploaded. **Studio does
not slice** — Snapmaker Orca does; reading a G-code file is not producing one.
Your originals are never modified. Studio never starts a print on its own. Every
check is advisory and none of them promises a successful print.

## Known limitations

- Windows only.
- The installer is not code-signed; verify the SHA256.
- Purge cannot be separated from printed filament in Snapmaker Orca output.
- The fitted nozzle cannot be read from stock firmware.
- Free storage is not reported by this firmware, so Studio says so rather than
  guessing whether a job will fit.
- Painted colour cannot be classified without slicing.

## Install

Installer name, size and SHA256: [RELEASE_METADATA.md](RELEASE_METADATA.md).
What was verified and how: [TRUST_STATUS.md](TRUST_STATUS.md).
