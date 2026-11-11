"""BroadLink IR packet helpers. Pure functions, no device access.

Packet layout: 0x26 (IR), repeat count (extra plays, 0-255), payload length (2 bytes LE),
then pulse/space durations in ticks of 32.84 us; a duration over 255 ticks is 0x00 then
2 bytes big-endian. A learned code holds every frame the remote sent while the button
was down, so one learned "press" can play for seconds. `one_frame` trims it to a single
frame so the caller controls the play time with `repeat`.
"""

from __future__ import annotations

TICK_US = 32.84
GAP_US = 20_000  # a space this long ends a frame
MAX_REPEAT = 255


def decode(packet: bytes) -> list[int]:
    """Pulse/space durations in microseconds."""
    if len(packet) < 4 or packet[0] != 0x26:
        raise ValueError("not a BroadLink IR packet")
    end = min(len(packet), 4 + (packet[2] | packet[3] << 8))
    out: list[int] = []
    i = 4
    while i < end:
        if packet[i] == 0 and i + 2 < end:
            ticks = packet[i + 1] << 8 | packet[i + 2]
            i += 3
        else:
            ticks = packet[i]
            i += 1
        if ticks:
            out.append(round(ticks * TICK_US))
    return out


def encode(pulses: list[int], repeat: int = 0) -> bytes:
    if not 0 <= repeat <= MAX_REPEAT:
        raise ValueError(f"repeat must be 0..{MAX_REPEAT}")
    body = bytearray()
    for us in pulses:
        ticks = max(1, int(us // TICK_US))
        if ticks > 255:
            body += bytes([0, ticks >> 8 & 0xFF, ticks & 0xFF])
        else:
            body.append(ticks)
    return bytes([0x26, repeat, len(body) & 0xFF, len(body) >> 8]) + bytes(body)


def frames(pulses: list[int]) -> list[list[int]]:
    """Split at long spaces (odd index = space; pulses alternate on/off)."""
    out: list[list[int]] = []
    cur: list[int] = []
    for i, us in enumerate(pulses):
        cur.append(us)
        if us >= GAP_US and i % 2 == 1:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def _same(a: list[int], b: list[int], tol: float = 0.25) -> bool:
    return len(a) == len(b) and all(
        abs(x - y) <= tol * max(x, y) for x, y in zip(a, b, strict=True)
    )


def one_frame(packet: bytes) -> list[int]:
    """The button's own frame from a learned code, including the gap after it.

    A held button often sends its command frame a few times, then a generic "still held"
    frame shared by every button (seen on the exp000 robot remote). The very first frame
    may be glitched, captured as the button goes down. So take the first frame that
    repeats; never the most common one, which can be the shared hold frame."""
    fs = frames(decode(packet))
    if len(fs) == 1:
        return fs[0]
    for i, f in enumerate(fs):
        if any(_same(f, g) for g in fs[i + 1 :]):
            return f
    raise ValueError("no frame repeats in this learned code; learn it again")


def duration_s(pulses: list[int]) -> float:
    return sum(pulses) / 1_000_000
