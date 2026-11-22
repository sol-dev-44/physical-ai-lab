import { type PointerEvent, useCallback, useEffect, useRef, useState } from "react";
import { stickVector } from "./stick";

type Props = { onMove: (x: number, y: number) => void; onRelease: () => void; size?: number };

/** A touch joystick: drag to drive, lift to stop. Pointer capture keeps the drag even when
 * the finger leaves the circle. */
export function Joystick({ onMove, onRelease, size = 220 }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  // The pointer that is driving, in a ref so a late pointermove after pointerup can never
  // restart driving (a dead-man path must not depend on React flushing state).
  const pointer = useRef<number | null>(null);
  // The latest onRelease, so the window listeners below are added once, not every render.
  const releaseRef = useRef(onRelease);
  useEffect(() => {
    releaseRef.current = onRelease;
  }, [onRelease]);
  const [knob, setKnob] = useState({ x: 0, y: 0 });

  const move = (e: PointerEvent) => {
    if (!ref.current) return;
    const v = stickVector(ref.current.getBoundingClientRect(), e.clientX, e.clientY);
    setKnob(v);
    onMove(v.x, v.y);
  };
  const end = useCallback(() => {
    if (pointer.current === null) return;
    pointer.current = null;
    setKnob({ x: 0, y: 0 });
    releaseRef.current();
  }, []);
  // Only the driving finger ends the drag; another finger lifting does not.
  const endPointer = (e: PointerEvent) => {
    if (e.pointerId === pointer.current) end();
  };

  // Hiding the tab or leaving the window releases the stick.
  useEffect(() => {
    const hidden = () => {
      if (document.visibilityState === "hidden") end();
    };
    document.addEventListener("visibilitychange", hidden);
    window.addEventListener("blur", end);
    return () => {
      document.removeEventListener("visibilitychange", hidden);
      window.removeEventListener("blur", end);
    };
  }, [end]);

  return (
    <div
      ref={ref}
      role="slider"
      aria-label="Drive joystick: drag to drive, release to stop"
      aria-valuenow={0}
      aria-valuetext={knob.x || knob.y ? `forward ${knob.y.toFixed(2)}, turn ${knob.x.toFixed(2)}` : "released"}
      tabIndex={0}
      className="joystick"
      style={{ width: size, height: size }}
      onPointerDown={(e) => {
        if (e.button !== 0 || pointer.current !== null) return;
        e.currentTarget.setPointerCapture(e.pointerId);
        pointer.current = e.pointerId;
        move(e);
      }}
      onPointerMove={(e) => {
        if (e.pointerId === pointer.current && e.buttons !== 0) move(e);
      }}
      onPointerUp={endPointer}
      onPointerCancel={endPointer}
      onLostPointerCapture={endPointer}
    >
      <div
        className="knob"
        style={{ transform: `translate(${String(knob.x * size * 0.35)}px, ${String(-knob.y * size * 0.35)}px)` }}
      />
    </div>
  );
}
