import { act, fireEvent, render, screen } from "@testing-library/react";
import stateJson from "../../../packages/schema/fixtures/console/valid/server_state.json";
import { DriveScreen } from "./DriveScreen";
import { type ClientMessage, State } from "./protocol";

const state = State.parse(stateJson);
const real = State.parse({ ...stateJson, fake: false });

const captureOf = Object.getOwnPropertyDescriptor(HTMLElement.prototype, "setPointerCapture");

beforeEach(() => {
  vi.spyOn(Element.prototype, "getBoundingClientRect").mockReturnValue({
    left: 0, top: 0, width: 200, height: 200, right: 200, bottom: 200, x: 0, y: 0, toJSON: () => ({}),
  });
  HTMLElement.prototype.setPointerCapture = () => {
    // jsdom has no pointer capture
  };
});

afterEach(() => {
  vi.restoreAllMocks();
  if (captureOf) Object.defineProperty(HTMLElement.prototype, "setPointerCapture", captureOf);
  else Reflect.deleteProperty(HTMLElement.prototype, "setPointerCapture");
});

const props = { refused: null, maxV: 0.3 as number | null, maxW: 1.5 as number | null };

describe("DriveScreen", () => {
  it("sends stop from the big stop button", () => {
    const send = vi.fn();
    render(<DriveScreen send={send} status="open" state={state} {...props} />);
    fireEvent.click(screen.getByRole("button", { name: /stop/i }));
    expect(send).toHaveBeenCalledWith({ type: "stop" });
  });

  it("never shows a fake e-stop reading as real", () => {
    render(<DriveScreen send={vi.fn()} status="open" state={state} {...props} />);
    expect(screen.getByText(/e-stop: no sensor/i)).toBeInTheDocument();
    expect(screen.queryByText(/e-stop clear/i)).not.toBeInTheDocument();
  });

  it("never shows a fake battery reading as real", () => {
    render(<DriveScreen send={vi.fn()} status="open" state={state} {...props} />);
    expect(screen.getByText(/battery: no sensor/i)).toBeInTheDocument();
    expect(screen.queryByText(/13\.1/)).not.toBeInTheDocument();
  });

  it("shows real readings when the devices are real", () => {
    render(<DriveScreen send={vi.fn()} status="open" state={real} {...props} />);
    expect(screen.getByText(/e-stop clear/i)).toBeInTheDocument();
    expect(screen.getByText(/13\.1 V/)).toBeInTheDocument();
  });

  it("shows when the robot is fake and when the connection is down", () => {
    render(<DriveScreen send={vi.fn()} status="closed" state={state} {...props} />);
    expect(screen.getByText(/fake devices/i)).toBeInTheDocument();
    expect(screen.getByText(/reconnecting/i)).toBeInTheDocument();
  });

  it("shows the last refusal with its rule", () => {
    render(
      <DriveScreen
        send={vi.fn()}
        status="open"
        state={state}
        refused={{ type: "refused", rule: "stop_file", reason: "STOP exists" }}
        maxV={0.3}
        maxW={1.5}
      />,
    );
    expect(screen.getByText(/stop_file/)).toBeInTheDocument();
  });

  it("stops a held stick when the connection drops, and needs a fresh press after reconnecting", () => {
    const send = vi.fn();
    const view = render(<DriveScreen send={send} status="open" state={state} {...props} />);
    fireEvent.pointerDown(screen.getByRole("slider", { name: /joystick/i }), { pointerId: 1, button: 0, buttons: 1, clientX: 100, clientY: 0 });
    expect(send).toHaveBeenCalledWith(expect.objectContaining({ type: "drive" }));
    send.mockClear();

    view.rerender(<DriveScreen send={send} status="closed" state={state} {...props} />);
    expect(send).toHaveBeenCalledWith({ type: "stop" });

    view.rerender(<DriveScreen send={send} status="open" state={state} {...props} />);
    send.mockClear();
    fireEvent.pointerMove(screen.getByRole("slider", { name: /joystick/i }), { pointerId: 1, buttons: 1, clientX: 100, clientY: 0 });
    expect(send).not.toHaveBeenCalled();
  });

  it("the stop button releases a held stick, and the finger must lift and press again", () => {
    vi.useFakeTimers();
    try {
      const send = vi.fn();
      render(<DriveScreen send={send} status="open" state={state} {...props} />);
      const pad = () => screen.getByRole("slider", { name: /joystick/i });
      fireEvent.pointerDown(pad(), { pointerId: 1, button: 0, buttons: 1, clientX: 100, clientY: 0 });
      send.mockClear();

      fireEvent.click(screen.getByRole("button", { name: /stop/i }));
      expect(send.mock.calls).toEqual([[{ type: "stop" }]]); // one stop, not two

      send.mockClear();
      fireEvent.pointerMove(pad(), { pointerId: 1, buttons: 1, clientX: 100, clientY: 0 });
      vi.advanceTimersByTime(500);
      expect(send).not.toHaveBeenCalled();
    } finally {
      vi.useRealTimers();
    }
  });

  it("a finger moving through a reconnect cannot leave the robot driving", () => {
    vi.useFakeTimers();
    try {
      let now = 0;
      vi.spyOn(performance, "now").mockImplementation(() => now);
      let open = true;
      const delivered: ClientMessage[] = [];
      const send = (m: ClientMessage) => {
        if (open) delivered.push(m);
      };
      const pad = () => screen.getByRole("slider", { name: /joystick/i });
      const view = render(<DriveScreen send={send} status="open" state={state} {...props} />);
      fireEvent.pointerDown(pad(), { pointerId: 1, button: 0, buttons: 1, clientX: 100, clientY: 0 });

      open = false; // Wi-Fi drops
      view.rerender(<DriveScreen send={send} status="closed" state={state} {...props} />);
      view.rerender(<DriveScreen send={send} status="connecting" state={state} {...props} />);
      for (let i = 0; i < 10; i++) {
        now += 16;
        fireEvent.pointerMove(pad(), { pointerId: 1, buttons: 1, clientX: 100 + i * 3, clientY: 0 });
      }
      open = true;
      view.rerender(<DriveScreen send={send} status="open" state={state} {...props} />);
      delivered.length = 0;
      fireEvent.pointerUp(pad(), { pointerId: 1 });
      for (let i = 0; i < 20; i++) {
        now += 50;
        act(() => {
          vi.advanceTimersByTime(50);
        });
      }
      expect(delivered).toEqual([]);
    } finally {
      vi.useRealTimers();
    }
  });

  it("does not drive before the welcome gives its limits", () => {
    const send = vi.fn();
    render(<DriveScreen send={send} status="open" state={state} refused={null} maxV={null} maxW={null} />);
    fireEvent.pointerDown(screen.getByRole("slider", { name: /joystick/i }), {
      pointerId: 1, button: 0, buttons: 1, clientX: 100, clientY: 0,
    });
    expect(send).not.toHaveBeenCalled();
  });

  it("does not drive while not connected", () => {
    const send = vi.fn();
    render(<DriveScreen send={send} status="connecting" state={state} {...props} />);
    fireEvent.pointerDown(screen.getByRole("slider", { name: /joystick/i }), {
      pointerId: 1, button: 0, buttons: 1, clientX: 100, clientY: 0,
    });
    expect(send).not.toHaveBeenCalled();
  });

  it("clamps the speed when the welcome lowers the limit", () => {
    const send = vi.fn();
    const view = render(<DriveScreen send={send} status="open" state={state} {...props} />);
    view.rerender(<DriveScreen send={send} status="open" state={state} refused={null} maxV={0.05} maxW={1.5} />);
    fireEvent.pointerDown(screen.getByRole("slider", { name: /joystick/i }), {
      pointerId: 1, button: 0, buttons: 1, clientX: 100, clientY: 0,
    });
    expect(send).toHaveBeenCalledWith(expect.objectContaining({ type: "drive", v: 0.05 }));
  });
});
