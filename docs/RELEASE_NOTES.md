# Snapmaker Studio v0.8.0 — the spool, the printer, and the evidence

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

Two things you can use, and one claim Studio can now back.

## Will this print run out of filament?

A printer knows which spool is in which slot, because it is looking at it. It
knows nothing about how much is left on it. So the question people actually ask
before pressing print is one no printer can answer — and Studio used to say
"unknown" to it on every setup.

If you run **Spoolman** on your network, Studio can now read it.

**Settings → Materials provider.** Choose Spoolman, type the address of the
machine it runs on, press *Test connection*, then say which spool is in which
slot. That is the whole setup. No account, no cloud, and Studio does not scan
your network looking for anything.

It asks which way your slots are numbered — 1 to 4, or 0 to 3 — because a person
counts them one way and the G-code counts them the other. Guessing puts every
spool one slot out and then reports the wrong material with total confidence.

### How hard Studio leans on a number

A refusal to send is the strongest thing Studio says, so it has to be earned:

- **Enough, and recent** — the figure and its age, and you carry on.
- **Short, tracked, and recent** — *not enough*. This blocks the send.
- **Short, but nobody has updated the figure in over a week** — a warning with
  how old it is. Never a refusal.
- **A weight worked out from the spool's declared size** — a warning. That is
  arithmetic, not a record of what has been used.
- **No date on the figure at all** — a warning. Nothing says it is still true.
- **Nothing tracking the spool, or Spoolman unreachable** — *unknown*. Not
  "enough", and not "empty".

Being stopped by bookkeeping teaches people to ignore the warnings, and the next
one might be right.

### When the printer and Spoolman disagree

The printer wins on what is physically in the slot, because it can see it, and
the disagreement is shown rather than quietly resolved:

> Printer reports PLA; your Spoolman mapping says PETG. Check slot 2.

Studio still uses Spoolman's remaining weight there. Which material is loaded and
how much is left are two different claims, and only one of them was contested.

Studio reads Spoolman and never writes to it. It does not create spools, and it
does not decrement anyone's remaining weight after a print.

## A second printer, and what that does and does not mean

Studio's printer intelligence used to be written around one machine. The bed
fallback was a constant called `U1_BED`; a sliced job was checked against the
text "u1" rather than against the printer on the other end of the wire, so a job
correctly sliced for any other machine was reported as wrong.

That knowledge is now data. Studio ships printer profiles — build volume, tool
count, what a machine reports about its own materials, what it is known *not* to
report — and the checks read what the printer actually says.

To prove it rather than assert it, a second profile ships: a **VORON 2.4 250**.
One extruder against the U1's four, a 250 mm cube, no object exclusion, and
nothing at all reporting loaded filament. The same code ran against it: one
toolhead was read as one, a four-tool job was blocked, and what is loaded came
back *unknown* — because a tool count is not a spool count.

**Snapmaker U1 — hardware verified.**
**VORON 2.4 250 — profile verified; hardware not tested by this project.**

Those are different claims and Studio keeps them apart. No VORON has ever been
connected to Studio. That profile's facts come from the configuration Klipper
itself publishes for the machine. The U1 remains the only printer this project
has put on a wire, and it is the printer everything here is verified against.

## Fixed on the way

These were found while making the above reachable. **None of them could affect
v0.7.2**, because nothing in that release could configure a material provider —
the engine could read one and no screen ever sent it an address.

- A provider address went straight to the network layer. A `file://` address
  opened a local file, and a public web address was actually fetched. Addresses
  are now checked to be on your own network before anything is opened. Studio
  still makes no requests to the internet.
- A stale weight, and a weight worked out from a spool's declared size, could
  both refuse a send. Both now warn.
- Spoolman hides archived spools unless asked for them, so a slot mapped to one
  read as "no such spool" rather than "that spool is archived".
- On a printer that reports its own filament, Studio now records that the machine
  itself confirmed the slot — as opposed to a mapping you entered.

## Also in this release

- Design and placement checks name the printer they measured against, so a figure
  that came from a profile never reads as one that came from your machine.
- Printer Hub no longer calls every printer that answers a U1, and shows which
  machine it identified and on what evidence.
- The not-found hint no longer tells you to change a setting on a machine Studio
  has never seen.

## Still true

Studio does not slice — Snapmaker Orca does. Studio never starts a print on its
own; every action in Printer Hub is confirmed by you. Everything is local: no
cloud, no account, nothing uploaded. Your original files are never modified —
preparing always writes a copy. Advice is advisory: Studio reports what it can
establish and says "unknown" when it cannot, and it does not promise a print will
work.

Windows only. The installer is not code-signed — verify the SHA256 on the release
page before running it.

## Known limitations

- The fitted nozzle cannot be read from stock firmware, and free storage is not
  reported by it either.
- Remaining filament is known only where something tracks it. Without a provider
  it stays unknown, which is the honest answer on a stock setup.
- Painted colour is read, but whether two colours meet on a layer is decided by
  the slice, so such colours have a toolhead reserved rather than being called
  simultaneous.
- A PrusaSlicer object whose volumes use different filaments cannot be fully
  carried; the audit reports the rest as not representable rather than picking
  one.
- One machine, one firmware version. The read-only verification generalises; the
  sample does not.

Verification for this release — every count, and what was run against the real
printer — is in [TRUST_STATUS.md](TRUST_STATUS.md).
