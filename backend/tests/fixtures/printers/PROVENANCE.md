# Printer fixtures — where each one came from

Studio's printer intelligence is tested against fixtures rather than hardware, so
what a fixture *is* has to be recorded as carefully as what it contains. There are
three kinds, and they are not interchangeable.

## Hardware evidence

Captured read-only from a physical machine on a LAN. The only one Studio has is
the Snapmaker U1, and it does not live in this directory — it lives inline in
`tests/test_printer_real_shapes.py`, where the exact `print_task_config` payload a
real U1 returned is pinned so the reader cannot regress against it again.

Recorded outcome: `docs/internal/evidence/0.7.2.json`, `hardware 26/26`.

## Derived from authoritative configuration

`voron_2_4_250_moonraker.json`.

**This is not hardware evidence and must never be described as any.** No VORON 2.4
has been connected to this project. The file is the response Moonraker would
return for a machine built to the configuration Klipper itself publishes for that
printer — `config/kit-voron2-250mm.cfg`, blob
`e82ee28a152ed61599e0422c1c353d13e0c3453e`, GPL-3.0, read 2026-08-25.

Only facts were taken: which sections the configuration declares, the axis limits
its steppers declare, the single `[extruder]` it declares. No configuration text
was copied into this repository. The derivation of every field is written into the
fixture's own `_provenance` block, so the file explains itself wherever it is
read.

The absences matter as much as the contents. That configuration declares no
`exclude_object`, no `bed_mesh`, no `input_shaper`, no `pause_resume`, no runout
sensor, and nothing at all describing loaded filament. Those absences are what
this fixture exists to exercise: they are the shape of a machine that is not a U1,
and they are how Studio's checks are proved to read the printer rather than assume
one.

An absence in that file is not a claim about any particular VORON. It is a base
configuration a builder edits, and owners routinely add those modules. Studio's
capability logic treats a live object list as the only thing that settles the
question in either direction; the profile can say only what is *expected*.

## Simulated

Payloads written by hand to drive a branch — a malformed response, an unknown
object name, a printer that reports more tools than any profile records. They live
inside the tests that use them, never in this directory, so that nothing here can
be mistaken for a reading of a real machine.
