# 90-second demo script

One idea, shown once, with no narration of features. Every frame is the real
application on the real sample file shipped in this repository
(`examples/demo_offplate_foreign.3mf`). Nothing is staged.

**The single idea:** *Snapmaker Orca says "out of bounds". Studio says which
object, which edge, how many millimetres, why — and fixes it without touching
your file.*

---

## 0:00 – 0:10 · The problem, not the product

**Screen:** Snapmaker Orca with the sample project loaded, showing its error.

**Voice / caption:**
> You downloaded a model. Your slicer says: out of bounds.
> Which object? Why? It doesn't say.

---

## 0:10 – 0:25 · Studio answers it

**Screen:** Studio → Compatibility → open the same file. The Object placement
card fills in.

**On screen, real output:**
> **1 object is outside the U1's printable area.**
> Object 2 · 10 × 10 × 10 mm — Hangs 55.0 mm past the right edge.

**Voice:**
> Studio reads the file. The part is tiny — it isn't too big. It's in the wrong
> place, because this project was made for a 350 millimetre bed and it still
> carries that printer's coordinates.

---

## 0:25 – 0:40 · The fix, and what it protects

**Screen:** click **Move onto the plate (saves a copy)**. Result appears.

**On screen, real output:**
> 1 object(s) moved onto the U1 plate in a new copy — `..._placed_U1.3mf`.
> Your original file was not changed.
> Layout, rotation, scale and height are unchanged.

**Voice:**
> One click. Studio writes a new file, leaves your original alone, and keeps the
> creator's arrangement exactly as it was.

---

## 0:40 – 0:55 · It only says what it can prove

**Screen:** the Cost & Pricing Doctor on the same, unsliced project.

**On screen, real output:**
> This project has not been sliced yet, so no real material figure exists in the
> file. Slice it in Snapmaker Orca and open the saved project again, or enter
> your own estimate.

**Voice:**
> And where Studio can't know something, it says so. No invented number.
> On a sliced project, this shows the time, weight and cost your own slicer
> already computed — and tells you that's where it came from.

---

## 0:55 – 1:15 · The part nobody else does

**Screen:** the **Best tool for this project** panel under the Orca handoff,
showing a community tool with its reason, licence and caution.

**Voice:**
> The U1 has a whole open-source ecosystem — slicer forks, converters,
> dashboards. The hard part is knowing which one your file needs.
> Studio reads your project and tells you. Mixed nozzle sizes? There's a fork
> for that. Texture data most slicers throw away? There's a fork for that too.
> Nothing special? It says so, and sends you to Snapmaker Orca.

---

## 1:15 – 1:30 · The close

**Screen:** the terminal, one command, real output.

```
$ u1convert placement model.3mf --fix
{ "ok": true, "objects_moved": 1, "after": { "off_plate": [] } }
```

**Voice:**
> Everything the app does is a documented local API and a CLI, MIT licensed,
> entirely offline. Nothing uploaded, no account.
>
> **Orca slices. Fluidd monitors. Studio decides.**

---

## Production notes

- Shoot at 1920 × 1080, light theme, system UI scaling at 100%.
- Anonymise everything on screen: no real IP addresses, hostnames, usernames or
  local paths. Use a demo folder path.
- Do not cut between takes inside a single claim — a viewer must be able to see
  that the result followed the click.
- Do not speed up the fix. It is fast; showing it at real time is the point.
- No music over the 0:40 segment. The refusal is the strongest moment in the
  video and should land in silence.
