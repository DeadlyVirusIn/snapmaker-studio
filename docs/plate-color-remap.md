# Plate Color Remap

Change **one plate's** filament assignment without touching other plates, meshes,
or painted details. Built for the common Snapmaker U1 case: *"my model says white
but I loaded green in another slot — only fix this plate."*

## Usage
1. Open the **Plate Color Remap** page (sidebar).
2. **Open a 3MF project.** Studio inspects it and lists plates by their **plate
   number** (the slicer's `plater_id`) — never by object order.
3. Pick the **target plate**, the **from** filament (those actually used on that
   plate, with colour swatches), and the **to** filament (any slot in the palette).
4. Click **Preview changes** — a dry-run shows exactly which objects would change,
   which plates stay untouched, and any warnings. Nothing is written yet.
5. Click **Export verified copy.** Studio writes a **new** file and verifies it
   before reporting success.

## Safety guarantees
- Studio only rewrites the selected plate's **object-level extruder** assignment in
  `Metadata/model_settings.config`.
- **Meshes, painted facets, gold accents, and all other plates are never edited.**
  Paint and mesh data live in the `3D/Objects/*.model` files, which Studio copies
  byte-for-byte and never modifies.
- The **original file is never mutated** — export always writes a new file.
- A **verification gate** reopens the output and confirms: only
  `model_settings.config` changed; every `.model` (mesh + paint) is byte-identical;
  exactly the intended objects changed (from->to); all other plates are unchanged.
  If any check fails, the output is **quarantined** and the export is reported as
  failed — success is never claimed on an unverified file.
- Compatibility confirmed against the OrcaSlicer 3MF reader
  (`docs/research/orca-3mf-compat.md`): editing only `model_settings.config` object
  `extruder` values is Orca-safe.

## Known limitation
Large projects (e.g. ~90 MB) take roughly **~30 seconds** to export, because
Studio re-zips and then re-opens the result to run the full verification gate. The
UI stays responsive and shows progress (inspect -> preview -> export & verify).

## Manual validation recipe (for any file)
1. **inspect** — confirm the plate list and each plate's filaments.
2. **dry-run** — confirm the target objects and that other plates are listed as untouched.
3. **export** — write the new file.
4. **reopen / reinspect** the output.
5. **diff** the input vs output zip entries — only `Metadata/model_settings.config`
   should differ; every `3D/` entry must be byte-identical.

## Freedom Torch example (real, validated)
- Plate 4, user-visible white -> green = internally **filament 6 -> 3**.
- Target objects: **12 and 14**.
- After export: **Plate 6 unchanged**, **gold accents unchanged**, painted facets
  and meshes byte-identical, only `model_settings.config` differs, original file
  byte-identical.
- Covered by `backend/tests/test_plate_remap_fixture.py` (runs when the real file
  is present via `SNAPSTUDIO_FT_FIXTURE` or the known path; skips cleanly otherwise)
  and by synthetic-fixture tests in `backend/tests/test_plate_remap.py`.
