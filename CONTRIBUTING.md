# Contributing

Thank you for helping improve Intelbras iSIC Cloud for Home Assistant.

## Before starting

Open an issue for behavioral changes or protocol work. Never include real
credentials, serial numbers, camera frames, APK contents, or additional vendor
binaries in an issue or pull request.

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

## Pull requests

- Keep one logical change per pull request.
- Add or update tests for behavior changes.
- Update translations and documentation when user-visible behavior changes.
- Use conventional commit prefixes where practical (`feat:`, `fix:`,
  `docs:`, `test:`, `chore:`).
- Confirm that logs and diagnostics do not expose credentials.

By contributing original code, you agree to license it under the MIT License.
Do not contribute code or artifacts you are not authorized to redistribute.
