# Ecosystem outreach — the notes that were posted

Studio's registry names other people's projects and explains to users when those
projects are the right tool. Those maintainers do not know that, and they are the
people best placed to correct how Studio describes them.

These are the notes sent for that purpose, kept here verbatim so the wording is
auditable.

## Status — posted 2026-08-23

Each repository's ability to receive a note was re-checked through the GitHub API
immediately before posting, and each note was tailored to that project.

| Project | Posted | Reply |
|---|---|---|
| FOrcaSlicer | [jiyang1018/FOrcaSlicer#11](https://github.com/jiyang1018/FOrcaSlicer/issues/11) | — |
| U1 Print Hub | [dlgambill/u1hub#2](https://github.com/dlgambill/u1hub/issues/2) | — |
| MakerWorld to Snapmaker U1 | [Dragon2203/makerworld-to-snapmaker-u1#2](https://github.com/Dragon2203/makerworld-to-snapmaker-u1/issues/2) | — |
| Snapmaker U1 Toolkit | [bbolinger/snapmaker-u1-toolkit#33](https://github.com/bbolinger/snapmaker-u1-toolkit/issues/33) | — |
| OrcaSlicer ImageMap | **not posted** — issues are disabled on that repository | n/a |

ImageMap is deliberately skipped. There is no channel, and routing around a
maintainer who has closed one would be exactly the behaviour these rules forbid.
If its entry is wrong, it stays wrong until they open a channel or contact the
project.

Each note says the same thing: here is how Studio describes your project, here is
the exact rule that triggers it, correct it or ask to be removed. None asks for a
star, a vote, an endorsement or a link back. The "Reply" column is filled in if
and when a maintainer responds.

## Rules these follow, and must keep following

- **No promotion.** Each note exists to say "here is how your project is
  described, correct it if it is wrong" — not to advertise Studio.
- **No claimed endorsement.** Studio names these tools; none of them has endorsed
  Studio, and nothing here implies otherwise.
- **One note per project, once.** Repeating is spam.
- **Correct or delete on request.** If a maintainer would rather not be listed,
  remove the entry from the registry. That is a one-line change.
- **Nothing is posted automatically.** No tooling in this repository posts to
  anyone's issue tracker.

Registry entries live in `backend/snapstudio_core/data/ecosystem.json`; the schema
and contribution rules are in [../EXTENDING.md](../EXTENDING.md).

---

## FOrcaSlicer — `jiyang1018/FOrcaSlicer`

Posted as [issue #11](https://github.com/jiyang1018/FOrcaSlicer/issues/11), titled
*"How Snapmaker Studio describes FOrcaSlicer (correction welcome)"*.

> Hi — I maintain Snapmaker Studio, an MIT-licensed local tool that reads a 3MF
> and explains what it needs before slicing. It has a small registry of
> open-source tools and suggests one when a project's contents call for it.
>
> When Studio reads more than one nozzle diameter in a project it names
> FOrcaSlicer, with this reason shown to the user:
>
> > This project already uses more than one nozzle size, which is exactly what
> > this fork is built for.
>
> It also shows your licence (AGPL-3.0) and, because the README describes the
> project as a research preview, a caution to review output before a long print.
> Studio never installs anything and never launches a tool on its own, and no code
> or data from this project is used.
>
> I am opening this so the description is yours to correct rather than mine to
> guess at. If anything above is wrong or out of date, the entry is a single JSON
> object in `backend/snapstudio_core/data/ecosystem.json` — a PR is welcome, and so
> is "please remove it", which is a one-line change.

## U1 Print Hub — `dlgambill/u1hub`

Posted as [issue #2](https://github.com/dlgambill/u1hub/issues/2), titled *"How
Snapmaker Studio describes U1 Print Hub (correction welcome)"*.

> Hi — Snapmaker Studio is an MIT-licensed local pre-print checker for the U1. It
> stops where the Hub starts, and says so: when a project already contains
> toolpaths, Studio names U1 Print Hub with the reason
>
> > This project is already sliced, so the next step is getting it onto a printer
> > rather than back into a slicer.
>
> Your README's protocol notes were genuinely useful while building Studio's
> read-only Printer Hub — in particular that the U1 answers Moonraker on port 80
> as well as 7125. Studio now probes both, which fixed real "printer not found"
> reports. No code from this project is used.
>
> I am opening this so you can correct how your project is described rather than
> find out later. If the description or the trigger is wrong, the entry is a single
> JSON object in `backend/snapstudio_core/data/ecosystem.json` — a PR is welcome,
> and removal is a one-line change if you would rather not be listed.

## MakerWorld to Snapmaker U1 — `Dragon2203/makerworld-to-snapmaker-u1`

Posted as [issue #2](https://github.com/Dragon2203/makerworld-to-snapmaker-u1/issues/2),
titled *"How Snapmaker Studio describes this extension (correction welcome)"*.

> Hi — Snapmaker Studio is an MIT-licensed desktop pre-print checker for the U1.
> When it opens a project that looks like a MakerWorld download authored for
> another printer, it names this extension with the reason
>
> > This looks like a MakerWorld download authored for another printer. Converting
> > it in the browser next time keeps the creator's profile intact from the start.
>
> The registry entry records your licence as MIT, and carries this note: your own
> notices state that some conversion logic and reference data derive from a
> PolyForm-Noncommercial project. Studio implements several of the same
> compatibility corrections in its own engine, written independently from the
> published symptoms and the 3MF schema — it uses no code, profile data or
> reference data from this project. If you think anything in Studio's engine reads
> as derived rather than independent, tell me and I will change it.
>
> I am opening this so the description is yours to correct. Corrections to the
> registry entry are a one-object PR against
> `backend/snapstudio_core/data/ecosystem.json`, and removal is a one-line change.

## Snapmaker U1 Toolkit — `bbolinger/snapmaker-u1-toolkit`

Posted as [issue #33](https://github.com/bbolinger/snapmaker-u1-toolkit/issues/33),
titled *"How Snapmaker Studio describes the Toolkit (correction welcome)"*.

> Hi — Snapmaker Studio is an MIT-licensed local pre-print checker for the U1.
> When a project already contains toolpaths, Studio names the Toolkit as one way
> to send it to the printer without opening a slicer again, alongside your own
> caution that it is command-line and young.
>
> Studio holds the same line your README does: it can prepare, explain and
> preview, but it never starts a print on its own — every printer action sits
> behind an explicit confirmation. No code from this project is used.
>
> I am opening this so you can correct how your project is described rather than
> find out later. The entry is a single JSON object in
> `backend/snapstudio_core/data/ecosystem.json` — a PR is welcome, and removal is a
> one-line change if you would rather not be listed.

## OrcaSlicer ImageMap — `sentientstardust-dev/OrcaSlicer-ImageMap`

**Not posted.** Issues are disabled on that repository. The note that would have
been sent is kept here so the entry's description is still auditable:

> Snapmaker Studio (MIT, local-only) reads a 3MF before slicing and suggests the
> tool that fits what it found. When it finds texture parts in a project it names
> ImageMap, with this reason:
>
> > This model carries image-texture data, which most slicers throw away and this
> > fork can actually print.
>
> It shows AGPL-3.0 and a beta caution taken from the project's own README.
> Nothing is installed or launched by Studio.

## Snapmaker Orca — `Snapmaker/OrcaSlicer`

Not an outreach target. Studio's relationship to the official slicer is a
one-way handoff that is a hard rule in the codebase: Studio prepares a file and
launches the verified executable with it, and does not slice, control Orca, or
read its source. Worth raising only if Snapmaker asks how Studio interoperates.

---

## If someone asks "why should I care?"

The honest answer: Studio makes it possible for a beginner to find these projects
at the moment they would actually help, instead of having to know all of them
first. Studio gets a better answer for its users, and those projects get reached
by people who need them. That is the whole trade, and it does not require anyone
to endorse anything.
