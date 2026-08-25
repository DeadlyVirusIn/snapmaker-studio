# Do I have enough filament to finish this print?

> **State:** this describes `main` after v0.7.2. The published installer, v0.7.2,
> does not contain the settings page described here. Not a release announcement.

A printer knows which spool is in which slot, because it is looking at it. It
knows nothing at all about how much filament is left on that spool. So the
question people actually ask before pressing print is one no printer can answer,
and Studio said "unknown" to it on every setup.

Something on your network may know. Spoolman tracks spools and what has been used
from them, and Studio can read it — read-only, over your own network, optional.

## Setting it up

**Settings → Materials provider.**

1. Choose **Spoolman**.
2. Type the address of the machine it runs on: `spoolman.local:7912`, or its IP.
3. Press **Test connection**.
4. Say which numbering your slots use — 1 to 4, or 0 to 3 — and then which spool
   is in which slot.

That is all of it. No account, no cloud, and Studio does not scan your network
looking for anything.

### Why it asks about slot numbering

A person counts the slots on a printer 1, 2, 3, 4. G-code counts them 0, 1, 2, 3.
Guess wrong and every spool is one slot out, and Studio then reports the wrong
material for every slot with complete confidence — which is worse than not
knowing. So it asks instead of guessing.

### What "Test connection" tells you

Two numbers, because they are genuinely different:

- how many spools Spoolman has;
- how many of those carry a weight **Spoolman is actually keeping track of**.

Spoolman reports what a spool started with until something prints from it. A shelf
of spools you have just registered will all report a full kilogram, and that is a
declared size rather than a measurement. Studio treats those as estimates, and
says so, rather than letting a number that has never been updated stop you
printing.

## What Studio will and will not say

| What it knows | What it says |
|---|---|
| A tracked weight, updated recently, and the job needs more | **Not enough** — this blocks the send |
| A tracked weight, updated recently, and enough for the job | Enough, with the figure and its age |
| A tracked weight nobody has updated in over a week | A warning, with how old it is. Never a refusal |
| A weight worked out from the spool's declared size | A warning. It is arithmetic, not a record |
| A weight with no date at all | A warning. Nothing says it is still true |
| Nothing tracking the spool | **Unknown** — go and look at it |
| The provider is unreachable | **Unknown**. Not "enough", and not "empty" |

A blocker is the strongest thing Studio says, so it has to be earned: only a
figure something is genuinely keeping, recent enough to still be true, can stop a
send. Everything else warns. The reason is not caution for its own sake — a
person refused a print over bookkeeping learns to ignore the refusals, and the
next one might be right.

Past a week, a figure warns and can never be the sole reason a send is refused.

## The printer and the provider disagreeing

The printer is authoritative about **what is physically in the slot**, because it
can see it. A provider adds what the machine cannot know: which spool this is, and
how much is on it.

When they disagree, Studio shows the disagreement and keeps the printer's answer:

> Printer reports PLA; your Spoolman mapping says PETG. Check slot 2.

It does not pick a winner quietly, and it does not throw away the provider's
remaining weight because the material disagreed — those are two separate claims
about the same slot, and the second may still be right.

## On a printer that reports no filament at all

Most Klipper printers publish nothing about what is loaded; the Snapmaker U1 is
unusual in doing so. On a machine that does not, your mapping is the only source —
and Studio says so in those words:

> PLA is mapped to this slot and matches what the job expects. This printer does
> not report its own filament, so that is your mapping rather than something the
> machine has confirmed.

A provider mapping is never presented as an observation. Studio will still use
the remaining weight, because a spool you told it about having 43 g on it is a
real reason to expect an 87 g job to run out.

## What Studio never does

- **Writes.** Studio does not create spools, does not decrement anyone's remaining
  weight, and does not mark a spool used after a print. Consumption tracking
  belongs to the tool that owns the data; two tools writing the same number is how
  they end up disagreeing.
- **Requires a provider.** A stock printer with no other software is a first-class
  setup. Without a provider, Studio says it does not know, which is true.
- **Leaves your network.** The address is checked to be on your own network —
  loopback, a private range, a tailnet, or a `.local` style name — before any
  request is opened. A public address is refused rather than fetched.
- **Invents a figure.** A provider that cannot say how much is left produces
  unknown, everywhere, all the way to the send button.

## Other providers

The seam is generic: `material_providers.py` normalises any source into one shape
that everything downstream reads without knowing where it came from.

**U1Hub** was re-examined on 2026-08-25 and is deliberately **not** integrated. It
does expose `/api/spools` and `/api/slots`, but they carry no version or schema,
are undocumented for use by other tools, sit behind its own password gate, and are
written for its own interface — and, decisively, U1Hub tracks spool *identity*
(brand, material, colour) and not remaining weight, so it has nothing to answer
this question with. Studio has never read its internal files and will not.
See [interop/U1HUB_INTEROP_PROPOSAL.md](interop/U1HUB_INTEROP_PROPOSAL.md).
