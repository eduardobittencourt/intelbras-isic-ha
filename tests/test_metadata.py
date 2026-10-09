"""Repository metadata tests."""

import importlib
import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_manifest_metadata() -> None:
    """Manifest points to the canonical repository and has a semantic version."""
    manifest = json.loads(
        (ROOT / "custom_components/intelbras_isic/manifest.json").read_text()
    )

    assert manifest["domain"] == "intelbras_isic"
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])
    assert manifest["version"] == project["version"]
    assert manifest["documentation"].startswith(
        "https://github.com/eduardobittencourt/"
    )
    assert manifest["issue_tracker"].endswith("/issues")
    assert manifest["codeowners"] == ["@eduardobittencourt"]


def test_brand_icon_is_png() -> None:
    """The bundled HACS brand asset is a PNG file."""
    icon = ROOT / "custom_components/intelbras_isic/brand/icon.png"
    assert icon.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_all_platforms_import() -> None:
    """Every forwarded Home Assistant platform imports successfully."""
    for platform in ("binary_sensor", "camera", "sensor"):
        importlib.import_module(f"custom_components.intelbras_isic.{platform}")
