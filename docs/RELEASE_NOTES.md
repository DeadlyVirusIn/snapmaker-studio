# Snapmaker Studio v0.4.0-beta.21 — One Clear Path for a Novice

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

This release makes the first ten minutes simple: open a model, see one prioritized
fix plan, prepare a U1 profile copy, hand it to Snapmaker Orca. Power users lose
nothing — Advanced mode is unchanged and one click away.

## Simple mode, simplified

- **Five sidebar items instead of twelve:** **Home · Check my model · My designs ·
  Printer · Help.** Everything else (Get Started, Compatibility, Scale, Print
  Quality, Colors & Materials, Cost, Find Models, Batch) lives under **More tools**.
- **Simple mode is the default for new installs.** If you already chose Advanced,
  your choice is kept — Advanced mode itself is untouched.

## Your fix plan

Opening a model now starts with **Your fix plan** — at most five prioritized,
plain-language actions built from the checks Studio already ran (plate fit, mesh
health, colours vs toolheads, supports, multi-part spacing). Each action says
whether to **do it in Studio** or **do it in Snapmaker Orca**, and the list is
labelled what it is: advisory — not a guarantee.

## Fewer dead ends

- The old Multi-Material explainer tab (which only told you to go somewhere else)
  is gone; the colour check runs automatically on an open model.
- `/doctor/pricing` and `/doctor/profit` now land on the one Cost page instead of
  quietly showing the same content under three names.
- The Scale page states plainly that 3MF scaled export isn't supported (preview,
  then resize in Orca) — no more disabled "not ready" button, and no more
  future-tense promises anywhere in the app (a test now enforces this).
- Raw technical fields (setting paths, evidence strings) in Compatibility findings
  are tucked behind a "Technical detail" disclosure.

## Honest limits (unchanged)

- Studio prepares **U1 profile copies for review in Snapmaker Orca** — it does not slice.
- **Originals are never modified** — preparing a model writes a new copy.
- **No print-success guarantees.**
- Object placement, spacing and bed-boundary fit remain **advisory / not verified by
  Studio** and must be checked in Snapmaker Orca before slicing.

Local-first · open source (MIT).
