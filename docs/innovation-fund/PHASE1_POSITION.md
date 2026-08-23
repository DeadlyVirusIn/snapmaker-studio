# Phase 1 competitive position — where Studio actually stands

Assessed **2026-08-23**, against the live project wall at
<https://www.snapmaker.com/innovation-fund>. Every number below was read from the
GitHub API on that date, not carried over from the earlier competitor matrix.

## The state this document starts from

Snapmaker Studio is **submitted, confirmed, and publicly listed** — entry sent
24 June 2026, confirmed 29 June, listed as *"snapmaker-studio — by Kunal
Khurana"*. There is nothing left to enter. See
[SUBMITTED_ENTRY.md](SUBMITTED_ENTRY.md).

| | |
|---|---|
| Projects in the running | **41** |
| Winners | **20** — 3 × $5,000, 7 × $3,000, 10 × $1,500 |
| Evaluation closes | **22 September 2026** |
| Winners announced | 30 September 2026 |
| Weighting | 80% Technical Committee · 20% community vote |
| Community vote | Not live yet — the fund's page says the voting system is still being built |

Roughly one entry in two wins something. This is not a long shot; it is a field
where being unremarkable is the main way to lose.

## The field, grouped by what these projects actually do

| Group | Entries | Studio overlap |
|---|---|---|
| **Colour / texture generation** — Lumina-Layers, Kromacut, ditherforge, PrintProof, Bird3D, OrcaFS-NeotkoCM, Lumina | 7 | none |
| **Converters** — makerworld-to-snapmaker-u1, bambu-to-snapmaker-u1, Bambu & Snapmaker U1, btu, Nozzle Buddy | 5 | **direct, and crowded** |
| **Slicer forks / slicer UI** — FOrcaSlicer, Snapmaker-Orca multi-nozzle, OrcaSlicer FS UI rework, orcaslicer-imagemap, u1-slicer-for-android | 5 | none — Studio does not slice |
| **Dashboards / senders / fleet** — u1hub, snapmaker-u1-toolkit, SnapCon, Helix, PrinterTools, Foreman 5 | 6 | partial — Printer Hub, but Studio asks a different question |
| **CAD / modelling** — sindricad, snaporca-cad, BREPcode, Meshivo, PolyCarver, Miniskyline | 6 | none |
| **Hardware** — Sidecar 16-Color MMU, QCMS, multiACE, AFC-Klipper-Add-On, Driver Heatsink, P1S/X1 Hotend, pandabreath | 7 | none |
| **Firmware / platform** — SnapmakerU1 Extended Firmware, bespok3d, U1 Adaptive Pressure Advance | 3 | none |
| **Planning / verification** — Adaptive Manufacturing Planner, **Snapmaker Studio** | 2 | this is the lane |

**The lane is still uncontested.** Searching GitHub for pre-print validation,
3MF validation for the U1, or a Moonraker-based readiness check returns nothing in
this field. No other entry compares a project against the machine it will print
on. The one conceptual neighbour, Adaptive Manufacturing Planner, describes phase
one as software-level fuse width and contour verification, and has no findable
public repository — it is early.

**But conversion is not a differentiator.** Five entries convert files. If a judge
reads Studio as "another converter", it loses to five better-known ones. The June
submission text opens with pre-print failure but the wall description reduces it
to a checker, which is close to that failure mode.

## Community traction, measured today

| Project | Stars | Forks | Open issues | Licence | Last push |
|---|---:|---:|---:|---|---|
| Lumina-Layers | 995 | 141 | 21 | GPL-3.0 | 2026-08-02 |
| SnapmakerU1 Extended Firmware | 934 | 111 | 83 | GPL-3.0 | 2026-08-23 |
| Kromacut | 257 | 29 | 28 | AGPL-3.0 | 2026-08-22 |
| AFC-Klipper-Add-On | 252 | 97 | 93 | GPL-3.0 | 2026-08-21 |
| sindricad | 143 | 13 | 5 | AGPL-3.0 | 2026-08-22 |
| bl2u1 | 67 | 15 | 4 | GPL-3.0 | 2026-04-07 |
| u1-slicer-for-android | 53 | 7 | 27 | AGPL-3.0 | 2026-08-18 |
| u1hub | 51 | 3 | 1 | MIT | 2026-08-17 |
| ditherforge | 28 | 2 | 0 | MIT | 2026-07-30 |
| bespok3d | 25 | 1 | 1 | AGPL-3.0 | 2026-08-22 |
| makerworld-to-snapmaker-u1 | 21 | 2 | 1 | MIT | 2026-08-06 |
| FOrcaSlicer | 19 | 1 | 4 | AGPL-3.0 | 2026-08-14 |
| snapmaker-u1-toolkit | 17 | 0 | 2 | MIT | 2026-07-30 |
| bambu-to-snapmaker-u1 | 15 | 4 | 11 | — | 2026-08-10 |
| **snapmaker-studio** | **1** | **0** | **0** | MIT | 2026-08-23 |

Studio is **last in the field on every community measure I could find a repository
for.** The median entry here has ~25 stars; the leaders have hundreds. More
telling than stars: the strong projects have *open issues* — 21, 83, 93. Issues
mean users. Studio has had none, ever.

A second finding, and a fixable one: as of this morning the repository did not
appear in GitHub's top 30 results for "snapmaker", and its description still read
*"The workflow platform for modern 3D printing"* — the pre-pivot positioning. A
judge clicking "View on GitHub" from the wall landed on a description of a
different product from the README's.

## If the committee picked 20 today, where does Studio fall?

**Borderline. It makes the 20 only if a judge actually opens the repository.**

The case for, on the committee's own criteria:

- *Innovation & Technical Depth* — **top quartile.** Nothing else in the field
  attempts correctness under missing information: evidence grading, the
  project-to-printer join, an audit that can refuse its own claim, a feature
  withdrawn because its arithmetic could not be justified. Most entries are
  competent implementations of an obvious idea. This one has a thesis.
- *Openness & Quality* — **top quartile.** MIT in a GPL-heavy field, a data-file
  extension seam, a documented CLI and local API, and — uniquely, as far as I can
  tell — verification that runs against the *published installer* and against real
  hardware, reproducible by anyone with two commands.
- *Practicality & Adaptability* — **middle.** The problems Studio solves are real
  but abstract. "Turn a photo into a colour print" and "16 colours on a U1" are
  instantly graspable; "compares your project against your printer's reported
  capabilities" needs a paragraph.
- *Community (20%)* — **bottom.** Last in the field. There is no way to fix this
  honestly in four weeks, and the voting system is not even live.

Realistic outcome: **Active Builder tier ($1,500) is achievable; Eco-Enhancer
($3,000) is possible on technical merit; U1 Pioneer ($5,000) is not.** The three
top prizes will go to projects with both depth and visible impact — Extended
Firmware, Lumina-Layers, AFC-class work. Studio cannot out-traction them and
should not try.

The decisive variable is **whether the committee reads past the wall card.**

## The five real risks, ranked

Ranked by expected effect on the final score, with the criterion each hits.

### 1. External listing weakness — the wall describes a June product
**Hits: all three technical criteria.**
The listing text and the cover image both come from the 24 June entry. They
describe understand/validate/prepare/monitor and a workflow platform. Everything
Studio is now strongest on — the project-to-printer preflight, the fidelity audit,
the fix ledger, colour planning, the ecosystem recommender, the installed-build
acceptance harness, the read-only real-U1 verification — postdates it. A committee
scoring the card scores a two-month-old product. This is the highest-leverage item
because it is pure signal loss, not a product gap.

### 2. Community weakness — one star, zero issues, last in the field
**Hits: Community (20%), and Practicality by implication.**
Nothing suggests anyone has used Studio and had a good outcome. Downloads exist
(43) and clones exist (57 unique in a fortnight), but no engagement of any kind. A
committee that reads traction as evidence of usefulness will mark this down, and
they would not be wrong to. Four weeks cannot manufacture a community, and the
attempt would be worse than the gap.

### 3. Presentation weakness — the hardest project in the field to explain
**Hits: Practicality & Adaptability, and Innovation by omission.**
Every other entry has a one-sentence pitch a maker instantly pictures. Studio's
value is conditional, structural, and about *not* claiming things. That is
genuinely harder to convey, and skim-reading judges will get it wrong more often
than they get it right. The 71-second demo and the judge overview exist precisely
for this, but the demo is not linked from anywhere Snapmaker controls.

### 4. Evidence weakness that was publicly visible — CI red on main
**Hits: Openness & Quality.**
The public Actions tab showed a failing build on the head of `main`, and had for
every commit since the job was added: Tauri's build script refuses to run when the
frozen sidecar is absent, and CI does not freeze it. For a project whose entire
argument is "verify it yourself", a red X is self-refuting — and worse, an earlier
trust record claimed the check was "now enforced in CI" when it had never passed.
Fixed on 2026-08-23; the false claim is corrected in
[../TRUST_STATUS.md](../TRUST_STATUS.md).

### 5. Product weakness — conversion is table stakes, and the depth is invisible from outside
**Hits: Innovation & Technical Depth.**
Five entries convert files. Studio's conversion is not a differentiator and should
not be presented as one. The genuinely novel work — refusal under uncertainty,
graded evidence, an audit that can fail — is *internal*, and a judge cannot see it
without reading tests or running the app. This is not a missing feature; it is a
legibility problem for real work.

Deliberately **not** on this list: features. Studio does not need more surface
area before 22 September, and adding some would make risks 3 and 5 worse.
