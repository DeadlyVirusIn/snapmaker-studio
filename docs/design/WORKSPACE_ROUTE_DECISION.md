# `/workspace` subtree — decision: intentional, keep (not nav-listed)

Audited: `WorkspaceSwitch` → (simple) `DesignInsights` / (advanced) `LiveWorkspace`,
plus `StrategyPicker`, `BusinessDoctors`, `DesignHealth`, `lib/simple.ts`.

**Finding:** this is **not dead code**. `/workspace` is the screen the user lands on
after **Open file / drag-drop** (`hooks/useOpenFile.ts` → `AppShell.tsx`). It is in
`STATIC_ROUTES` (so `isKnownRoute` accepts it, no blank page) but deliberately
**absent from `PRIMARY_NAV`/`SECONDARY_NAV`** — you reach it by opening a model,
not by clicking a sidebar item. That is the intended flow (Discover → open → the
file's workspace), so there is nothing broken to fix.

**Decision:** keep as-is; do not delete, do not add a sidebar entry. A nav entry
would be misleading (there's no file to show until one is opened). If a future
"recent/empty workspace" landing is wanted, that's a feature, not a cleanup.

**Guard:** `nav.test.ts` already asserts `isKnownRoute` covers static routes, so
`/workspace` won't regress to a blank page. No code change this sprint.
