# Snapmaker Studio v0.6.1 — the answers, attacked

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

v0.6.0 closed the workflow: the sliced job comes back on its own, Studio works out
whether it belongs to your project, and the send confirmation says what will
actually happen. This release was spent trying to make all of that lie.

Everything below was a real defect in v0.6.0. If you are running it, this is worth
the download.

## Studio could not read the object names in a real Orca job

The strongest evidence that a G-code file is the slice of your project is that it
prints the same objects. Studio looked for that in the labels Snapmaker Orca writes
when object exclusion is switched on — and it is off by default.

Three jobs pulled off a real U1 carry 90, 52 and 3,476 object labels between them,
in the *other* dialect, and not one of the kind Studio was looking for. So the
evidence was there, in the files it was written for, and Studio was not reading it.
It reads both dialects now, and PrusaSlicer's as well.

## A matching setup was being read as a matching project

Same printer, same spools, same materials came out as "looks like your project" —
which is true of every job sliced in a workshop. Any file in the folder could be
called the slice of any project.

Evidence is now separated into what identifies the *model* — which objects the job
prints — and what merely describes the *setup* it was sliced with. With nothing
identifying the model, the answer is "Studio can't tell", however much of the rest
lines up, and the reasoning is one click away wherever the verdict appears.

The separation also fixes the opposite mistake: a project re-sliced in a different
colour is still that project, and a job printing one plate of a four-plate project
is part of it rather than a stranger.

## The watcher would offer a file that stopped part-way

Snapmaker Orca writes its time estimate and filament total inside the first few
hundred kilobytes of a job, and the old completion check accepted either as proof
the file had finished. A job cut off early contained both. It now needs the ending
its own dialect actually has.

The same check also slept two seconds per file inside a request the app repeats
every five seconds, so a folder of twelve jobs blocked for twenty-four. It
remembers sizes between polls instead, and never sleeps.

## Nothing re-read the world between the check and the send

You read the checks, walk to the printer, come back and press send. In between, a
slot can empty, a spool change, a print start, or the job be re-sliced to the same
filename — and nothing on screen looks any different.

The check now records what it looked at. Sending re-reads the same things, and if
any of it moved, nothing is uploaded: what changed is named, the fresh answer
replaces the stale one, and the decision goes back to you.

## "Upload failed" was four different situations

A printer that refused the file, a connection that dropped, bytes accepted but
never listed, and a file the printer has not finished reading each need something
different done about them. They are told apart now — including a printer still
describing the file this one replaced, which is how a job starts with the previous
file's estimate.

## Filament figures now say where they came from

"87 g needed, 43 g left, it will run out" only stops a send when it rests on a
figure something is actually keeping track of, short by more than that tracking can
drift. A number of unstated origin warns instead. Negative weights, weights larger
than the spool holds, and weights that are not weights are refused rather than
used, and a tracker that contradicts the printer about what is loaded is shown as a
disagreement rather than silently resolved.

## A model name could reach a support bundle

The bundle drops your project's filename on purpose — it goes to a stranger. The
sliced-job half of it was carrying the name through anyway. Fixed, and now guarded
by a test that tries to get a model name out of every route into the bundle.

## A badge told people they had firmware they do not have

"Extended firmware" appeared whenever a printer reported fifteen or more macros —
which a community build adds, and so does an owner who writes their own. Detection
is positive only now: the firmware has to answer for itself, distinguishably from
what the printer serves for a path nobody claims. Not finding it never means your
printer is stock, because Studio cannot know that.

## A prepared PrusaSlicer copy prints the way the project did

Layer height, first layer height, infill, walls, brim, support on or off and the
filaments now carry into the U1 copy, each recorded with where it came from. A
project sliced at 0.15 mm with four walls used to arrive as the starter profile's
0.2 mm and two, which is a different print of the same shape.

Temperatures deliberately do not carry: a PrusaSlicer profile's 245 °C is about a
Prusa hotend, and copying it into a U1 project would look like fidelity while
handing one machine another machine's numbers.

## What has not changed

Studio still does not slice — Snapmaker Orca does. It still never starts a print,
never modifies your original file, and never sends anything anywhere: no cloud, no
account, no telemetry.

## Verified against this installer

- Installed-build acceptance: **30/30**, including upgrading in place from v0.6.0
- Real Snapmaker U1, read-only: **26/26**
- `u1convert selfcheck`: **25/25** over 15 documented routes
- `pytest`: **967 passed, 3 skipped** · `npm run test`: **290 passed**
- Bounds measured on files built for the purpose: a 525 MB job reads in 0.20 s
  holding 40 MB; its timeline scans in 3.0 s holding 9 MB

Verification detail: [docs/TRUST_STATUS.md](TRUST_STATUS.md). Installer name, size
and hash: [docs/RELEASE_METADATA.md](RELEASE_METADATA.md).

## Still true, and stated plainly

Windows only. The installer is not code-signed — verify the SHA256. Purge cannot be
separated from printed filament in Orca's output. The fitted nozzle cannot be read
from the printer, and stays unknown. Free storage is not exposed by stock firmware.
Painted colour cannot be classified without slicing. Remaining filament is known
only where something tracks it.
