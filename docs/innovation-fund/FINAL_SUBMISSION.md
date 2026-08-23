# Final submission package — Snapmaker Innovation Fund, Phase 1

**Status: ready to send. Not sent.** The form asks for the maintainer's name and
email and represents them personally.

Prepared 2026-08-23, against the fund's rules as published on that date
(<https://www.snapmaker.com/innovation-fund>). Phase 1 closes **7 September 2026**.

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

---

## 1. What goes in the form

| Field | Value |
|---|---|
| Project name | Snapmaker Studio |
| Project URL | <https://github.com/DeadlyVirusIn/snapmaker-studio> |
| Category | Workflow / software tooling |
| Licence | MIT |
| Cover image (optional, 640×360, ≤5 MB) | Export `docs/brand/hero.svg` at 640×360, or use `docs/media/demo-poster.jpg` |
| Name, email | The maintainer's own |

**Short description (~40 words):**

> Snapmaker Studio is a free, local-first desktop app that reads a downloaded 3D
> project, explains the risks in plain language, compares it against your actual
> U1 over Moonraker, fixes only what it can justify, and proves what survived.
> Snapmaker Orca still slices.

The long description is in [../INNOVATION_FUND.md](../INNOVATION_FUND.md) and is
the canonical text. Do not rewrite it in the form; paste it.

## 2. The other two entry requirements

The form is one of three. All three are required.

1. **Published on GitHub or another public page** — done:
   <https://github.com/DeadlyVirusIn/snapmaker-studio>, with a published release,
   a demo, and a verification record.
2. **Shared in a Snapmaker community channel** — **outstanding.** This is a stated
   requirement and it is also the only honest route into the 20% community
   component. It carries the maintainer's name, so it is theirs to post.
3. **Submitted through the fund's online form** — **outstanding**, for the reason
   above.

## 3. What is being submitted

**Release:** [v0.4.0-beta.24](https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.4.0-beta.24)
— the first build verified against a real Snapmaker U1. Installer name, size and
SHA256: [../RELEASE_METADATA.md](../RELEASE_METADATA.md). Verification record:
[../TRUST_STATUS.md](../TRUST_STATUS.md).

**Demo:** [`docs/media/snapmaker-studio-demo.mp4`](../media/snapmaker-studio-demo.mp4)
— 71 seconds, every frame the installed application.

## 4. How the package maps to the three judged criteria

The committee scores 80% on Innovation & Technical Depth, Openness & Quality, and
Practicality & Adaptability. The remaining 20% is a community vote.

| Criterion | Read this | The one-line case |
|---|---|---|
| Innovation & Technical Depth | [TECHNICAL_DEPTH.md](TECHNICAL_DEPTH.md) | Being correct when the file or the printer does not expose enough information to be certain — evidence grading, a project-to-printer join, a preservation invariant, a fidelity audit that can fail, deterministic colour classification, and a feature withdrawn because its maths could not be justified |
| Openness & Quality | [OPEN_ECOSYSTEM.md](OPEN_ECOSYSTEM.md) | MIT, local-first, no account or telemetry, documented CLI and local API, a data-file ecosystem registry anyone can extend by pull request, and every claim reproducible by one command |
| Practicality & Adaptability | [JUDGE_OVERVIEW.md](JUDGE_OVERVIEW.md) | Seven concrete novice dead-ends, each with what Studio actually does — and a printer layer that speaks Moonraker rather than anything U1-specific |
| Community (20%) | [USER_EVIDENCE.md](USER_EVIDENCE.md) | Thin and honestly reported: interest is measured, outcome is empty, and nothing is inflated to cover the gap |

## 5. Evidence, in one table

Verified against the published beta.24 installer, not a development build.

| What | Result |
|---|---|
| Installed-application acceptance, through the real UI | 21/21 |
| Read-only verification against a real Snapmaker U1 | 13/13 |
| Regression tests against genuine Orca/Bambu/Prusa projects | 34 tests |
| End-to-end pipeline self-check | 15/15 |
| Backend tests | 663 passed, 3 skipped |
| Desktop tests | 247 passed across 31 files |
| TypeScript · production build · Rust | clean |

Reproduce any of it: [JUDGE_WALKTHROUGH.md](JUDGE_WALKTHROUGH.md).

## 6. The claims this package will not make

Stated here so they cannot creep back in under deadline pressure:

- **No print-success guarantee.** Every check is advisory.
- **No "nothing was lost"** unless the fidelity audit granted that claim for that
  specific project.
- **No endorsement.** Snapmaker has not endorsed this project, and neither has any
  of the community projects Studio names.
- **No fabricated adoption.** There are no testimonials because there are no
  testimonials.
- **No signed-installer claim** until an installer is actually signed.
- **The 112-file corpus is not headline evidence.** It measures structure, not
  print success, and it is dominated by STLs. It stays as historical context.

## 7. Sequence for the maintainer

1. Confirm MFA is enabled on the GitHub account.
2. Share the project in a Snapmaker community channel (entry requirement).
3. Submit the form at <https://www.snapmaker.com/innovation-fund>, pasting the
   short and long descriptions from [../INNOVATION_FUND.md](../INNOVATION_FUND.md).
   There is no documented way to revise a submission, so send it once.
4. Separately, apply to SignPath Foundation at <https://signpath.org/apply> —
   everything it asks for is prepared in
   [../CODE_SIGNING_POLICY.md](../CODE_SIGNING_POLICY.md).

## 8. Package contents

| File | What it is |
|---|---|
| [../INNOVATION_FUND.md](../INNOVATION_FUND.md) | The submission text itself, plus the fund's current rules |
| [JUDGE_OVERVIEW.md](JUDGE_OVERVIEW.md) | Five-minute orientation for a judge |
| [JUDGE_WALKTHROUGH.md](JUDGE_WALKTHROUGH.md) | Reproduce every claim yourself |
| [DEMO_SCRIPT_90_SECONDS.md](DEMO_SCRIPT_90_SECONDS.md) | The recorded demo, beat by beat |
| [TECHNICAL_DEPTH.md](TECHNICAL_DEPTH.md) | The engineering case |
| [OPEN_ECOSYSTEM.md](OPEN_ECOSYSTEM.md) | Licence wall, registry, interoperability |
| [COMPETITOR_MATRIX.md](COMPETITOR_MATRIX.md) | The measured field |
| [DIFFERENTIATION_STRATEGY.md](DIFFERENTIATION_STRATEGY.md) | Why this position holds |
| [USER_EVIDENCE.md](USER_EVIDENCE.md) | Measured community signal, interest separated from outcome |
| [ECOSYSTEM_OUTREACH.md](ECOSYSTEM_OUTREACH.md) | The notes sent to other maintainers, verbatim, with URLs |
| [NEXT_MOVES.md](NEXT_MOVES.md) | What is left, ranked, weaknesses first |
| [CHANGE_SUMMARY.md](CHANGE_SUMMARY.md) | What changed and why, across the sprints |
