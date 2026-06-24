# Proof — Real-World Validation

Snapmaker Studio is validated against a corpus of **real files** people actually
downloaded and printed — Bambu/Orca projects, PrusaSlicer exports, plain STLs,
multi-color and single-color, large meshes, custom presets, and non-English
filenames. Every file is run end to end: **diagnose → get it ready → validate**.

## Headline

- **Internal validation corpus: 112/112 outputs passed the U1-clean validation gate.**
  This measures Studio's read → prepare → validate pipeline, **not** a guarantee of print
  success on hardware.
- Files are anonymized below as `sample-NNN`; source family, size, before/after verdict,
  and validation result are kept.
- Originals are never modified; a clean print-ready copy is produced.

## Methodology

- Each file is classified by source family, then run through the engine:
  read-only **diagnose** (verdict + score), **get it ready** (convert/repair),
  and structural + U1-cleanliness **validation** of the output.
- "Clean" = output verdict READY **and** validation passes (no residual foreign
  Bambu/BBL/H2D identity, consistent per-color arrays, geometry preserved).
- Reproduce locally:

```bash
python validation/validate_corpus.py <path-to-corpus-folder>
```

The machine-generated results (filenames anonymized):

---

# Snapmaker U1 Conversion — Real-World Validation

**Corpus:** 112 files  
**Clean (READY + validated):** 112  
**Failures:** 0  
**Validation-gate pass rate: 112/112 (not a print-success guarantee).**

## Corpus composition

| Family | Count |
|---|---|
| stl | 91 |
| bambu | 13 |
| u1 | 6 |
| prusa(geometry) | 2 |

- multi-color: 18  
- single-color: 94  
- large (>=50MB): 2  
- custom-preset: 18  
- non-English filenames: 2

## Failures by category

| Category | Count |
|---|---|

## Top failure patterns

- none

## Per-file results

| File | Family | MB | Filaments | Before | After | Score | Valid | Cat | Notes |
|---|---|---|---|---|---|---|---|---|---|
| sample-001 | bambu | 9.4 | 4 | REPAIRABLE | READY | 100 | True |  |  |
| sample-002 | bambu | 39.7 | 5 | REPAIRABLE | READY | 100 | True |  |  |
| sample-003 | bambu | 1.6 | 4 | REPAIRABLE | READY | 100 | True |  |  |
| sample-004 | bambu | 1.6 | 4 | REPAIRABLE | READY | 100 | True |  |  |
| sample-005 | prusa(geometry) | 31.6 | 0 | REPAIRABLE | READY | 100 | True |  |  |
| sample-006 | prusa(geometry) | 12.1 | 0 | REPAIRABLE | READY | 100 | True |  |  |
| sample-007 | bambu | 11.2 | 7 | REPAIRABLE | READY | 100 | True |  |  |
| sample-008 | bambu | 1.9 | 5 | REPAIRABLE | READY | 100 | True |  |  |
| sample-009 | bambu | 1.9 | 5 | REPAIRABLE | READY | 100 | True |  |  |
| sample-010 | bambu | 27.8 | 4 | REPAIRABLE | READY | 100 | True |  |  |
| sample-011 | bambu | 14.2 | 4 | REPAIRABLE | READY | 100 | True |  |  |
| sample-012 | bambu | 21.9 | 4 | REPAIRABLE | READY | 100 | True |  |  |
| sample-013 | u1 | 4.2 | 4 | READY | READY | 100 | True |  |  |
| sample-014 | bambu | 50.2 | 1 | REPAIRABLE | READY | 100 | True |  |  |
| sample-015 | u1 | 16.5 | 4 | READY | READY | 100 | True |  |  |
| sample-016 | stl | 3.8 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-017 | stl | 0.5 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-018 | stl | 26.8 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-019 | stl | 22.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-020 | stl | 5.1 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-021 | stl | 10.0 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-022 | stl | 16.5 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-023 | stl | 62.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-024 | stl | 0.0 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-025 | stl | 0.0 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-026 | stl | 34.8 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-027 | stl | 16.9 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-028 | stl | 11.4 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-029 | stl | 18.3 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-030 | stl | 18.9 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-031 | stl | 14.1 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-032 | stl | 5.7 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-033 | stl | 7.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-034 | stl | 1.3 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-035 | stl | 6.6 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-036 | stl | 39.4 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-037 | stl | 37.7 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-038 | stl | 33.6 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-039 | stl | 4.3 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-040 | stl | 32.7 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-041 | stl | 18.8 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-042 | stl | 12.3 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-043 | stl | 18.5 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-044 | stl | 6.0 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-045 | stl | 2.1 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-046 | stl | 8.6 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-047 | stl | 10.1 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-048 | stl | 11.1 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-049 | stl | 12.3 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-050 | stl | 16.7 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-051 | stl | 23.3 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-052 | stl | 3.4 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-053 | stl | 7.1 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-054 | stl | 3.4 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-055 | stl | 7.3 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-056 | stl | 23.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-057 | stl | 3.0 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-058 | stl | 19.8 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-059 | stl | 4.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-060 | stl | 15.3 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-061 | stl | 10.8 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-062 | stl | 7.1 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-063 | stl | 14.8 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-064 | stl | 5.1 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-065 | stl | 5.1 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-066 | stl | 22.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-067 | stl | 12.9 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-068 | stl | 26.6 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-069 | stl | 6.4 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-070 | stl | 2.6 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-071 | stl | 18.4 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-072 | stl | 6.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-073 | stl | 2.7 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-074 | stl | 4.3 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-075 | stl | 4.5 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-076 | stl | 36.6 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-077 | stl | 10.4 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-078 | stl | 20.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-079 | stl | 26.5 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-080 | stl | 3.9 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-081 | stl | 4.9 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-082 | stl | 4.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-083 | stl | 9.8 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-084 | stl | 1.7 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-085 | stl | 11.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-086 | stl | 10.7 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-087 | stl | 3.0 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-088 | stl | 7.1 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-089 | stl | 11.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-090 | stl | 5.3 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-091 | stl | 14.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-092 | stl | 1.6 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-093 | stl | 14.9 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-094 | stl | 9.1 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-095 | stl | 7.7 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-096 | stl | 5.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-097 | stl | 16.7 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-098 | stl | 16.0 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-099 | stl | 17.4 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-100 | stl | 3.6 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-101 | stl | 4.1 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-102 | stl | 3.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-103 | stl | 3.6 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-104 | stl | 4.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-105 | stl | 4.2 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-106 | stl | 4.8 | 0 | CONVERTIBLE | READY | 100 | True |  |  |
| sample-107 | u1 | 0.0 | 4 | READY | READY | 100 | True |  |  |
| sample-108 | bambu | 5.2 | 5 | REPAIRABLE | READY | 100 | True |  |  |
| sample-109 | u1 | 6.9 | 4 | READY | READY | 100 | True |  |  |
| sample-110 | u1 | 1.7 | 4 | READY | READY | 100 | True |  |  |
| sample-111 | u1 | 16.6 | 4 | READY | READY | 100 | True |  |  |
| sample-112 | bambu | 14.4 | 5 | REPAIRABLE | READY | 100 | True |  |  |