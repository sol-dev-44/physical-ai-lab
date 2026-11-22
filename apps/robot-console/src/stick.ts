export type Rect = { left: number; top: number; width: number; height: number };

/** Pointer position to a stick vector in the unit circle: +x right, +y up. */
export function stickVector(rect: Rect, clientX: number, clientY: number): { x: number; y: number } {
  const r = rect.width / 2;
  let x = (clientX - (rect.left + r)) / r;
  let y = -(clientY - (rect.top + rect.height / 2)) / (rect.height / 2);
  const len = Math.hypot(x, y);
  if (len > 1) {
    x /= len;
    y /= len;
  }
  return { x: x + 0, y: y + 0 };
}
