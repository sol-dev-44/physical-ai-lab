"""Checks on the tire's sizing against the rim. No CadQuery needed."""

from pathlib import Path

import pytest
from exp003_cad.params import Horn, HubParams, Tire, derive_tire, load_tire

P = HubParams(horn=Horn(19.9, 2.08, 4, 13.6, "M3", 5.0, 2.0, 4.0, 2.0), measured=True)


def test_default_tire_makes_a_120_mm_wheel_that_grips_the_rim():
    d = derive_tire(P, Tire())
    assert d.rim_seat_od_mm == 108.0
    assert d.bore_mm == pytest.approx(107.0)
    assert d.tread_mm == pytest.approx(6.5)
    assert d.grip_stretch == pytest.approx(108 / 107 - 1)  # just under 1%
    # The lips clear the 111 mm flanges by 0.2 mm a side and keep 4.3 mm of rubber over them.
    assert d.lip_bore_mm == pytest.approx(111.4)
    assert d.over_flange_mm == pytest.approx(4.3)
    # Rolling the 107 mm bore over a 111 mm flange: under 4%, which TPU 95A takes by hand.
    assert d.mount_stretch == pytest.approx(111 / 107 - 1)
    assert d.mount_stretch < 0.04


def test_bore_follows_a_measured_rim():
    d = derive_tire(P, Tire(rim_measured_od_mm=107.8))
    assert d.bore_mm == pytest.approx(106.8)


@pytest.mark.parametrize(
    ("tire", "message"),
    [
        (Tire(rim_measured_od_mm=106.0), "re-measure"),
        (Tire(interference_mm=-0.5), "spins on the rim"),
        (Tire(od_mm=116.0), "over the flanges"),
        (Tire(edge_chamfer_mm=4.5), "cut through the lip"),
        (Tire(interference_mm=3.0), "stretch"),
    ],
)
def test_unworkable_tires_are_rejected(tire, message):
    with pytest.raises(ValueError, match=message):
        derive_tire(P, tire)


def test_checked_in_rim_reading_sizes_the_bore():
    # 2026-11-19: the printed hub's top flange read 110.6 mm, so the seat is 107.6.
    t = load_tire(Path(__file__).resolve().parents[1] / "servo.toml")
    assert t.rim_measured_od_mm == pytest.approx(107.6)
    d = derive_tire(P, t)
    assert d.bore_mm == pytest.approx(106.6)
    assert d.lip_bore_mm == pytest.approx(110.6 + 0.4)
    assert d.tread_mm == pytest.approx(6.7)


def test_load_tire_without_a_tire_table_uses_the_design_rim(tmp_path):
    f = tmp_path / "servo.toml"
    f.write_text("measured = true\n")
    assert load_tire(f) == Tire()
