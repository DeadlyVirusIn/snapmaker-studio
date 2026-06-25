# Snapmaker Studio v0.4.0-beta.17.2 — Real Business Math + Orca Verification

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

The cost calculator now does real, transparent math from *your* numbers, and the files
Studio generates were opened in a real Snapmaker Orca. Estimates are rough and depend on
your inputs — not financial advice, not a print-success guarantee.

## Real business math

Material cost is now exactly what you'd expect:

```
material cost = grams used × spool price ÷ spool weight
e.g.  82 g × $24 ÷ 1000 g = $1.97
```

The **Material & business assumptions** panel asks for the inputs that matter and shows
them working:

- **Grams used** — auto-filled from your file (or the slicer when you send it to the
  printer); type a value to override when Studio doesn't know it.
- **Spool price + spool weight** (default 1000 g) → cost per gram.
- Electricity /kWh + printer watts, printer price + life (machine wear), labour time +
  rate, waste/failure %, **packaging**, marketplace fee %, **shipping cost + charged**,
  and markup. A live line shows the material formula; saved locally; reset to defaults.
- Full formula: material + electricity + machine wear + labour + packaging + failure
  buffer → cost; + marketplace fee + markup → price; shipping (charged − cost) adjusts
  profit. **Rough estimate — not financial advice.**

What's labelled honestly: print time comes from the slicer when known (else time-based
costs show as 0); material-type density isn't applied yet.

## Snapmaker Orca verification

Files Studio generates were opened in the **installed Snapmaker Orca** (not just code
review): the **scaled STL export** (a 20 mm cube → 30 mm at 150%) and a **Compatibility
"Prepare U1 copy"** 3MF both launched and opened without a crash or parse error.

## 3MF scaling

Still STL-only for scaled export, stated next to the controls. Verified uniform 3MF
scaling (multi-part / colour / paint preservation, checked in Orca) remains on the roadmap
— we don't ship unverified scaling.

## Carried forward

Editable assumptions + First Layer file evidence (beta.17.1), Scale STL export +
Compatibility prepare (beta.17), hardware-verified Printer Hub, Print Quality evidence,
Source Check, Plate Remap, Model Browser. Local-first. Studio does not slice; never takes
autonomous control; originals are never modified.

## Download (unsigned beta)

```
File:    Snapmaker.Studio_0.4.0-beta.17.2_x64-setup.exe
Size:    16121235 bytes
SHA256:  077de9444c1ef5a56d6b4f5f44a9986b094e150b26823716f5df463c8e8b845f
```

Unsigned — SmartScreen may show "Unknown publisher." Verify the SHA256 before installing.
Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.17.2/docs/windows-install.md).
