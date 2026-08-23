# User evidence

**Gathered 2026-08-23**, refreshed immediately before the beta.24 release, from the GitHub API against the repository itself. Every
number here is a measurement, not an estimate. Nothing on this page is a
testimonial, because there are no testimonials to report.

The previous report said "zero customer evidence". That was too strong. It is
closer to *thin, real, and anonymous*.

## What is measured

| Signal | Value | Source |
|---|---|---|
| Installer downloads, all releases | **43** | `repos/…/releases` asset download counts |
| Unique cloners, last 14 days | **57** (75 clones) | `repos/…/traffic/clones` |
| Unique visitors, last 14 days | **11** (15 views) | `repos/…/traffic/views` |
| Stars | 1 | repository metadata |
| Forks | 0 | repository metadata |
| Watchers | 0 | repository metadata |
| Issues opened, ever | 0 | repository metadata |
| Repository age | Created 2026-06-17 | repository metadata |

Downloads by release, highest first: beta.20.4 — 10, beta.20.2 — 6, beta.20 — 5,
others 0–3 each, across 39 published releases. beta.22, beta.23 and beta.24 were
published within a day of this measurement and have none yet.

## What that does and does not support

**It supports:** people have downloaded Studio's installer 43 times, and 57
distinct machines cloned the repository in a fortnight. That is not nothing, and
it is more than a project with one star would suggest.

**It does not support:** any claim about whether those installs helped anyone.
Nobody has opened an issue, starred the project, or written about it. There is no
feedback channel with anything in it. Downloads are not usage and usage is not
value, and this page will not pretend otherwise.

**The honest summary:** there is evidence of *interest* and no evidence of
*outcome*.

## Where feedback could now come from

Until 2026-08-23 there was no channel with anything in it. Four factual notes have
since been posted to the maintainers of projects Studio names, asking them to
correct how their work is described — see
[ECOSYSTEM_OUTREACH.md](ECOSYSTEM_OUTREACH.md) for the exact posts. Any reply is
the project's first external feedback of any kind, and will be recorded here as
what it is: a maintainer's correction, not a user outcome.

## The underlying problems, separately

The problems Studio addresses are evidenced independently of Studio, in the
projects that exist to solve neighbouring parts of them — see
[COMPETITOR_MATRIX.md](COMPETITOR_MATRIX.md), compiled from those projects' own
documentation:

- **Foreign projects need compatibility corrections.** Five separate
  Bambu/MakerWorld→U1 converters exist in the Phase 1 field. Nobody builds five
  converters for a problem nobody has. Each documents specific settings that must
  be corrected — exclude-object, brim, tree support with variable layer height —
  which is a published record of what goes wrong.
- **The printer's network interface is not discoverable by default.** Multiple
  independent guides document that the U1's web interface requires Advanced Mode
  on the touchscreen first. Studio's "printer not found" message says that
  because of it.
- **The U1 answers Moonraker on port 80 as well as 7125.** Documented by U1 Print
  Hub. Studio probed only 7125 until this was found, which would have made a
  reachable printer look offline.

That is evidence the *problems* are real. It is not evidence that Studio's
*answers* have helped a named person, and the two should not be conflated.

## What would change this page

An issue, a forum post, or a message from someone who used it. The most credible
route is the demo recording and the ecosystem notes — see
[NEXT_MOVES.md](NEXT_MOVES.md) — not asking for stars.

## Method

```bash
gh api repos/DeadlyVirusIn/snapmaker-studio --jq '{stars,forks,watchers,issues}'
gh api repos/DeadlyVirusIn/snapmaker-studio/releases \
  --jq '[.[].assets[].download_count] | add'
gh api repos/DeadlyVirusIn/snapmaker-studio/traffic/clones
gh api repos/DeadlyVirusIn/snapmaker-studio/traffic/views
```

Traffic endpoints require push access and only cover 14 days, so those two
figures are a window rather than a total.
