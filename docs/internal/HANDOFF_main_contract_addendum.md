# Addendum — the four contract fixtures, and the trap that stopped them

Written 2026-08-27. Read `HANDOFF_main_contract.md` first; this only adds what
was learned trying to close its four outstanding fixtures.

**No runtime code changed. `main` is unchanged at the commit that carries this
file, and the contract audit is still open.**

## State

| | |
|---|---|
| Current stable release | **v0.8.0**, published, untouched |
| Contract audit | **still open** — the four fixtures are built, not yet answered |
| Software gates | backend **1731 passed / 4 skipped**, desktop **335**, selfcheck **27/27**, `tsc` clean, `cargo check` clean, production build clean |

## What was done

The four fixtures named in the previous handoff were rebuilt from current `main`,
plus the controls they need:

| fixture | what it asks |
|---|---|
| `N0_prusa_carry_undeclared` / `N1_prusa_carry_declared` | do the five carried PrusaSlicer process values survive declared, and reset undeclared? |
| `M01_machine_gcode_undeclared` / `M02_machine_gcode_declared` | does an undeclared `machine_start_gcode` sentinel reach the exported G-code? |
| `F0_full_549` / `F1_minimal_541` | the same source prepared with the pre-minimisation template and the current one — semantic round-trip and slice comparison |

Each pair differs in exactly one thing, checked by digest: `N0` and `N1` differ
only in `different_settings_to_system`; so do `M01` and `M02`; `F0` and `F1`
differ only in the eight keys the last instalment removed.

The carried values are deliberately **not** the U1 preset's — 0.15 mm layers,
0.3 mm first layer, 37% infill, four walls, 8 mm brim — so a survivor cannot be a
default that was there anyway.

## The trap: a mis-aimed keystroke looks exactly like a timeout

Two runs failed with *"SAVE FAILED: … was not written within 120s"*, which reads
like Orca refusing the file. It was not. The hardened harness now reports which
windows were open at the moment of failure, and it said:

```
Windows: #32770:Save file as | wxWindowNR:N0_prusa_carry_undeclared - Snapmaker Orca
```

The Save dialog was open the whole time. The path was typed into the **file
list** rather than the *File name:* box, where it became type-ahead search and
Enter did nothing. Focus lands in the list often enough that the old code worked
for a whole sprint and then stopped.

Fixed by pressing **Alt+N** — the common dialog's accelerator for the filename
box — before selecting and typing. Both the Save Project As path and the G-code
export path do it now.

Three further hardenings came out of the same failure, and are worth keeping:

* **`Clear-OwnedModals`** before any shortcut. A project that declares deviations
  makes Orca show its *Customized Preset* notice on open, and `Ctrl+Shift+S` sent
  into that notice is silently lost. Every project carrying non-default source
  settings now declares, so this is the common case rather than the odd one.
* **`Test-IsFileDialog`** before typing a path. A `#32770` is not necessarily a
  file dialog, and typing a path into a warning is how a save never happens.
* **On failure, say what was on screen.** The diagnosis above took one run once
  the harness reported its windows, and several before that reported nothing.

## Why the fixtures are still unanswered

Two reasons, and the second is the one worth remembering.

The harness drives the foreground, so it competes with whoever is using the
machine — and it is built to lose that competition rather than type into
somebody's browser. The desktop was in near-continuous use, so runs kept
declining before they started. That is the harness behaving correctly, and an
idle gate was added so a run either happens on a quiet machine or does not happen
at all.

**Then the idle gate turned out to be measuring the wrong thing.** `Alt+N` did
not fix the save either, and the failure screenshot showed why: the window in the
foreground was not Orca and was not a browser. It was **another automated session
running on this machine**, working in a different repository, taking the
foreground while nobody touched the keyboard.

`GetLastInputInfo` measures *human* input. A second agent on the same desktop
makes the idle counter read "quiet" while the foreground is pulled away every few
seconds — so every save was typed into a dialog that lost focus before Enter
committed, and every failure read as a timeout.

Nothing was typed into the other session: `Send-OwnedKeys` checks foreground
ownership before every keystroke and the failures were all `SAVE FAILED`, never
`REFUSING TO TYPE`. The guard held. But a check before the send and a steal
during it is a race, and the results of a run under those conditions could not be
trusted anyway.

So idleness is now two conditions rather than one — no human input **and** a
foreground that stays put for several seconds — and `Assert-StillOwned` re-checks
ownership after the save is committed, so a stolen foreground is reported as a
stolen foreground instead of as a timeout.

**GUI automation on this machine needs a desktop with no other agent session
running on it.** That is a scheduling constraint, not a bug to code around.

## Running them

Everything lives in the session scratchpad and goes when the session does.
`build_fixtures.py` rebuilds all six from `main` in a few seconds;
`run_contract.ps1` waits for a clear desktop and runs whichever have no result
yet, skipping the ones that do; `compare.py` answers the four questions from the
files Orca wrote.

```
py build_fixtures.py                                  # six fixtures
.\run_contract.ps1 -MinIdleSec 120 -WaitMinutes 600   # waits, then runs
py compare.py                                         # the verdict
```

`run_contract.ps1` is re-runnable and idempotent — it skips anything already
saved, so an interrupted night can be picked up rather than restarted.

## One observation worth keeping regardless

Declaring deviations, which is what makes a carried setting reach the slicer,
also makes Snapmaker Orca show its **"Customized Preset"** notice when the
project is opened. `is_u1_clean` already says so as a warning rather than a
fault, and that is the right way round: the notice is accurate, because the
project genuinely does state values the named preset does not.

But it means a prepared copy of any PrusaSlicer project with non-default print
settings now shows that notice, where before it opened clean and quietly threw
the settings away. Worth a sentence in the user-facing copy before the next
release, so nobody reads it as a fault.

## Not started

**The second material provider.** It is gated on the contract audit being green,
and the audit is not answered yet. Nothing was researched, chosen or written.
