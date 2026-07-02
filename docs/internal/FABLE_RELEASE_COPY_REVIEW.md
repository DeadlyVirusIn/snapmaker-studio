# Release Copy Review — Snapmaker Studio (internal engineering review)

> **Internal review document** — not user documentation.
> Date: 2026-07-02 · Per-release copy verdicts + ready-to-paste rewrites. Nothing has
> been edited on GitHub; apply only after maintainer sign-off.
> Companions: `FABLE_PUBLIC_RELEASE_AUDIT.md`, `FABLE_UPSTREAM_UTILIZATION_AUDIT.md`.

## 1. Release-by-release verdicts (beta.16 → beta.21)

| Release | Verdict | Problem (quoted where it matters) |
|---|---|---|
| beta.16 | MINOR | "prepare a **safe copy**", "Looks **ready** to prepare" (pre-truth-sweep wording); lowercase title |
| beta.16.1 | CLEAN | cosmetic title/H1 case mismatch |
| beta.16.2 | CLEAN | same cosmetic |
| beta.17 | MINOR | "creates a **clean** … copy with **U1-safe** settings" (pre-sweep wording) |
| beta.17.1 / 17.2 | CLEAN | well-qualified |
| beta.18 | MINOR | fine alone; see 18.1 |
| beta.18.1 | MINOR (hygiene) | body is a verbatim duplicate of beta.18, 17 minutes later, no stated change |
| beta.18.2 | MINOR | title "Visual Proof Pass" vs body H1 "UX polish"; discusses trimming "read-only" copy that was itself stale |
| beta.18.3 | CLEAN | quotes overclaims only to describe removing them |
| beta.18.4 | MINOR | title "Installed-App Readiness Verification" vs body H1 "Layout & Orca-Accurate Scale Fit" |
| beta.19 | **NEEDS REWRITE (P1)** | "…independent multi-model audit (**Codex + Claude; Antigravity returned empty both runs — documented, not relied on**)." |
| beta.20 | **NEEDS REWRITE (P0 — pinned "Latest")** | "…(**independent reviewers: Codex + Claude — Antigravity/Gemini failed in this run and were not counted**)…" |
| beta.20.1 | MINOR | missing trademark/independence disclaimer block; no SHA256/verify section |
| beta.20.2 / 20.3 | MINOR | no SHA256/verify section |
| beta.20.4 | MINOR (near-clean) | no in-body SHA256 (links RELEASE_METADATA.md — partial mitigation) |
| beta.21 | MINOR (P1 to fix) | **no download/SHA256/verify section at all**; body text itself clean |

Also: release flags inconsistent (beta.10–19 unflagged; beta.20 pinned **Latest**;
20.x–21 Pre-release). Recommendation: all 0.4.0 betas → Pre-release; move Latest to
the newest **accepted** build (today that is beta.20.4; beta.21 after acceptance).

## 2. Ready-to-paste fixes

### 2a. beta.19 — replace the audit sentence

Replace:
> Systemic readiness-truth fixes from an independent multi-model audit (Codex + Claude; Antigravity returned empty both runs — documented, not relied on).

With:
> Systemic readiness-truth fixes from a full independent audit of every page's wording.

### 2b. beta.20 — replace the audit sentence

Replace:
> A full page-by-page audit (independent reviewers: Codex + Claude — Antigravity/Gemini failed in this run and were not counted)…

With:
> A full independent page-by-page audit of the app's readiness wording…

### 2c. Standard verify section — append to beta.20.1, 20.2, 20.3, 20.4, 21

```markdown
## Download & verify

- Installer: `Snapmaker.Studio_<version>_x64-setup.exe` (attached below)
- SHA256 and size: see [docs/RELEASE_METADATA.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/main/docs/RELEASE_METADATA.md)
- The installer is not code-signed yet, so Windows SmartScreen may show "Unknown
  publisher". Download only from this page and verify the checksum first:
  `Get-FileHash -Algorithm SHA256 .\Snapmaker.Studio_<version>_x64-setup.exe`
```

For beta.21 specifically, the concrete values are: size 16,137,296 bytes, SHA256
`792ea37dc8e620cbd9be44fd475d0b1f6531f20a81cec8b44f5a621f43bea2b2`.

### 2d. beta.20.1 — prepend the standard disclaimer block

```markdown
> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.
```

### 2e. beta.18.1 — add one clarifying line under the title

> This patch re-releases beta.18 with a corrected installer build; the feature set is identical to beta.18.

(Verify the actual reason from the git tags before pasting; do not guess in public.)

### 2f. beta.21 body — otherwise keep as-is

The existing beta.21 body is professional and truth-consistent (five-item Simple nav,
Fix Plan described as "advisory — not a guarantee", honest limits block). Only the
missing Download & verify section (2c) needs appending. No other rewrite needed.

### 2g. beta.20.4 body — keep as-is

Clean. Optionally append 2c for consistency.

## 3. README wording fixes

The README is professional; no internal terms; version block current. Two optional
polish items: (1) refresh the four beta.16-era screenshots after beta.21 acceptance —
the current dashboard image contains pre-sweep hero copy ("Perfect prints…", "clean
U1 project") and two images show older version stamps (beta.15 / beta.13) that a
careful judge will notice; (2) repo *description* (GitHub setting, not README):
suggest "Pre-print intelligence for the Snapmaker U1 — advisory checks, honest
readiness, local-first. Prepares U1 profile copies for Snapmaker Orca."

## 4. Banned / internal wording list (for release pages and public docs)

Never in public copy: internal AI/tool names (model or vendor names of review
tooling, e.g. the ones scrubbed from beta.19/20); maintainer personal names
("pending <name>" → "manual installed-app acceptance pending"); chat-transcript tone
("my mistake", "failed attempt", "force-killed" as anecdote); local user paths;
process IDs; raw tool logs. Overclaim words that require a qualifier in the same
sentence or must be avoided: ready, safe, clean, guaranteed, print-ready, verified,
collision-free, fully validated, 100%, perfect. "read-only" only for file analysis —
never for the Printer Hub (monitoring + user-confirmed controls). Enforcement hooks
already exist: `backend/tests/test_public_claims.py` (claims + AI-name guards),
`desktop/src/lib/copy.test.ts` (future-tense promises), `naming.test.ts` (feature
naming). Gap: nothing lints *release bodies* — add a release-checklist step: run the
banned-terms grep against the drafted body before `gh release create`.

## 5. Related doc-level fixes (from the repo scan, same sweep)

- `docs/TRUST_STATUS.md`: replace all 15 personal-name mentions with "the maintainer" /
  "manual installed-app acceptance"; same for the 1 hit in CLAUDE.md and the FABEL_* docs.
- Move/banner the three FABEL_* review docs (internal review, not user docs);
  `ORCA_CLI_SPIKE.md` can stay public with its roadmap reference reworded.
- `docs/RELEASE_CHECKLIST.md:75–76`: genericize the tool-name list ("external review
  tooling") — the line that warns against leaking names currently names them all.
- Unqualified "100%" corpus claims: `CHANGELOG.md:52`, `docs/ARCHITECTURE.md:82`,
  `docs/PRODUCT_VISION.md:70,217`, `docs/ROADMAP.md:109`, `docs/INNOVATION_FUND.md:67`
  → add the "structurally valid, internal gate, not print success" qualifier.
- `docs/brand/BRAND_GUIDELINES.md:28` + `docs/brand/README.md:13`: "print-ready" →
  "prepared U1 profile copy".
- `validation/validate_corpus.py:9` + `validation/corpus/README.md:23`: replace the
  real local example path with `path/to/your/3mf-folder`.
- `CHANGELOG.md:9`: beta.1 still labelled "UNRELEASED" — fix the tag.
- Brand asset `Gemini_Generated_Image_….png`: rename (discloses generator in filename).
