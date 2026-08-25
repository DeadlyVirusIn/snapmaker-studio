# A small read-only interface for spool state

**To:** the U1Hub maintainer
**From:** Snapmaker Studio (independent open-source project, MIT)
**Status:** proposal, still open. Studio depends on nothing in U1Hub today.

> ## Re-audited 2026-08-25 — Studio is not integrating, and here is why
>
> U1Hub's `main` was read again on 2026-08-25 rather than trusting this document.
> Two things were checked: whether an interface exists that U1Hub *means* to offer,
> and whether it carries the numbers this proposal is actually about.
>
> **`GET /api/spools` and `GET /api/slots` do exist**, in `rfid.js`. That is close to
> what is asked for below, and worth saying plainly.
>
> **They are not an external contract, on the evidence available.** They carry no
> schema or version field; they return internal state spread directly into the
> response; the README documents user-facing features and nowhere offers an API to
> other tools; the routes sit behind the same password gate as every page; and the
> code comments describe them in terms of "the UI" they serve. An Express route
> that a project's own frontend calls is not a promise to anyone else, and treating
> it as one would produce breakage that looks like U1Hub's fault and is Studio's.
>
> **More decisively, U1Hub does not track remaining filament weight.** Its spool
> registry is an RFID/QR *identity* store — brand, material, colour — and the words
> `remaining`, `weight` and `grams` do not appear in that module at all. The three
> fields this proposal names as carrying most of the value (`remaining_g`,
> `remaining_quality`, `remaining_as_of`) have nothing to map to. So even with a
> blessed, versioned API, integrating would not answer the question Studio is
> asking: *will this print run out of filament?*
>
> Studio therefore continues with Spoolman, which does track consumption, and this
> proposal stays open rather than being withdrawn — the offer is unchanged if an
> interface and a weight ever exist. Nothing in U1Hub's internal files has been
> read, then or now.
>
> Evidence: `dlgambill/u1hub`, MIT, default branch `main`, last pushed
> 2026-08-17. Reviewed files: `README.md`, `server.js`, `rfid.js`, `BETA-TESTING.md`.

## Why this is a proposal and not a pull request

Studio can tell a user that a sliced job needs 87 g in slot 2. It cannot tell them
whether 87 g is there, because a printer knows which spool is loaded and nothing
about what is left on it. U1Hub does know — it keeps a spool registry and a
loadout, which is the piece of the answer the machine cannot supply.

The obvious shortcut is to read `spools.json` and `slots.json` directly. Studio
will not do that. Those files are U1Hub's internal state; reading them would couple
this project to your implementation details, break the moment you change them, and
produce bug reports that look like your problem and are ours. It would also mean
two tools quietly disagreeing about the same spool with no way for either to know.

So: if there is an interface you are willing to support, Studio will use it. If
there is not, Studio carries on reporting "nothing tracks how much is left", which
is the truth on a stock setup and is not a crisis.

## What Studio would ask for

Four fields, read-only, one request. Everything else is optional.

```
GET /api/spools        →  the spools U1Hub knows about
GET /api/loadout       →  which spool is in which slot on a given printer
```

A shape along these lines would be enough — the names matter less than the
distinctions:

```json
{
  "schema": "u1hub/spools/1",
  "spools": [
    {
      "id": "a3f1",
      "material": "PLA",
      "subtype": "Matte",
      "color": "#2D9E59",
      "vendor": "Snapmaker",
      "remaining_g": 431.5,
      "remaining_quality": "tracked",
      "remaining_as_of": "2026-08-21T18:04:11Z"
    }
  ]
}
```

```json
{
  "schema": "u1hub/loadout/1",
  "printer": "u1-workshop",
  "slots": [
    { "slot": 0, "spool_id": "a3f1" },
    { "slot": 1, "spool_id": null }
  ]
}
```

Three details carry most of the value:

* **`remaining_quality`.** Studio blocks a send when a job needs more filament than
  a spool holds, and that sentence has to be earned. A figure U1Hub tracks is worth
  stopping a print for; a figure worked out from a net weight and a usage estimate
  is worth a warning. Studio labels these differently and says which it has, so
  the distinction has to survive the crossing.
* **`remaining_as_of`.** Bookkeeping drifts. Knowing when it was last true is the
  difference between "43 g left" and "43 g left, as of three weeks and four prints
  ago".
* **Slot numbering, stated.** A person counts the slots on a U1 as 1–4; G-code
  counts them 0–3. Getting that wrong reports the wrong material for every slot
  with complete confidence, which is worse than not knowing. Either numbering is
  fine as long as the response says which one it is.

## What Studio would never do

* **Write anything.** No creating spools, no decrementing remaining weight, no
  marking a spool used after a print. Consumption tracking belongs to the tool that
  owns the data; two tools writing the same number is how they end up disagreeing.
* **Require U1Hub.** A stock U1 with nothing else installed is a first-class setup
  and will stay one. Every provider Studio reads is optional.
* **Override the printer.** The machine is authoritative about *what* is in a slot,
  because it is looking at it. A provider may add what the machine cannot know — a
  spool identity, a remaining weight — and a disagreement between the two is shown
  to the user as a disagreement rather than resolved silently.
* **Copy U1Hub.** Studio does not queue jobs, does not manage a farm, and has no
  plans to. This is one number Studio is missing, not a feature it wants back.

## What already exists on the Studio side

The seam is built: `material_providers.py` normalises any source into one shape,
and Spoolman is read through it, read-only, over the local network. As of
2026-08-25 that is reachable from the app itself — Settings carries a materials
provider section, an address, a connection test and an explicit slot-to-spool
mapping. Before that date the engine could read a provider and nothing in the
desktop ever sent it one, which is worth stating plainly: this paragraph used to
say "shipped", and for a user of the published build it was not.

Adding U1Hub would be one provider function against a documented route — roughly
forty lines, no changes anywhere else, and nothing else in Studio would know or
care where the number came from.

## Contact

Open an issue on the Studio repository, or reply on whichever thread this reached
you through. If the answer is "no interface, not now", that is a complete answer —
this proposal exists so that the alternative is not Studio reading your files
behind your back.
