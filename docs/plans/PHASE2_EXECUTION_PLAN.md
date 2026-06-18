# Phase 2 — Execution Plan

Three features that turn Studio from "one file" into "my work": **Project
Library**, **Compare/Diff UI**, **Batch Conversion**. All local-first; all reuse
the existing kernel (`snapstudio_core`) + sidecar (`snapstudio_api`) + desktop
shell. Estimates are engineer-weeks for a single dev; sequence A -> B -> C (A
unblocks B and C).

---

## A. Project Library

**Goal:** a persistent local home for projects — what you opened, converted,
its verdict/score, where the output went — with search, tags, collections.

### Architecture
- **Store:** SQLite at `%APPDATA%/SnapmakerStudio/library.db` (stdlib `sqlite3`
  in the sidecar — no new runtime dep, freezes cleanly). The DB is an **index**,
  not a file store; it references source/output **paths** (files stay where the
  user keeps them — local-first, no copying GB of models).
- **Sidecar endpoints (new):** `GET /library`, `POST /library` (add/update from a
  doctor/convert result), `DELETE /library/{id}`, `GET /library/search?q=&tag=`.
- **Engine:** reuse `doctor`/`convert` results (already JSON dicts) as the row
  payload; a thin `library.py` does CRUD.

### Database changes (new `library.db`)
```
projects(id PK, name, source_path, source_family, output_path,
         verdict, score, filament_count, last_action, updated_at)
tags(id PK, name UNIQUE)
project_tags(project_id FK, tag_id FK)
collections(id PK, name)
collection_projects(collection_id FK, project_id FK)
history(id PK, project_id FK, action, detail, at)   -- doctor/convert events
```
Dates stored as ISO-8601 UTC strings (e.g. `2026-06-18T20:00:00Z`). Migrations
via a `schema_version` pragma; v1 ships the above.

### UX
- **Projects route** (replace the mock library): grid/list of real rows, status
  badges, search box (live), tag filters, collections in the sidebar "Pinned".
- Opening/converting a file auto-upserts a row + a history entry.
- Workspace shows the project's history timeline (real, not mock).
- Missing-file handling: row flagged "source moved" with a re-locate action.

### APIs (frontend)
`api.ts`: `listProjects()`, `searchProjects(q, tags)`, `upsertProject(result)`,
`deleteProject(id)`, `addTag/removeTag`. Session store records on doctor/convert.

### Milestones
1. `library.py` + schema + sidecar CRUD endpoints (+ tests). **~1.0 wk**
2. Auto-upsert on doctor/convert; history events. **~0.5 wk**
3. Projects UI (search/tags/collections) wired to real data. **~1.5 wk**
4. Missing-file + migration handling, polish. **~0.5 wk**
**Estimate: ~3.5 weeks.**

### Risks
- Path drift (users move files) -> mitigate with re-locate + content hash match.
- DB in a frozen sidecar -> verify PyInstaller bundles `sqlite3` (stdlib; low risk).
- Scope creep into a file manager -> keep it an *index*, not storage.

---

## B. Compare / Diff UI

**Goal:** ship the existing `diff` engine in the app — "what changed between
original and U1?" with geometry-preserved proof.

### Architecture
- **Engine exists** (`snapstudio_core/diff.py`, `diff_projects(a, b)` -> schema
  `diff/1`). Add a sidecar endpoint **`POST /diff {a, b}`** -> `service.diff()`.
- No DB needed; operates on two file paths. Library (A) supplies "compare to
  original" pairs automatically (source vs output_path).

### UX
- Workspace **Compare tab** becomes live: pick "original <-> converted" (auto-filled
  from the library row) or choose any two files.
- Render real diff sections: structure (+/- parts), geometry changed?
  (preserved = ok), object/plate/filament counts, painted-triangle delta,
  settings changed/added/removed (the engine already returns these).
- Headline reassurance: **"Geometry identical"** when fingerprints match.

### APIs
`api.ts`: `diff(a, b)`. Workspace Compare tab consumes `diff/1` dict.

### Milestones
1. `service.diff` + `POST /diff` endpoint (+ test). **~0.5 wk**
2. Compare tab real rendering (replace mock table). **~1.0 wk**
3. Auto-pair from library; "geometry identical" proof UI. **~0.5 wk**
**Estimate: ~2 weeks.**

### Risks
- Large files -> diff reads two archives; stream/limit settings list (engine
  already truncates in CLI). Low.
- Pairing UX ambiguity -> default to library auto-pair, manual picker as fallback.

---

## C. Batch Conversion

**Goal:** drop a folder; convert + validate many files; get a summary report.
This is the corpus validator, productized for end users.

### Architecture
- **Reuse `convert_to_u1`** per file; reuse the corpus classification/report
  logic. New `batch.py` orchestrates a job over a file list.
- **Sidecar:** `POST /batch {paths|dir, out_dir}` starts a job; progress via
  Server-Sent Events or polled `GET /batch/{job}` (per-file status). Run files
  sequentially in a worker thread (engine is CPU/IO bound; keep it simple first).
- Output: each `<name>_SnapmakerU1.3mf` beside source (or chosen out_dir) + a
  `batch-report.json/.md`.

### Database changes
Optional: a `batch_jobs` table (job id, started_at, totals) + per-file rows in
`history`. Reuse Library (A) so batch results populate the library.

### UX
- Dashboard "Batch" action / drop a **folder** on the hero.
- Progress screen: N/total, per-file rows (verdict, validated, category), running
  success rate; cancel button.
- Completion: summary (success rate, failures by category) + "open output folder";
  failures link into the Workspace for that file.

### APIs
`api.ts`: `startBatch(paths|dir)`, `batchStatus(job)` (poll). Cancel = `DELETE`.

### Milestones
1. `batch.py` (list -> convert -> validate -> classify) + tests. **~1.0 wk**
2. Sidecar job + progress endpoint (+ cancel). **~1.0 wk**
3. Batch UI (drop folder, progress, summary). **~1.5 wk**
4. Library integration + report export. **~0.5 wk**
**Estimate: ~4 weeks.**

### Risks
- Long jobs / huge files -> background worker + cancel; never block the UI thread.
- Disk pressure (temp copies) -> convert in place to out_dir, avoid copying like
  the validator does for very large files.
- Partial failures -> must continue + report (already the corpus behavior).

---

## Sequencing & total
A (3.5w) -> B (2w) -> C (4w) ~ **~9-10 engineer-weeks**. A first (DB + library is
the backbone B/C plug into). Each ships independently and is corpus-gated so
reliability can't regress.

## Cross-cutting
- New sidecar endpoints follow the existing token-gated + CORS pattern.
- Every engine addition gets unit tests + a corpus pass before UI wiring.
- Keep the novice one-click path unchanged; these are additive power features.
