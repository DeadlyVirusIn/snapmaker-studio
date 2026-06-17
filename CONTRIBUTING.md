# Contributing to Snapmaker Studio

Thanks for helping make Snapmaker U1 files "just work." Issues and pull requests are welcome.

## Dev setup

```bash
pip install -e "backend[dev]"
cd backend && pytest
```

## Guidelines

- Keep the engine (`snapstudio_core`) pure — no network, UI, or printer-communication imports.
- Add or update tests for any behaviour change, and keep the suite green.
- Never commit personal model files or absolute paths. Tests that need real sample files should skip cleanly when those files are absent.
- Keep changes focused and match the existing style.

## Pull requests

1. Fork and create a branch.
2. Make your change with tests.
3. Run `pytest` — all green.
4. Open a PR describing the user-facing effect.

## Reporting issues

Use the bug-report or feature-request template. For bugs, include your OS, Python version, and (if possible) a small sample file.

## License

By contributing, you agree that your contributions are released under the project's [MIT License](LICENSE).
