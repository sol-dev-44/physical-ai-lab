import { useEffect, useState } from "react";
import { DriveController } from "./driveController";
import { Joystick } from "./Joystick";
import type { ClientMessage, Refused, State } from "./protocol";
import type { Status } from "./useRobot";

type Props = {
  send: (m: ClientMessage) => void;
  status: Status;
  state: State | null;
  refused: Refused | null;
  /** From the welcome; null until it arrives. Nothing drives without it. */
  maxV: number | null;
  maxW: number | null;
};

export function DriveScreen({ send, status, state, refused, maxV, maxW }: Props) {
  const [speed, setSpeed] = useState(Math.min(0.15, maxV ?? 0.15));
  const speedLimit = Math.min(speed, maxV ?? 0); // always inside the welcome's cap
  // `send` from useRobot is stable for the page's life (it follows the current socket), so one
  // controller serves the whole page and seq keeps rising across reconnects. The welcome's
  // limits are applied in place below.
  const [controller] = useState(() => new DriveController(send, { maxW: maxW ?? 0, speedLimit }));

  useEffect(() => {
    controller.setLimits({ maxW: maxW ?? 0, speedLimit });
  }, [controller, maxW, speedLimit]);

  useEffect(() => {
    const id = setInterval(() => {
      controller.tick(performance.now());
    }, 50);
    return () => {
      clearInterval(id);
    };
  }, [controller]);

  // A dropped connection ends the drag: nothing may keep driving across a reconnect.
  useEffect(() => {
    if (status !== "open") controller.release();
  }, [controller, status]);

  // The joystick is re-created on every status change, so a finger that was down across a drop
  // or reconnect needs a fresh press. The Stop button bumps it too, so a finger still on the
  // stick cannot resume driving.
  const [presses, setPresses] = useState(0);
  const [seen, setSeen] = useState(status);
  if (status !== seen) {
    setSeen(status);
    setPresses((n) => n + 1);
  }
  const ready = status === "open" && maxV !== null && maxW !== null;

  return (
    <main className="drive">
      <header className="pills">
        <span className={`pill ${status === "open" ? "ok" : "warn"}`} role="status" aria-live="polite">
          {status === "open" ? "Connected" : status === "unauthorised" ? "Pair again" : "Reconnecting"}
        </span>
        {state?.fake && <span className="pill warn">Fake devices</span>}
        {state && <span className={`pill ${state.lease_alive ? "ok" : ""}`}>{state.lease_alive ? "Driving" : "Idle"}</span>}
        {state && (
          <span className={`pill ${state.fake ? "muted" : ""}`}>
            {state.fake ? "Battery: no sensor" : `${state.battery.volts.toFixed(1)} V`}
          </span>
        )}
        {state?.stop_file && <span className="pill bad">STOP file</span>}
        {state && (
          <span className={`pill ${state.fake ? "muted" : state.estop ? "bad" : "ok"}`}>
            {state.fake ? "E-stop: no sensor" : state.estop ? "E-stop pressed" : "E-stop clear"}
          </span>
        )}
      </header>

      <Joystick
        key={presses}
        onMove={(x, y) => {
          if (ready) controller.hold(x, y, performance.now());
        }}
        onRelease={() => {
          controller.release();
        }}
      />

      <label className="speed">
        Top speed {speed.toFixed(2)} m/s
        <input
          type="range"
          min={0.05}
          max={maxV ?? 0.3}
          disabled={maxV === null}
          step={0.01}
          value={speed}
          onChange={(e) => {
            setSpeed(Number(e.target.value));
          }}
        />
      </label>

      <button
        type="button"
        className="stop"
        onClick={() => {
          // Stop must always reach the robot: release() sends it if a stick was held.
          if (!controller.release()) send({ type: "stop" });
          setPresses((n) => n + 1);
        }}
      >
        Stop
      </button>

      {refused && (
        <p className="refused" role="status">
          Refused by <code>{refused.rule}</code>
          {refused.reason ? `: ${refused.reason}` : ""}
        </p>
      )}
    </main>
  );
}
