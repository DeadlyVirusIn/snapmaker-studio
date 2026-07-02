# Snapmaker Studio v0.4.0-beta.20.4 — Release Acceptance + Trust Cleanup

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

No new features. This release makes what Studio says about itself match what it
actually does — in the app and across every document.

## In the app

- **One name for the printer page.** It is the **Printer Hub** everywhere now; a few
  places still called it "Printer Doctor" and one step claimed live monitoring was
  "read-only" — the Printer Hub monitors *and* offers controls that always ask for an
  explicit confirmation. A test now keeps the naming consistent.
- **No more future-tense promises.** The First Layer page pointed at checks that
  "will live in" another page; it now points at what exists today (bed-mesh and
  telemetry live in the Printer Hub).

## Documentation truth pass

- **One canonical source for release facts.** New
  [docs/RELEASE_METADATA.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/main/docs/RELEASE_METADATA.md)
  holds the current version, installer name, size, SHA256, and trust status — other
  docs point at it instead of repeating (and drifting from) those values. The README
  checksum is filled in again.
- **Historical documents are labelled.** Early fund/judge documents described a
  read-only beta that predates Printer Hub controls; each now carries a clear
  "HISTORICAL" banner so old claims can't be mistaken for current ones.
- **Build volume clarified.** The U1's printable volume is **270×270×270 mm**
  (per the Snapmaker Orca U1 profile). The larger figures reported by the printer
  itself are axis *travel* limits, not printable area — the docs now say which is which.
- **Honest corpus wording.** Every "112/112" mention now reads: 112/112 files
  produced structurally valid U1 profile copies in the internal validation gate —
  this is not a print-success guarantee.
- **Security notes updated.** The desktop app's Content-Security-Policy is enabled
  and documented. A new test pins that 3MF archives are parsed fully in memory —
  archive entry names are never used as file paths, so crafted-archive path-traversal
  attacks don't apply.

## Honest limits (unchanged)

- Studio prepares **U1 profile copies for review in Snapmaker Orca** — it does not slice.
- **Originals are never modified** — preparing a model writes a new copy.
- **No print-success guarantees.**
- Object placement, spacing and bed-boundary fit remain **advisory / not verified by
  Studio** and must be checked in Snapmaker Orca before slicing.

Local-first · open source (MIT).
