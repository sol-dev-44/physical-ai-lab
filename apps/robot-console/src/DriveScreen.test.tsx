import { fireEvent, render, screen } from "@testing-library/react";
import stateJson from "../../../packages/schema/fixtures/console/valid/server_state.json";
import { DriveScreen } from "./DriveScreen";
import { State } from "./protocol";

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

const props = { refused: null, maxV: 0.3, maxW: 1.5 };

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
});
