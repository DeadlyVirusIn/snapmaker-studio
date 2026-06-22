# Reserved / low-traffic API endpoints (classification)

The loopback engine (`snapstudio_api/server.py`) exposes some POST routes that the
desktop client (`desktop/src/api.ts`) does not currently call. They were audited
and **kept** (not removed) — each is either referenced elsewhere, documented, or a
deliberate part of a route family. Removing them is not worth the risk for a beta.

| Endpoint | Desktop caller | Classification | Why kept |
|---|---|---|---|
| `/strategies`, `/strategy/recommend` | referenced in `api.ts` | **active/reserved** | wired in the client API layer |
| `/canonical` | none | **reserved** | source-neutral canonical model is a roadmap seam (referenced in design docs); read-only |
| `/community_knowledge` | none | **reserved** | documented in `docs/fund/VALIDATION.md`; advisory read-only |
| `/printer/bed_mesh` | none | **reserved (route family)** | parallels the other `/printer/*` read-only probes; cheap to keep, likely surfaced in a later printer view |

Policy: if any of these is still uncalled by the next minor release and not on the
near-term roadmap, revisit for removal then (with its tests/docs). Until then they
are intentionally retained as read-only, reserved API surface — no action needed.
