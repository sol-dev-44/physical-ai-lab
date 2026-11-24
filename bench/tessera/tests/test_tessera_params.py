"""Tessera's numbers. No CadQuery needed."""

import math

import pytest
from tessera_cad.params import (
    FIRST_PIECE_CUPS,
    TEST_KEY_CLEARANCES,
    Grid,
    Joint,
    body,
    boss_intrusion,
    boss_size,
    bowtie,
    cavity,
    flank_play,
    half_width,
    module_height,
    ribs,
    sockets,
)

G, J = Grid(), Joint()


def test_modules_leave_half_a_millimetre_between_neighbours():
    a = body(G, 1, 1)
    b = body(G, 1, 1)
    # b sits one cell to the right of a
    assert (b[0] + G.unit_mm) - a[1] == pytest.approx(2 * G.gap_mm)
    assert a[1] - a[0] == pytest.approx(51.5)
    assert a[1] - a[0] >= 2 * 25.4  # owner: the smallest cup is at least 2 in square


def test_one_socket_per_outside_cell_edge():
    assert len(sockets(G, 1, 1)) == 4
    assert len(sockets(G, 2, 3)) == 2 * (2 + 3)
    for s in sockets(G, 2, 3):
        # every socket sits mid-cell, so any two modules' sockets face each other
        along = s.at[0] if s.normal[0] == 0 else s.at[1]
        assert (along / G.unit_mm) % 1 == pytest.approx(0.5)


def test_bowtie_neck_sits_on_the_joint_line_and_flares_out():
    pts = bowtie(J, G)
    assert max(abs(x) for x, _ in pts) == pytest.approx(G.gap_mm + J.depth_mm)
    assert half_width(J, G, 0) * 2 == pytest.approx(J.neck_mm)
    assert half_width(J, G, G.gap_mm + J.depth_mm) * 2 == pytest.approx(J.end_mm)
    flank = math.degrees(math.atan((J.end_mm - J.neck_mm) / 2 / (G.gap_mm + J.depth_mm)))
    assert 10 < flank < 20  # steep enough to lock, shallow enough to print and slide


def _flank_gap(key, sock):
    """Perpendicular distance between the key's flank and the socket's (right upper flank)."""
    (x0, y0), (x1, y1) = sock[4], sock[3]  # neck to end, upper right flank
    px, py = key[3]
    return abs((y1 - y0) * px - (x1 - x0) * py + x1 * y0 - y1 * x0) / math.hypot(x1 - x0, y1 - y0)


def test_key_is_smaller_than_the_socket_by_its_clearance_all_round():
    for c in TEST_KEY_CLEARANCES:
        k, s = bowtie(J, G, c), bowtie(J, G)
        assert abs(s[2][0]) - abs(k[2][0]) == pytest.approx(c)  # end faces
        assert _flank_gap(k, s) == pytest.approx(c)  # slanted flanks, square to the face


def test_key_bridges_the_gap_with_plenty_in_each_socket():
    reach = bowtie(J, G, J.key_clearance_mm)[2][0]
    in_socket = reach - G.gap_mm
    assert in_socket > 6.0


def test_bosses_leave_the_cup_usable():
    w, d = boss_size(G, J)
    assert w == pytest.approx(16.2)
    assert boss_intrusion(G, J) == pytest.approx(6.1)
    x0, x1, _, _ = cavity(G, 1, 1)
    assert (x1 - x0) - 2 * boss_intrusion(G, J) > 35  # clear between opposite bosses


def test_bosses_never_reach_the_corners():
    w, _ = boss_size(G, J)
    # boss edge to the cell corner on the outer face
    assert G.unit_mm / 2 - w / 2 - G.gap_mm > G.wall_mm + G.corner_r_mm


def test_heights_come_in_steps():
    assert module_height(G, 2) == 52
    with pytest.raises(ValueError):
        module_height(G, 6)


def test_first_piece_cups_have_labels_and_serials():
    assert [c.label for c in FIRST_PIECE_CUPS] == ["TIPS", "SPARE"]
    assert [c.serial for c in FIRST_PIECE_CUPS] == [1, 2]


def test_plain_keys_always_leave_play():
    # the shallow flanks multiply clearance by about 3.5: why plate 1's keys all rattled
    assert flank_play(J, G, 0.10) == pytest.approx(0.90, abs=0.01)
    assert flank_play(J, G, 0.05) == pytest.approx(0.45, abs=0.01)
    assert flank_play(J, G, 0.0) == 0.0


def _beyond_socket_wall(c, sx, sy):
    """Signed distance from the socket flank (clearance 0) to the rib's crest, outward +."""
    reach = G.gap_mm + J.depth_mm
    x0, y0 = 0.0, sy * J.neck_mm / 2
    x1, y1 = sx * reach, sy * J.end_mm / 2
    tx, ty = x1 - x0, y1 - y0
    n = math.hypot(tx, ty)
    # the flank's normal that points away from the key's centre
    nx, ny = (-ty / n, tx / n) if (sx * sy) > 0 else (ty / n, -tx / n)
    d_centre = (c[0] - x0) * nx + (c[1] - y0) * ny
    return d_centre + J.rib_radius_mm


@pytest.mark.parametrize("interference", [0.10, 0.20])
def test_each_rib_crest_stands_its_interference_past_the_socket_wall(interference):
    cs = ribs(J, G, interference)
    assert len(cs) == 4
    for c, (sx, sy) in zip(cs, [(1, 1), (1, -1), (-1, 1), (-1, -1)], strict=True):
        assert _beyond_socket_wall(c, sx, sy) == pytest.approx(interference)
        # inside the socket, not in the gap between modules, and short of the socket's end
        assert G.gap_mm + J.rib_radius_mm < abs(c[0]) < G.gap_mm + J.depth_mm - J.rib_radius_mm


def test_layout_fills_the_field_once_and_keeps_room_to_grow():
    from tessera_cad.layout import FIELD_COLS, FIELD_ROWS, GROW, LAYOUT, cells

    taken = [c for p in LAYOUT for c in cells(p)]
    assert len(taken) == len(set(taken)), "two modules share a cell"
    assert not set(taken) & set(GROW)
    field = {(c, r) for c in range(FIELD_COLS) for r in range(FIELD_ROWS)}
    assert set(taken) | set(GROW) == field
    assert [p.name for p in LAYOUT if p.status == "printed"] == ["TIPS", "SPARE"]


def test_layout_puts_tall_at_the_back_and_heat_away_from_the_alcohol():
    from tessera_cad.layout import LAYOUT

    by = {p.name: p for p in LAYOUT}
    assert all(p.steps <= 2 for p in LAYOUT if p.row == 0)  # front row 52 mm or lower
    assert by["HEAT GUN"].col == 0 and by["ALCOHOL"].col + by["ALCOHOL"].nx == 9
    assert by["HEAT GUN"].material == "PETG"


@pytest.mark.parametrize(
    ("name", "across_mm"),
    [("SOLDER", 61.0), ("ALCOHOL", math.hypot(63.8, 63.8)), ("HEAT GUN", 45.0)],
)
def test_round_and_square_things_clear_the_socket_bosses(name, across_mm):
    from tessera_cad.layout import LAYOUT

    p = next(p for p in LAYOUT if p.name == name)
    w, d = boss_size(G, J)
    x0, x1, y0, y1 = cavity(G, p.nx, p.ny)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    room = min(cx - x0, cy - y0)
    for s in sockets(G, p.nx, p.ny):
        (sx, sy), (nx, ny) = s.at, s.normal
        if nx == 0:
            bx = (sx - w / 2, sx + w / 2)
            by = (sy, sy + d) if ny < 0 else (sy - d, sy)
        else:
            by = (sy - w / 2, sy + w / 2)
            bx = (sx, sx + d) if nx < 0 else (sx - d, sx)
        px, py = min(max(cx, bx[0]), bx[1]), min(max(cy, by[0]), by[1])
        room = min(room, math.hypot(cx - px, cy - py))
    assert across_mm < 2 * room
