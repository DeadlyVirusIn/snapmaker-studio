# Snapmaker Studio v0.4.0-beta.20.2 — Manual Cost Entry + Collision Honesty

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

Installed-app acceptance surfaced two honesty gaps on complex multi-object 3MF
projects. This patch fixes both and is honest about what Studio does not yet check.

## Fixes

- **Cost & Pricing Doctor — manual grams entry.** When Studio can't read
  volume/grams from a file, the calculator no longer dead-ends on an "unavailable"
  card. It now shows the assumptions form so you can enter grams from Orca's
  filament estimate; with grams entered and **Recalculate**, you get material cost,
  suggested price and profit. Blank grams with no estimate shows "Enter grams to
  calculate cost" rather than fake numbers. Results only update on Recalculate.
- **Object spacing / collisions are honest now.** Studio does **not** yet verify
  object-to-object spacing for multi-part 3MF layouts. The Project and Compatibility
  Doctors now say so plainly — "object spacing / collisions are not verified by
  Studio yet; open in Snapmaker Orca and check for too-close / collision warnings
  before slicing" — and no longer report a multi-object plate as ready / no issues.
- **Support enforcers vs support.** The Compatibility Doctor now warns when a model
  uses support enforcers while support generation is turned off, so those regions
  don't print unsupported.

## Honest limits

- Studio prepares **U1 profile copies for review in Snapmaker Orca** — it does not
  slice, and it does not claim collision-free or finished output for complex
  3MF / multi-object layouts.
- Object placement, spacing and bed-boundary fit remain **advisory** and must be
  verified in Snapmaker Orca before slicing.
- **Originals are never modified** — preparing a model writes a new copy.
- **No print-success guarantees.**

Local-first · open source (MIT).
