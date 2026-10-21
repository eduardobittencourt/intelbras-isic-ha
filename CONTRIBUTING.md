# Contributing

Thank you for helping improve Intelbras iSIC Cloud for Home Assistant.

## Before starting

Open an issue for behavioral changes or protocol work. Never include real
credentials, serial numbers, camera frames, APK contents, or additional vendor
binaries in an issue or pull request.

## Documentation

Write documentation, interface text, comments, and contribution descriptions in
English. Use the [documentation index](docs/README.md) to choose the right
location: user procedures belong in `docs/guides/`, implementation details in
`docs/reference/`, and plans or dated evidence in `docs/development/`. Update
incoming links when moving a document. Record test dates and limitations
separately from current behavior. Do not add duplicate language versions.

## Development setup

Use Python 3.14 or newer:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
pre-commit install
```

Run the same checks as CI:

```bash
ruff check .
ruff format --check .
pytest
```

The test extra accepts the harness versions used by CI for HA 2026.9.4 and
2026.10.1. To reproduce one environment, add
`pytest-homeassistant-custom-component==0.13.367` (minimum) or `==0.13.372`
(current stable) to the install command. NumPy is selected by that harness.

## Pull requests

- Keep one logical change per pull request.
- Add or update tests for behavior changes.
- Update English interface strings and documentation when user-visible behavior
  changes. Keep `strings.json` and `translations/en.json` consistent.
- Use conventional commit prefixes where practical (`feat:`, `fix:`,
  `docs:`, `test:`, `chore:`).
- Confirm that logs and diagnostics do not expose credentials.

By contributing original code, you agree to license it under the MIT License.
Do not contribute code or artifacts you are not authorized to redistribute.
