# Ecosystem outreach — factual notes, ready to post

Studio's registry names other people's projects and explains to users when those
projects are the right tool. Those maintainers do not know that, and they are the
people best placed to correct how Studio describes them.

These are short, factual notes for that purpose. They are **drafts for a human to
post**, from their own account, when they judge it appropriate.

## Status — checked 2026-08-23, not posted

Whether each repository can receive a note was checked through the GitHub API:

| Project | Issues | Note |
|---|---|---|
| FOrcaSlicer | enabled (discussions too) | A discussion is the better fit than an issue |
| U1 Print Hub | enabled | |
| MakerWorld to Snapmaker U1 | enabled | |
| Snapmaker U1 Toolkit | enabled | |
| OrcaSlicer ImageMap | **disabled** | Do not post. There is no channel, and finding another route round that would be exactly the behaviour these rules forbid |

The four reachable repositories have between zero and three open issues each,
which means an unsolicited note would be highly visible and would set the tone for
a first contact with that maintainer.

These drafts are therefore left unposted. Not because it is technically
impossible — the tooling and the authenticated account are both there — but
because outreach carries the maintainer's name and reputation, and the judgement
of when and in what tone to introduce yourself to a peer is theirs. Everything up
to that point is done: the text is written, the recipients are verified, and the
one repository that must be skipped is identified.

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

> **Subject:** Snapmaker Studio points users here when a project uses mixed nozzle sizes
>
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
> Studio never installs anything and never launches a tool on its own.
>
> If any of that is wrong or out of date, the entry is one JSON object —
> a PR against `backend/snapstudio_core/data/ecosystem.json` is welcome, and so is
> "please remove it".

## OrcaSlicer ImageMap — `sentientstardust-dev/OrcaSlicer-ImageMap`

> **Subject:** Studio points users here when a model carries texture data
>
> Hi — Snapmaker Studio (MIT, local-only) reads a 3MF before slicing and suggests
> the tool that fits what it found. When it finds texture parts in a project it
> names ImageMap, with this reason:
>
> > This model carries image-texture data, which most slicers throw away and this
> > fork can actually print.
>
> It shows AGPL-3.0 and a beta caution taken from your own README. Nothing is
> installed or launched by Studio.
>
> Corrections welcome as a one-object PR against
> `backend/snapstudio_core/data/ecosystem.json`, including removal if you prefer.

## U1 Print Hub — `dlgambill/u1hub`

> **Subject:** Studio sends users to the Hub once a project is sliced
>
> Hi — Snapmaker Studio is a local pre-print checker for the U1. It stops where
> the Hub starts, and says so: when a project already contains toolpaths, Studio
> names U1 Print Hub with the reason
>
> > This project is already sliced, so the next step is getting it onto a printer
> > rather than back into a slicer.
>
> Your README's protocol notes were genuinely useful while building Studio's
> read-only Printer Hub — in particular that the U1 answers Moonraker on port 80
> as well as 7125. Studio now probes both, which fixed real "printer not found"
> reports.
>
> If the description or the trigger is wrong, a PR against
> `backend/snapstudio_core/data/ecosystem.json` is the whole change.

## MakerWorld to Snapmaker U1 — `Dragon2203/makerworld-to-snapmaker-u1`

> **Subject:** How Snapmaker Studio describes this extension
>
> Hi — Snapmaker Studio is a desktop pre-print checker for the U1. When it opens a
> project that looks like a MakerWorld download authored for another printer, it
> names this extension with the reason
>
> > Converting in the browser next time keeps the creator's profile intact from
> > the start.
>
> Studio implements several of the same compatibility corrections in its own
> engine, written independently from the published symptoms and the 3MF schema —
> no code or profile data from this project is used, because of the PolyForm
> notices. If you think anything in Studio's engine reads as derived rather than
> independent, tell me and I will change it.
>
> Corrections to the registry entry are a one-object PR.

## Snapmaker U1 Toolkit — `bbolinger/snapmaker-u1-toolkit`

> **Subject:** Studio lists the Toolkit, and shares its stance on print starts
>
> Hi — Snapmaker Studio is an MIT local pre-print checker for the U1. When a
> project already contains toolpaths, Studio names the Toolkit as one way to send
> it to the printer without opening a slicer again, alongside your own caution
> that it is command-line and young.
>
> Studio holds the same line your README does: it can prepare, explain and
> preview, but it never starts a print on its own — every printer action is behind
> an explicit confirmation.
>
> If the description is wrong, the registry entry is one JSON object and a PR is
> welcome.

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
