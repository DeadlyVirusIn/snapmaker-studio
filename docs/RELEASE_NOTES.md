# Snapmaker Studio v0.4.0-beta.20.3 — STL Project Doctor Consistency Fix

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

Installed-app acceptance found that an STL and its matching 3MF — the same design —
got very different Project Doctor results. This patch makes STL analysis consistent
and removes developer text from the GUI.

## Fixes

- **STL files now get real Project Doctor design analysis.** When Studio can read an
  STL's geometry it shows a design-health score and findings (watertight, overhang /
  support, bed fit) — the same kind of result a 3MF gets — instead of a blank "—".
  A blank score now appears only when the geometry genuinely can't be read.
- **No command-line text in the GUI.** The Project Doctor no longer shows raw
  `repair` command text. STL preparation now reads "Create a U1 profile copy, then
  review it in Snapmaker Orca before slicing", with a **Prepare U1 copy** button.
- **Design health and U1 preparation are separate.** A healthy STL still needs a U1
  profile copy before Orca — Studio shows the design score and the "prepare a U1
  copy" step as distinct things, and does not call an unprepared STL "ready".
- Cost & Pricing manual-grams behaviour is unchanged.

## Honest limits

- Studio prepares **U1 profile copies for review in Snapmaker Orca** — it does not
  slice.
- **Originals are never modified** — preparing a model writes a new copy.
- **No print-success guarantees.**
- Object placement, spacing and bed-boundary fit remain **advisory / not verified by
  Studio** and must be checked in Snapmaker Orca before slicing.

Local-first · open source (MIT).
