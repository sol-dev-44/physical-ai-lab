import { fireEvent, render, screen } from "@testing-library/react";
import { Joystick } from "./Joystick";

const original = Object.getOwnPropertyDescriptor(HTMLElement.prototype, "setPointerCapture");

afterEach(() => {
  if (original) Object.defineProperty(HTMLElement.prototype, "setPointerCapture", original);
  else Reflect.deleteProperty(HTMLElement.prototype, "setPointerCapture");
  Reflect.deleteProperty(document, "visibilityState"); // back to the prototype's getter
});

function setup() {
  const onMove = vi.fn();
  const onRelease = vi.fn();
  const view = render(<Joystick onMove={onMove} onRelease={onRelease} />);
  const el = screen.getByRole("slider");
  el.getBoundingClientRect = () => ({
    left: 0, top: 0, width: 200, height: 200, right: 200, bottom: 200, x: 0, y: 0, toJSON: () => ({}),
  });
  HTMLElement.prototype.setPointerCapture = () => {
    // jsdom has no pointer capture
  };
  return { el, onMove, onRelease, view };
}

const press = (el: HTMLElement, init: PointerEventInit = {}) =>
  fireEvent.pointerDown(el, { pointerId: 1, button: 0, buttons: 1, clientX: 100, clientY: 0, ...init });

describe("Joystick", () => {
  it("drives from the pointer position", () => {
    const { el, onMove } = setup();
    press(el);
    expect(onMove).toHaveBeenCalledWith(0, 1);
  });

  it("a move after release never drives", () => {
    const { el, onMove, onRelease } = setup();
    press(el);
    fireEvent.pointerUp(el, { pointerId: 1 });
    onMove.mockClear();
    fireEvent.pointerMove(el, { pointerId: 1, buttons: 1, clientX: 100, clientY: 0 });
    expect(onMove).not.toHaveBeenCalled();
    expect(onRelease).toHaveBeenCalledTimes(1);
  });

  it("only the primary button starts driving", () => {
    const { el, onMove } = setup();
    press(el, { button: 2, buttons: 2 });
    expect(onMove).not.toHaveBeenCalled();
  });

  it("another finger lifting does not release the driving one", () => {
    const { el, onRelease } = setup();
    press(el);
    fireEvent.pointerUp(el, { pointerId: 2 });
    expect(onRelease).not.toHaveBeenCalled();
  });

  it("losing pointer capture releases", () => {
    const { el, onRelease } = setup();
    press(el);
    fireEvent.lostPointerCapture(el, { pointerId: 1 });
    expect(onRelease).toHaveBeenCalledTimes(1);
  });

  it("hiding the tab releases a held stick", () => {
    const { el, onRelease } = setup();
    press(el);
    Object.defineProperty(document, "visibilityState", { value: "hidden", configurable: true });
    fireEvent(document, new Event("visibilitychange"));
    expect(onRelease).toHaveBeenCalledTimes(1);
  });

  it("the window losing focus releases a held stick", () => {
    const { el, onRelease } = setup();
    press(el);
    fireEvent.blur(window);
    expect(onRelease).toHaveBeenCalledTimes(1);
  });

  it("calls the latest onRelease after a re-render", () => {
    const { el, onRelease, view } = setup();
    const next = vi.fn();
    press(el);
    view.rerender(<Joystick onMove={vi.fn()} onRelease={next} />);
    fireEvent.blur(window);
    expect(next).toHaveBeenCalledTimes(1);
    expect(onRelease).not.toHaveBeenCalled();
  });

  it("does not re-add the window listeners on every render", () => {
    const { view } = setup();
    const add = vi.spyOn(window, "addEventListener");
    view.rerender(<Joystick onMove={vi.fn()} onRelease={vi.fn()} />);
    expect(add).not.toHaveBeenCalled();
    add.mockRestore();
  });

  it("pointercancel releases", () => {
    const { el, onRelease } = setup();
    press(el);
    fireEvent.pointerCancel(el, { pointerId: 1 });
    expect(onRelease).toHaveBeenCalledTimes(1);
  });

  it("becoming visible does not release", () => {
    const { el, onRelease } = setup();
    press(el);
    Object.defineProperty(document, "visibilityState", { value: "visible", configurable: true });
    fireEvent(document, new Event("visibilitychange"));
    expect(onRelease).not.toHaveBeenCalled();
  });

  it("a move from the driving pointer with no buttons down releases", () => {
    const { el, onRelease } = setup();
    press(el);
    fireEvent.pointerMove(el, { pointerId: 1, buttons: 0, clientX: 100, clientY: 0 });
    expect(onRelease).toHaveBeenCalledTimes(1);
  });

  it("unmounting while held releases; unmounting idle does not", () => {
    const held = setup();
    press(held.el);
    held.view.unmount();
    expect(held.onRelease).toHaveBeenCalledTimes(1);
    const idle = setup();
    idle.view.unmount();
    expect(idle.onRelease).not.toHaveBeenCalled();
  });
});
