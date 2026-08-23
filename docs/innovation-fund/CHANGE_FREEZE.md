# Change freeze — 2026-08-23 until Phase 1 evaluation closes

beta.24 is the build being judged. From today, **no runtime change lands because
it is interesting.** A stable build accumulating real-world evidence is worth more
than beta.25, .26 and .27 shipped into silence.

## What still gets in

A change needs to fit one of these, and the commit message must say which.

| Gate | Meaning |
|---|---|
| **P0** | Data loss or corruption, a dangerous action, or a failure of a trust claim — Studio asserting something false about a file or a printer, or modifying an original |
| **P1** | A common workflow is broken: the app will not start, a project will not open, preparing a copy fails |
| **P1 Evidence** | A claim made to a judge, in the demo, or in the reproducibility docs is shown to be false. Fixing the claim counts; so does fixing the code behind it |
| **User-driven** | A real tester reports a meaningful failure. This is the gate we most want to use, and the one that has never yet fired |

Everything else is deferred to the post-Phase-1 backlog in
[NEXT_MOVES.md](NEXT_MOVES.md).

## What is explicitly deferred

Painted-colour enumeration · a second printer · OBJ/GLB input · a plugin framework
· any additional Doctor · macOS and Linux builds · diagnostic packs as data ·
cost-from-sliced-project · the reproducibility manifest · code signing.

**Code signing is deferred deliberately.** It is prepared to the last legal step
and it remains useful, but it will not land inside the evaluation window and it
does not affect judging. It is not the next action and should not be treated as
one.

## Releases

**Do not cut beta.25 unless a P0 or P1 forces it.** If one does:

- fix only that,
- re-run the installed-build acceptance harness and the read-only hardware
  verification against the new installer,
- update `RELEASE_METADATA.md`, `TRUST_STATUS.md` and the changelog in the same
  commit as the release,
- and leave the demo alone unless the fix changes what the demo shows.

Documentation, evidence and presentation changes are **not** frozen. Those are the
work of this period.

## Priorities for the remaining window

1. Official listing accuracy — the card the committee reads
2. Community visibility — the project has never been posted about
3. External feedback — one real report is worth more than any feature
4. Judge comprehension — the first screen, the demo, the walkthrough
5. Reliability fixes that arise from 3

## How to tell this freeze is working

The repository should show, at the end of the window: few or no runtime commits,
several evidence and documentation commits, and — if the community work lands —
at least one issue opened by somebody other than the author.
