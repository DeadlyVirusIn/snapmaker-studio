# Snapmaker Studio v0.4.0-beta.6

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

**This is a hardening / audit patch** on top of beta.5. It folds in the real
multi-LLM (`/octo:review`) follow-up fixes and a production-hardening sprint:
stronger input validation, safer error and file-output handling, softened
print-success wording, and a freshly bundled, smoke-tested sidecar. No new
product features; the beta.5 feature set is carried forward unchanged.

## The Intelligence Layer for Open 3D Printing
Orca slices. Fluidd monitors. **Studio helps decide what to fix before you print.**
Before a layer is sliced, Studio reads your model and your Snapmaker U1 (read-only)
and surfaces likely print risks, what it costs, and what to sell it for — one
screen, plain language. Advisory only; not a guarantee of print success.

### Doctor pillars
- **Project Doctor** — will it fit and print on your U1?
- **Printer Doctor** — a 0–100 health score from the U1's own signals.
- **Cost Doctor** — true cost, suggested price, and profit.

## New in beta.6 — hardening & audit patch

- **Real `/octo:review` follow-up fixes** — request body-drain hardening, a
  non-finite (NaN/Infinity) scale guard, and dead-code/doc-claim cleanup found by
  an actual multi-provider review (Codex + Claude).
- **Centralized API input validation** — bad user input (non-numeric, NaN/Infinity,
  out-of-range port, missing fields, malformed JSON) now returns a clean **HTTP 400**
  with a short, sanitized message instead of a 500.
- **Sanitized error responses** — server 500s no longer echo raw Python exception
  text or file paths to the client.
- **Report output path validation** — fix-report writes are constrained to a `.json`
  file inside the output directory, refuse to overwrite a model/source file, and
  block `..` traversal.
- **Reduced batch polling** — batch status polls every 2s (was 400ms), easing load
  on the local engine during long jobs.
- **Public claim hardening** — softened absolute print-success and corpus-result
  wording to advisory framing (it surfaces likely risks; it is not a guarantee);
  explicit advisory/read-only labels on the Print Quality and First Layer Doctors.
- **Sidecar freshness guard** — the release tooling (`npm run release:windows` +
  the tag-triggered release workflow) always re-freezes the PyInstaller sidecar and
  **smoke-tests the bundled sidecar's endpoints**, so a stale sidecar can't ship.
- **Fresh bundled-sidecar endpoint smoke** — verified on this build (see Quality).
- **CSP tracked as a pre-GA blocker (NOT fixed)** — see `docs/SECURITY.md`. The
  current beta uses a local-only renderer + loopback token; a Content Security
  Policy must be hardened and GUI-verified before a wider/signed public launch.
- **Windows code signing still pending** — this installer is **unsigned**.
- **Plate Remap XML parser hardening documented as deferred** — the verified
  safe-copy writer is unchanged; the regex→lxml swap is planned with a test backlog
  (`docs/design/PLATE_REMAP_XML_HARDENING.md`).

## Carried from beta.5 (feature set, unchanged)
- **Print Quality Doctor (MVP)** — pick a symptom (stringing, ringing, layer shift,
  warping, first layer, blobs, under-extrusion, rough surface, bridging, colour
  bleed) for likely causes, safe first checks, where to look in Orca, and what not
  to change blindly. Advisory only; never changes settings/g-code.
- **First Layer Doctor (MVP)** — pick what you see for likely causes, beginner
  checks, clearly-marked advanced U1 checks, and slicer settings to inspect.
  Advisory only; no printer/config/g-code changes.
- **Beginner workflow guidance** — a "Get Started: from model to first print" page;
  steps outside Studio (slicing, preparing the printer) are labelled as such.
- **Doctor navigation cohesion** — every Doctor reachable from the sidebar; a "when
  to use each" overview; "Why Studio?" in the secondary/help area.
- **Plate Color Remap confidence** — each colour tagged **changing** or
  **protected**; verified safe copy, original untouched.
- **Model Discovery polish** — clear key-missing state, link-out-only providers
  explained, privacy note. No downloads or imports (v1 is search + link-out); never
  scrapes.
- **Scale Doctor guidance** — plain material multiplier estimate and explicit
  joints/threads/holes/thin-detail warnings. Analysis-only; writes nothing.
- Visual 3D plate preview remains deferred (colour/part summary fallback).

## Safety
- All Doctors are **advisory and read-only**: no printer control, no auto-fix, no
  profile/g-code/settings writes, no guaranteed-print claims.
- Model Discovery does not download or import models (v1 is search + link-out), and
  never scrapes.
- Real-world validation fixtures are not included in the repository (they may be
  copyrighted/commercial).

## Windows install (unsigned beta)
This beta installer is **currently unsigned**, so Windows SmartScreen may show
**"Unknown publisher."** That is expected for an unsigned beta. Only download it
from the official GitHub release, and verify the checksum before installing.

```
File:    Snapmaker.Studio_0.4.0-beta.6_x64-setup.exe
Size:    16,057,930 bytes
SHA256:  E9F6E0A6FA33908E532655F42117B043CD6065ED56CF9FE3D48A1792A3C9A547
```

Full guidance: [docs/windows-install.md](windows-install.md). Code-signing
readiness plan: [docs/windows-code-signing.md](windows-code-signing.md).

## Quality
- Backend: 232 automated tests pass (3 conditional real-fixture tests skip when the
  fixture is absent).
- Frontend: vitest 51/51; TypeScript clean; production build clean.
- Sidecar re-frozen for this release; bundled-sidecar smoke verified: `/health` 200,
  Doctor/plate/compatibility/model_search/scale/quality/first_layer routes present,
  bad input → 400, valid input → 200, 0 orphan processes on exit.

_Beta — local-first; nothing leaves your computer._
