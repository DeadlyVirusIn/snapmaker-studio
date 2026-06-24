# Contributing to Snapmaker Studio

Thanks for helping make Snapmaker U1 files "just work." Issues and pull requests are welcome.

## Dev setup

```bash
pip install -e "backend[dev]"
cd backend && pytest
```

## Checks before opening a PR

Run the checks that match what you touched — all must pass:

- **Backend:** `cd backend && pytest`
- **Frontend:** `cd desktop && npx tsc --noEmit && npx vitest run`
- **Desktop / Rust** (only when `desktop/src-tauri/` is touched): `cd desktop/src-tauri && cargo check`

## Guidelines

- Keep the engine (`snapstudio_core`) pure — no network, UI, or printer-communication imports.
- Add or update tests for any behaviour change, and keep the suite green.
- Keep changes focused and match the existing style.
- **Never commit private data or generated tool state.** No real IPs, hostnames, local
  paths, usernames, tokens/secrets/API keys, private or copyrighted model/file names, or
  tool/session state (e.g. `.claude-octopus/`, `.docker/mcp/`, `validation/report.md`,
  `*.db`/`*.sqlite`, OS cache trees). Anonymize proof/sample data (`sample-NNN`). Tests
  needing real sample files should skip cleanly when those files are absent.

## Pull requests

1. Fork and create a branch.
2. Make your change with tests.
3. Run `pytest` — all green.
4. Open a PR describing the user-facing effect.

## Reporting issues

Use the bug-report or feature-request template. For bugs, include your OS, Python version, and (if possible) a small sample file.

## License

By contributing, you agree that your contributions are released under the project's [MIT License](LICENSE).
