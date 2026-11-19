"""Checks on the hub's derived numbers. No CadQuery needed, so these run in the lab's suite."""

from dataclasses import replace
from pathlib import Path

import pytest
from exp003_cad.params import Horn, HubParams, derive, load

# Plausible STS3215 values, used only to test the arithmetic.
HORN = Horn(
    od_mm=20.0,
    thickness_mm=2.5,
    bolt_count=4,
    bolt_circle_mm=14.0,
    bolt_size="M2",
    center_head_mm=5.0,
    center_head_height_mm=0.0,
    shaft_height_mm=4.0,
)


def params(**horn_changes) -> HubParams:
    return HubParams(horn=replace(HORN, **horn_changes), measured=True)


def test_recess_is_shallower_than_the_horn():
    d = derive(params())
    assert d.recess_depth_mm == pytest.approx(1.5)
    assert d.recess_diameter_mm == pytest.approx(20.4)

    thin = derive(params(thickness_mm=1.6))
    assert thin.recess_depth_mm == pytest.approx(1.1)


def test_web_grows_to_keep_two_mm_under_m3_heads():
    d = derive(params(bolt_size="M3", bolt_circle_mm=14.0))
    # recess 1.5 + counterbore 3.3 + 2.0 of material = 6.8, more than the 6.0 default.
    assert d.web_mm == pytest.approx(6.8)
    assert d.web_mm - d.counterbore_depth_mm - d.recess_depth_mm == pytest.approx(2.0)


def test_screw_length_reaches_into_the_horn_but_not_the_case():
    d = derive(params())
    # 2.2 mm of hub to clamp, then at least 2.0 mm of thread in the horn; the case is 5.7 mm away.
    assert d.screw_length_mm == 5
    assert d.screw == "M2 x 5"


def test_center_pocket_only_when_the_center_screw_stands_proud():
    assert derive(params()).center_pocket_depth_mm == 0.0
    proud = derive(params(center_head_height_mm=1.2))
    assert proud.center_pocket_depth_mm == pytest.approx(1.5 + 1.2 + 0.5)
    assert proud.center_pocket_diameter_mm == pytest.approx(6.0)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"shaft_height_mm": 2.0}, "servo case"),
        ({"bolt_circle_mm": 19.0}, "outside the horn"),
        ({"center_head_mm": 11.0}, "centre screw"),
        ({"bolt_size": "M4"}, "bolt_size"),
        ({"bolt_count": 1}, "bolt_count"),
        ({"thickness_mm": 0.8}, "too thin"),
    ],
)
def test_impossible_measurements_are_rejected(change, message):
    with pytest.raises(ValueError, match=message):
        derive(params(**change))


def test_counterbores_stay_above_a_deep_centre_pocket():
    # The measured horn (2026-11-17): M3 holes and a centre screw standing 2 mm proud. The pocket
    # (1.5 + 2.0 + 0.5 = 4.0 mm deep) must stop below the counterbore floors, with material between.
    d = derive(params(bolt_size="M3", bolt_circle_mm=13.6, center_head_height_mm=2.0))
    counterbore_floor = d.web_mm - d.counterbore_depth_mm
    assert counterbore_floor - d.center_pocket_depth_mm == pytest.approx(0.8)


def test_checked_in_servo_file_is_the_measured_horn():
    p = load(Path(__file__).resolve().parents[1] / "servo.toml")
    assert p.measured is True
    d = derive(p)
    assert d.web_mm == pytest.approx(8.1)
    assert d.screw == "M3 x 6"


def test_load_reads_every_field(tmp_path):
    f = tmp_path / "servo.toml"
    f.write_text(
        "measured = true\n"
        "[horn]\n"
        "od_mm = 21.0\nthickness_mm = 2.0\nbolt_count = 4\nbolt_circle_mm = 14.5\n"
        'bolt_size = "M2.5"\ncenter_head_mm = 5.5\ncenter_head_height_mm = 0.4\n'
        "shaft_height_mm = 4.5\n"
    )
    p = load(f)
    assert p.measured is True
    assert p.horn == Horn(21.0, 2.0, 4, 14.5, "M2.5", 5.5, 0.4, 4.5)
