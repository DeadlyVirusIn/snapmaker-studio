# Snapmaker Studio v0.9.0 — the project that crosses whole

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

Bring a project from another slicer and Studio prepares a U1 copy of it. Until
now that copy quietly lost things: painted colour, the parts an object was built
from, the settings you had set on one object, and — in one path — the print
settings themselves. This release is mostly about the crossing, and everything in
it was established by handing Snapmaker Orca a file, letting Orca save it back,
and reading what Orca wrote.

## Your project arrives as the project you made

### Painted colour survives

A prepared copy carried painted colour exactly as the source wrote it, and Orca
opened it with nothing painted. Painting is only read when the mesh sits in its
own object file inside the package — so that is where a painted object goes now,
and the colour arrives.

Eight painted facets in, eight out, in the same slots. The encoding did not
change; where it lives did.

### An object's parts arrive as parts

A project saying "this half prints in filament 2 and that half in filament 5"
used to arrive as one undifferentiated object, and Studio correctly reported the
second filament as not carried. The copy now splits the object along its real
volume boundaries, so each part crosses with its own filament.

The parts recombine to the source geometry facet for facet, nothing is
duplicated, and a filament in slot 5 is not quietly clamped to four.

### A modifier arrives as a modifier

Some volumes in a project are not meant to be printed — they change how the
slicer behaves near them. Studio used to carry the whole object as one mesh, so
those arrived as solid plastic. Worse than the "not carried" it reported.

Each now crosses with the word Orca actually uses for it, over geometry marked as
not-printable. Measured rather than guessed: two cubes that do not touch, sliced,
and the plate footprint read back — 500 mm² when the second is solid, 400 mm² for
every non-printing role. None of them becomes plastic.

### Several objects arrive as several objects

A project with more than one object kept its geometry in one place, and painting
is not read from there — so a multi-object painted project lost its colour while
every individual check passed. Every object now crosses as its own object with
its own file, its own place on the plate and its own records.

If any one object cannot be carried, the whole project declines and crosses
verbatim instead. Half a conversion would leave the rest in a shape the target
does not read.

### Settings you set on a single object

Studio read per-object settings and reported every one of them as not carried.
Three of them can cross — layer height, infill density and supports — and they do
now, in the target's own vocabulary rather than the source's.

That distinction matters: copying the source's spelling across is writing
nonsense with a straight face. Handing Orca one candidate at a time, with an
invented word as the control, drew the line: those three survive, the source's
own spellings do not. Every value is checked before it is written, because a
value the slicer cannot read does not cost you the setting — it costs you the
object.

A per-object layer height is withheld on a multi-filament plate, because Orca
refuses to slice a plate whose objects disagree about it when a prime tower is
involved. The audit says so rather than writing a project that will not open.

## Two fixes you would have noticed

**The print settings from your project were reaching the file and not the
slicer.** Studio translates five values from a source project — layer height,
first layer, infill density, wall count and brim — so a project sliced at 0.15 mm
with four walls does not arrive at 0.2 mm with two. They were being written but
not *declared*, and an undeclared value is replaced by the preset on load. The
whole of that promise was correct in the file and invisible in the slicer. It is
declared now.

**An unpainted patch on a painted object** printed in the wrong filament. It now
prints in its own volume's filament, as it should.

## A second materials provider

Studio has read **Spoolman** for a while to answer "will this job run out of
filament?". It now reads **Bambuddy** as well.

**Settings → Materials provider** offers None, Spoolman or Bambuddy. There is no
second page: pick one, give the address of the machine on your network that runs
it, test the connection, map a spool to each slot. Changing provider clears the
address and the mapping, because a spool number only means something to the
provider that issued it.

Everything after that point is identical whichever one you use — the same
sufficiency rules, the same warnings, the same refusals. A short, tracked, recent
weight still blocks a send; a stale one, a figure worked out from a spool's
declared size, and a figure with no date all warn instead; nothing tracking the
spool stays unknown.

Both are read-only. Studio does not create spools and does not decrement anyone's
remaining weight.

## Fixed on the way

- **A provider address that redirected off your network was followed.** A local
  address is not a promise about where the *next* request goes, and one that
  answered with a redirect to the public internet was being followed. Refused
  now, for every provider, in the one place all of them share. Studio still makes
  no requests to the internet.
- **A slot with a stale mapping claimed the printer had looked at it.** If a
  mapping pointed at a spool that no longer exists, Studio said "the printer
  reports it empty" — with no printer connected and nothing having looked. It now
  says which of the three it actually means: the printer saw an empty slot, your
  mapping points at a spool that is gone, or nothing can tell.
- **Malformed numbers from a provider** could become a weight. They stay unknown.
- **A modifier off the plate** was reported as an object off the plate.
- **Eight values in the U1 template** had never reached a print — restated preset
  defaults that the slicer overwrote on load, including a nozzle type and start
  and end code older than the presets they were competing with. Removed.

## Also in this release

- The fidelity report answers each fact twice: what is in the file, and what the
  slicer will do with it. "Preserved" used to mean only the first.
- Prepare declares the values the slicer is not to take from its own preset, so a
  stated value is the value that runs.
- Placement moves a project onto the plate in one piece, in the target's layout.

## Still true

Studio does not slice — Snapmaker Orca does. Studio never starts a print on its
own; every action in Printer Hub is confirmed by you. Everything is local: no
cloud, no account, nothing uploaded off your local network — the one transfer
Studio makes is a sliced job to your own printer, after you confirm it. Your
original files are never modified; preparing always writes a copy. Advice is
advisory: Studio reports what it can establish and says "unknown" when it cannot,
and it does not promise a print will work.

Windows only. The installer is not code-signed — verify the SHA256 on the release
page before running it.

## Known limitations

- The fitted nozzle cannot be read from stock firmware, and free storage is not
  reported by it either.
- Remaining filament is known only where something tracks it. Without a provider
  it stays unknown, which is the honest answer on a stock setup.
- A materials provider that requires a sign-in cannot be read; Studio has nowhere
  safe to keep a credential and says so rather than storing one.
- Two providers are implemented and normalise into one shared shape. That is
  evidence the shape is general; it is not a claim that every provider will work.
- Painted colour is read, but whether two colours meet on a layer is decided by
  the slice, so such colours have a toolhead reserved rather than being called
  simultaneous.
- An object whose volumes cannot all be represented declines the split and
  crosses whole, with the audit naming what that costs.
- One machine, one firmware version. The read-only verification generalises; the
  sample does not.

Verification for this release — every count, and what was run against the real
printer — is in
[TRUST_STATUS.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.9.0/docs/TRUST_STATUS.md).
Installing and verifying the download:
[windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.9.0/docs/windows-install.md).
Materials providers in detail:
[MATERIAL_PROVIDERS.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.9.0/docs/MATERIAL_PROVIDERS.md).
