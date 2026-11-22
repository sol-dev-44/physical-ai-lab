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
  maxV: number;
  maxW: number;
};

export function DriveScreen({ send, status, state, refused, maxV, maxW }: Props) {
  const [speed, setSpeed] = useState(Math.min(0.15, maxV));
  // `send` from useRobot is stable for the page's life (it follows the current socket), so one
  // controller serves the whole page and seq keeps rising across reconnects. The welcome's
  // limits are applied in place below.
  const [controller] = useState(() => new DriveController(send, { maxW, speedLimit: Math.min(speed, maxV) }));

  useEffect(() => {
    controller.setLimits({ maxW, speedLimit: Math.min(speed, maxV) });
  }, [controller, maxW, maxV, speed]);

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

  // The joystick is re-created for every new connection, so a reconnect needs a fresh press.
  const [connection, setConnection] = useState(0);
  const [seen, setSeen] = useState(status);
  if (status !== seen) {
    setSeen(status);
    if (status === "open") setConnection((n) => n + 1);
  }

  return (
    <main className="drive">
      <header className="pills">
        <span className={`pill ${status === "open" ? "ok" : "warn"}`}>
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
        key={connection}
        onMove={(x, y) => {
          controller.hold(x, y, performance.now());
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
          max={maxV}
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
          send({ type: "stop" });
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
