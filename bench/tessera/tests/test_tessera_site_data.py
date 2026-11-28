"""The website's Tessera drawings must match the models. No CadQuery needed."""

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tessera_export_site", HERE / "export_site.py")
assert spec and spec.loader
export_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_site)


def test_site_data_is_current():
    # Fails after any change to tessera_cad's params or layout. Fix: run export_site.py, commit.
    assert export_site.OUT.read_text() == export_site.render(export_site.build()), (
        "run bench/tessera/export_site.py and commit the JSON"
    )


def test_layout_fills_the_field_once():
    data = json.loads(export_site.OUT.read_text())
    lay = data["layout"]
    seen: set[tuple[int, int]] = set()
    for m in lay["modules"]:
        for i in range(m["nx"]):
            for k in range(m["ny"]):
                cell = (m["col"] + i, m["row"] + k)
                assert cell not in seen
                assert 0 <= cell[0] < lay["cols"] and 0 <= cell[1] < lay["rows"]
                seen.add(cell)
    assert len(seen) == lay["cols"] * lay["rows"]


def test_key_sits_inside_the_socket():
    j = json.loads(export_site.OUT.read_text())["joint"]
    assert len(j["socket"]) == len(j["key"]) == 6
    assert max(abs(x) for x, _ in j["key"]) < max(abs(x) for x, _ in j["socket"])
    assert len(j["ribs"]) == 4
