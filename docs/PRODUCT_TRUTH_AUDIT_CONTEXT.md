# Product Truth Audit Context — beta.20

Purpose: Snapmaker Studio is a local pre-print intelligence layer for the Snapmaker U1. It
reads a 3D model, runs read-only "Doctors" that explain print risks in plain language, and
prepares a separate copy for handoff to Orca (originals are never modified). "Prepared" means
a copy is written — it is NOT a claim the model is clean, layout-safe, or will print. Studio
does NOT slice (Orca does); nothing here is a print-success guarantee.

Latest release: v0.4.0-beta.20 (commit d2599af).

## Routes (from App.tsx)
/ Dashboard · /workspace Workspace · /start BeginnerWorkflow · /source SourceCompatibility ·
/compatibility Compatibility · /scale ScaleDoctor · /first-layer FirstLayer ·
/print-quality PrintQuality · /plate-remap PlateRemap · /find-models FindModels ·
/printers Printers (+PrinterControls) · /batch Batch · /projects Projects · /settings Settings ·
/why WhyStudio · /help Help · /doctor/:id DoctorLanding (project, cost, pricing, profit,
multi-material). Components: DesignInsights/LiveWorkspace, BusinessDoctors, IntelligenceReport,
DesignHealth, OrcaHandoff, StrategyPicker, Compare/diff.

## Prior REAL user failures (must stay fixed)
- Scale Doctor recommended unsafe 128% that Orca rejects on placement.
- Compatibility "U1 copy" opened in Orca with objects outside the plate (layout not fixed).
- Pricing/Cost pages showed placeholder instead of the calculator.
- Project Doctor false green "U1-ready"/100 for a 13-colour/5-plate file.
- Systemic false-ready wording across surfaces.

## Must NEVER be overclaimed (from raw verdict / validated_ok alone)
U1-ready · ready to slice · clean · safe · fixed · validated · passed.

## Honest wording rules
- profile compatible ≠ print ready.
- structure validated ≠ layout safe.
- dimension/size fit ≠ Orca placement fit.
- layout/scale placement is an advisory heuristic, NOT a port of Orca PartPlate — verify in Orca.
- Studio does not slice; originals are never modified.
- no print-success guarantees — "prepared"/"profile compatible" never means "will print".
