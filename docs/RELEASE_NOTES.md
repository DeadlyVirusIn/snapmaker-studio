# Snapmaker Studio v0.4.0-beta.22 — Object placement, and the right tool for your file

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

Two new things Studio can tell you about a project, plus a set of fixes that make
a downloaded project open cleanly in Snapmaker Orca.

## Where your objects actually sit

A project made for a bigger printer carries that printer's coordinates. A small
part can be well inside the U1's size limits and still land off the plate — every
size check passes, and Snapmaker Orca's only word for it is "out of bounds".

Studio now names the object, its size, which edge it hangs past and by how many
millimetres. When one move fixes it, there is a button that writes a **new copy**
with the whole arrangement moved onto the plate. Your original file is not
changed, and the creator's layout, rotation, scale and height are kept exactly.

For projects with several plates, Studio measures the plate layout the file
actually uses and moves every plate onto the U1's own grid, keeping the spacing
the creator had between them. It moves every plate or none — and when it cannot
work out the layout safely, or an object is not listed on any plate, or a plate
will not fit, it says which of those is the reason instead of half-fixing your
project.

## Best tool for this project

The U1 has a large open-source ecosystem, and the hard part for a beginner is
having to know all of it before any of it can help. Studio now reads what your
project actually contains and names the tool that fits, with the reason drawn
from your file, its licence, and a warning if it is an experimental community
project.

Mixed nozzle sizes, image-texture data, an already-sliced project, a project
downloaded for another printer — each points somewhere different. When there is
nothing special about your file, Studio says so and sends you to Snapmaker Orca.

Studio never installs anything and never opens a tool on its own, and it only
says a tool is installed when it actually found it on your computer.

## Opening a downloaded project cleanly

When Studio prepares a U1 copy it now also corrects the things that stop
Snapmaker Orca behaving properly on a U1 — and only those things. Your print
settings are still yours.

- **Exclude Object is switched on**, so the U1 can cancel one failed object
  without losing the whole plate, and adaptive bed mesh has object outlines to
  work from.
- **An automatic brim is switched off.** Snapmaker Orca decides differently from
  the slicer your project was made in and can add a brim it never had. A brim you
  chose yourself is left alone.
- **Tree supports combined with variable layer height** are switched to the
  hybrid style — the correction the original slicer makes but never saves into
  the file.
- **Filament lists are repaired** where an empty or missing entry would make the
  slicer warn or refuse to open the project.
- **The original printer's sliced output is removed**, so Snapmaker Orca slices
  fresh for your U1 instead of showing a preview of a print that would never
  happen. Your plate pictures are kept.

Every change shows what it was before and why it changed.

## What a print costs, when the file knows

If a project has already been sliced, it records what that slicer worked out: the
time and material per plate, and the grams of each filament. Studio now costs
from those real figures and tells you that is where they came from, including
different prices per material.

If the project has not been sliced, Studio says so and tells you what to do —
it does not invent a number.

## Also in this release

- Studio finds your printer more reliably: it now checks both addresses a U1
  answers on. When nothing answers, it tells you to turn on Advanced Mode on the
  printer's touchscreen, which is the usual reason.
- Files downloaded from model sites are opened with a size limit, so a corrupt or
  deliberately malformed project is refused with a clear message instead of
  freezing the app.
- Printer addresses are checked before Studio uses them.
- New command-line tools for people who want the data without the app:
  `u1convert traits`, `ecosystem`, `cost` and `placement --fix`.

## Unchanged

Local-first: no cloud, no account, nothing uploaded. Studio does not slice —
Snapmaker Orca does. Your originals are never modified. Studio never starts a
print on its own, and it gives advisory checks, not a guarantee of print success.

## Install

See [RELEASE_METADATA.md](RELEASE_METADATA.md) for the installer name, size and
SHA256, and [windows-install.md](windows-install.md) for the full instructions.
The installer is not code-signed yet, so Windows SmartScreen will show an unknown
publisher — verify the SHA256 before running it.
