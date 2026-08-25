# Snapmaker Studio v0.7.0 — the painting, read

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

Multi-material painting is the part of a project most tools treat as opaque. A
model painted in four filaments looks, to anything that is not a slicer, like a
mesh — and Studio was one of those things. It could prove a project *had* painted
regions, and then said painted colour "cannot be classified without slicing".

The paint was in the file the whole time. This release reads it.

## What Studio now knows about a painted project

Before anything is sliced, from the project's own per-facet data:

- **Which filament slots the painting uses.** Exactly, including a slot the
  project paints with but never lists — which is a defect in the project, and is
  reported rather than quietly renumbered onto a filament that happens to exist.
- **How much of the model each painted colour covers** — the number of facets it
  touches *and* the surface area it accounts for. Those are two different facts
  and are shown as two: a mesh's triangles are not equal in size, so 40% of the
  facets is not 40% of the surface.
- **The height band each painted colour occupies**, reconstructed from the
  painted patches themselves and placed by the object's own transform, so the
  heights are the heights on the plate.
- **Which colour the unpainted parts print in** — from the part's own assignment,
  or `unknown` where the project does not say.

## What that changes for a project with more colours than toolheads

The old answer to a painted six-colour project was one sentence: *Studio cannot
classify this safely*. Now each colour gets a verdict and the evidence behind it:

- a colour whose painting shares a height band with another **needs a toolhead**,
  because the two can meet on a layer;
- a colour painted only between, say, 38.2 mm and 61.0 mm, with every other
  colour ending below it or starting above, **can be handled as a planned swap**;
- a colour that cannot be compared — no readable height, or another colour
  assigned to a whole object whose extent Studio has not measured — stays
  **unclassified, with that reason attached**.

The colours card leads with the sentence a beginner needs — "Parts of this model
are painted with 3 filament colours." — and keeps every number behind it one
click away.

## Where Studio still stops

**Two painted colours whose heights overlap can meet on a printed layer. Whether
they do is decided when Orca slices.** Studio says the first and never the
second. That boundary is the point of the feature, not a gap in it.

## Fixed

- **Every painted project in the field was reported as unpainted.** The trait
  looked for painting in `Metadata/model_settings.config`, where no slicer has
  ever written it.
- **The fidelity audit compared painting by counting markers in the bytes.** That
  cannot tell painting that survived from painting that was rewritten: remap
  every painted facet to a different filament, or shrink a painted region to a
  quarter of its area, and the count is identical. It compares the painting
  itself now.

## What has not changed

Studio still does not slice — Snapmaker Orca does. It still never starts a print,
never modifies your original file, and never sends anything anywhere: no cloud, no
account, no telemetry.

## Verified against this installer

- Installed-build acceptance: **31/31**, including upgrading in place from v0.6.2
- Real Snapmaker U1, read-only: **26/26**
- `u1convert selfcheck`: **27/27** over 15 documented routes
- `pytest`: **1104 passed, 3 skipped** · `npm run test`: **304 passed**

The decoding itself was checked against files two real slicers wrote: paint was
handed to PrusaSlicer 2.9.6 and OrcaSlicer 2.4.2, and both wrote every attribute
back byte for byte. The painted fixture was then sliced for a five-extruder
printer, and the G-code used tools T0–T4 and no others — which is what proves a
paint state names filament N counting from one, rather than that being asserted.

Verification detail: [docs/TRUST_STATUS.md](TRUST_STATUS.md). Installer name, size
and hash: [docs/RELEASE_METADATA.md](RELEASE_METADATA.md). What painting Studio
reads and where it stops: [docs/PAINTED_COLOUR.md](PAINTED_COLOUR.md). Each
release's evidence is kept separately under `docs/internal/evidence/`.

## Still true, and stated plainly

Windows only. The installer is not code-signed — verify the SHA256. Purge cannot be
separated from printed filament in Orca's output. The fitted nozzle cannot be read
from the printer, and stays unknown. Free storage is not exposed by stock firmware.
Painted colour is read from the project, but whether two painted colours share a
printed layer is decided by the slice, not the file. Remaining filament is known
only where something tracks it.
