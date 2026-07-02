# Public Release Audit — Snapmaker Studio (internal engineering review)

> **Internal review document** — written for the maintainers, not end users.
> Date: 2026-07-02 · Scope: everything a visitor sees on the public GitHub repo and
> release pages, audited as a hostile-but-fair judge, novice user, security reviewer,
> and ecosystem analyst would. Review-only: no code changed, nothing published,
> beta.21 not marked accepted.

Companions: `FABLE_RELEASE_COPY_REVIEW.md` (per-release copy + rewrites),
`FABLE_UPSTREAM_UTILIZATION_AUDIT.md` (upstream state + utilization).

---

## 1. Executive summary

The public surface is in far better shape than a month ago — the beta.20.x truth
sweep worked, the canonical `RELEASE_METADATA.md` exists, the newest release bodies
(beta.20.4, beta.21) contain zero internal terms and honest, well-qualified claims,
and no secrets, emails, or private IPs exist anywhere in tracked files.

Three problems still stand between the repo and "judge-ready":

1. **Two old release bodies name internal AI review tooling** (beta.19 and beta.20:
   "Codex + Claude … Antigravity returned empty / failed"), **and beta.20 is the
   release pinned as "Latest"** — the single most-visited release URL lands on the
   worst sentence in the repo. This is the P0.
2. **"the maintainer" appears 15 times in `docs/TRUST_STATUS.md`**, the trust document linked
   from the README and release notes. Personal-name acceptance chatter reads as
   internal process leaked into public docs. (Also 1 hit in CLAUDE.md and a few in
   the FABEL_* review docs.) P1.
3. **The newest releases stopped printing verification info.** beta.16–beta.20 each
   stated the SHA256 in the body; beta.20.1–21 dropped it (20.4 at least links the
   metadata doc; **beta.21 has no download/verify section at all**). For an unsigned
   installer whose trust story is "verify the hash," the newest release giving the
   least verification guidance is exactly backwards. P1.

**Verdict:** README is professional (clean of internal terms; accurate "read-only"
usage; current version block). Release pages are *mostly* professional but need a
targeted cleanup of 2 old bodies, the Latest pin, and verification sections before
promoting beta.21. No private data exposure found. Recommended path: **docs-only +
release-copy cleanup now → manual GUI acceptance → then promote beta.21.** No
beta.21.1 app patch is needed for anything found here.

---

## 2. Findings table (public-facing surfaces)

| File/Page | Public-facing? | Issue | Severity | Recommended fix | Fix now |
|---|---|---|---|---|---|
| Release v0.4.0-beta.20 (pinned **Latest**) | Yes — highest traffic | Body names "Codex + Claude — Antigravity/Gemini failed in this run"; internal multi-model audit chatter | **P0** | Edit body: replace sentence with "a full independent page-by-page audit"; move Latest pin to the current accepted release | Yes |
| Release v0.4.0-beta.19 | Yes | Body names "Codex + Claude; Antigravity returned empty both runs" | **P1** | Same rewrite (draft in FABLE_RELEASE_COPY_REVIEW.md) | Yes |
| docs/TRUST_STATUS.md | Yes (linked from README + releases) | 15× "the maintainer"; "PENDING (manual acceptance)" acceptance chatter | **P1** | Replace with "manual installed-app acceptance pending"/"the maintainer"; keep the honest process, drop the personal name | Yes |
| Release v0.4.0-beta.21 | Yes — newest | No download/SHA256/verify section, no RELEASE_METADATA link | **P1** | Append standard verify section (draft provided) | Yes |
| Releases 20.1/20.2/20.3 | Yes | No SHA256 in body; 20.1 also missing the trademark/independence disclaimer block | P2 | Append verify section + disclaimer to 20.1 | Yes |
| Release flags | Yes | beta.10–19 unflagged, 20.x–21 Pre-release, beta.20 Latest — inconsistent | P2 | Make all 0.4.0 betas Pre-release; pin Latest to newest accepted build | Yes |
| Release v0.4.0-beta.18.1 | Yes | Body is a verbatim duplicate of beta.18 (17 min apart, no changelog) | P2 | Add one line stating what 18.1 actually changed | Yes |
| Releases 16.1 / 18.2 / 18.4 | Yes | Title vs body-H1 mismatches ("Safety Patch" vs "safety patch"; "Visual Proof Pass" vs "UX polish"; "Installed-App Readiness Verification" vs "Layout & Orca-Accurate Scale Fit") | P2 | Align titles/H1s | Optional |
| README screenshots (docs/screenshots/beta16/dashboard.png) | Yes | In-image marketing copy predates the truth sweep: "**Perfect prints** — … Doctors check every model", "Repair & standardize into a **clean** U1 project" — wording the product itself banned | P2 | Re-capture screenshots on beta.21 (also shows the new 5-item Simple nav — a win) | Yes (with acceptance pass) |
| Repo description | Yes | "Diagnose, transform, **validate**, and manage print files" — no U1/advisory scoping; `cli` topic borderline | P2 | Suggest: "Pre-print intelligence for the Snapmaker U1 — advisory checks, honest readiness, local-first. Prepares U1 profile copies for Snapmaker Orca." | Yes |
| docs/FABEL_*.md + docs/FABLE_*.md + docs/ORCA_CLI_SPIKE.md | Public repo, internal by nature | Contain model names, a maintainer's first name, internal process talk | P2 | Add a one-line "Internal engineering review — not user documentation" banner to each (FABLE_* docs already carry it); optionally move to docs/internal/ | Yes (banner) |
| docs/RELEASE_CHECKLIST.md:75–76 | Public repo, internal by nature | Lists internal review tool names | P2 | Reword to "external review tooling" or banner as internal | Yes |
| docs/brand/…/Gemini_Generated_Image_awl389….png | Yes (tracked asset) | Filename discloses AI generator of a brand asset | P2 | Rename file (content is fine) | Yes |
| CLAUDE.md | Public repo, internal by convention | Contains 1× maintainer name + agent-ops rules; NOT linked from README/docs as user docs (verified) | P3 | Acceptable as repo-internal instructions; do not link from marketing surfaces | No |
| Git history / commit messages | Yes | "Co-Authored-By" AI trailers | P3 | Standard practice for AI-assisted work; leave | No |
| README.md | Yes | Clean: no internal terms; "read-only" uses all correctly describe file analysis, not the printer; version block matches RELEASE_METADATA | — | none | — |
| docs/RELEASE_METADATA.md / SECURITY.md / JUDGE_OVERVIEW.md / WHAT_TO_TEST_FIRST.md / fund/* | Yes | Consistent post-20.4 state; fund docs carry HISTORICAL banners | — | none | — |

---

## 3. Security / privacy findings

| Finding | Severity | Evidence | Public exposure? | Fix |
|---|---|---|---|---|
| No secrets/API keys/tokens in tracked files | — | grep for token/key/Bearer shapes: 0 hits | n/a | none |
| No emails in tracked files | — | grep common mail domains: 0 hits | n/a | none |
| No private IPs | — | grep private/known ranges: 0 hits | n/a | none |
| No real local user paths | — | Only hit is synthetic test data (`orca.test.ts`: "C:/Users/secret/path.3mf") — clearly fake | Public but harmless | none |
| Screenshots contain no private data | — | Manual review of README-linked PNGs: generic sample files ("cube_U1.3mf"), public site content, no IPs/usernames | Public, clean | none |
| Personal name in trust docs | P1 | TRUST_STATUS.md 15× maintainer first name | Yes | Replace with role wording |
| "force-kill" occurrences | P3 | All legitimate technical uses (orphan-process guarantees in ARCHITECTURE/main.rs/server.py); incident anecdotes live only in internal review docs | Low | none |
| 3MF zip handling / CSP / CORS / loopback claims | — | SECURITY.md matches code (in-memory container + pinning test; CSP present in tauri.conf.json); consistent since 20.4 | Accurate | none |
| Release assets | — | One `.exe` per release, consistent naming, API-level sha256 digests present | Clean | add in-body hashes (above) |

---

## 4. beta.21 readiness recommendation

beta.21's own body and the README are professional and truth-consistent; nothing
found requires an app patch. Before promoting beta.21 anywhere judge-visible:

1. **P0/P1 release-page cleanup** (edit beta.19 + beta.20 bodies, fix the Latest
   pin, add verify sections to 20.1–21) — drafts ready in FABLE_RELEASE_COPY_REVIEW.md.
2. **TRUST_STATUS de-personalization** ("manual installed-app acceptance pending").
3. **Screenshot refresh on beta.21** (kills the "Perfect prints"/"clean" in-image
   claims and shows the new novice IA).
4. Then run the beta.21 GUI acceptance checklist and flip trust status if green.

Order of operations matters: do 1–2 (30 minutes of edits) before sharing any links.
