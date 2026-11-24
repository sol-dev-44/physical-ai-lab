"""The deck fit coupon's numbers. No CadQuery needed."""

import pytest
from exp003_cad.params import (
    M25_NUT_MM,
    M25_STUD_MM,
    DeckCoupon,
    derive_deck_coupon,
)


def test_jack_holes_step_up_in_size():
    d = derive_deck_coupon(DeckCoupon())
    sizes = [dia for _, _, dia in d.jacks]
    # Printed for a reading (7.75 mm) later withdrawn: the deck's hole now follows JACK_THREAD_MM.
    assert sizes == sorted(sizes) and len(set(sizes)) == 3


def test_rocker_cutouts_are_snug_then_loose():
    d = derive_deck_coupon(DeckCoupon())
    (_, _, l1, s1), (_, _, l2, s2) = d.rockers
    assert (l1, s1) == pytest.approx((19.4, 13.4))
    assert (l2, s2) == pytest.approx((19.7, 13.7))


def test_standoff_stud_reaches_the_nut_but_stops_above_the_bed():
    d = derive_deck_coupon(DeckCoupon())
    roof = d.boss_height_mm - d.nut_pocket_depth_mm
    engaged = M25_STUD_MM - roof
    assert engaged == pytest.approx(M25_NUT_MM)  # the full nut
    tip_above_bed = d.nut_pocket_depth_mm - M25_NUT_MM
    assert tip_above_bed == pytest.approx(1.0)


def test_channel_fits_the_uctronics_with_slip_clearance():
    d = derive_deck_coupon(DeckCoupon())
    assert d.channel_inner_mm == pytest.approx(27.6)
