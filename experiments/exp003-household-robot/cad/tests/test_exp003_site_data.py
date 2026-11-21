"""The website's build data must match the design. No CadQuery needed."""

import importlib.util
import json
from pathlib import Path

CAD = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("export_site", CAD / "export_site.py")
assert spec and spec.loader
export_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_site)


def test_site_data_is_current():
    # Fails after any change to the CAD numbers, servo.toml, the exp003 README's progress log or
    # phases, or docs/inventory.md. Fix: run cad/export_site.py (see its docstring) and commit.
    on_disk = export_site.OUT.read_text()
    assert on_disk == export_site.render(export_site.build()), (
        "run export_site.py and commit the JSON"
    )


def test_site_data_has_every_section():
    data = json.loads(export_site.OUT.read_text())
    for key in (
        "wheel",
        "tire",
        "cradle",
        "servo",
        "base",
        "bom",
        "phases",
        "timeline",
        "consumables",
    ):
        assert data[key]
    # The 2026-11-17 order (items 1 to 30) plus later rows, numbered without gaps.
    assert [r["n"] for r in data["bom"]] == list(range(1, len(data["bom"]) + 1))
    assert len(data["bom"]) >= 30
    assert {p["track"] for p in data["phases"]} == {"v1", "v2"}


def test_hub_section_stays_inside_the_wheel():
    data = json.loads(export_site.OUT.read_text())
    w = data["wheel"]
    for poly in w["hub_section"]:
        for r, z in poly:
            assert 0 <= r <= w["rim_od_mm"] / 2 + w["flange_mm"] + 1e-9
            assert 0 <= z <= w["width_mm"] + 1e-9
