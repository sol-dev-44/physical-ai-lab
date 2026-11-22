import { act, renderHook } from "@testing-library/react";
import { StrictMode } from "react";
import stateJson from "../../../packages/schema/fixtures/console/valid/server_state.json";
import { useRobot } from "./useRobot";

class FakeSocket {
  static all: FakeSocket[] = [];
  static get last(): FakeSocket {
    const s = FakeSocket.all[FakeSocket.all.length - 1];
    if (!s) throw new Error("no socket yet");
    return s;
  }
  sent: string[] = [];
  closed = false;
  onopen: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  onclose: ((e: { code: number }) => void) | null = null;
  readyState = 0;
  constructor(public url: string) {
    FakeSocket.all.push(this);
  }
  send(data: string) {
    this.sent.push(data);
  }
  close() {
    this.closed = true;
  }
  open() {
    this.readyState = 1;
    this.onopen?.();
  }
  say(msg: unknown) {
    this.onmessage?.({ data: JSON.stringify(msg) });
  }
}

const make = (url: string) => new FakeSocket(url) as unknown as WebSocket;
const types = (s: FakeSocket) => s.sent.map((m) => (JSON.parse(m) as { type: string }).type);
const welcome = { type: "welcome", run_id: "r", max_v: 0.3, max_w: 1.5, lease_s: 0.3 };

beforeEach(() => {
  FakeSocket.all = [];
});
afterEach(() => {
  vi.useRealTimers();
});

describe("useRobot", () => {
  it("says hello with the token when the socket opens", () => {
    renderHook(() => useRobot("ws://robot/ws", "tok", make));
    act(() => {
      FakeSocket.last.open();
    });
    expect(JSON.parse(FakeSocket.last.sent[0] ?? "{}")).toEqual({ type: "hello", token: "tok" });
  });

  it("is open only once the welcome arrives, and keeps it; malformed messages are ignored", () => {
    const { result } = renderHook(() => useRobot("ws://robot/ws", "tok", make));
    act(() => {
      FakeSocket.last.open();
    });
    expect(result.current.status).toBe("connecting");
    act(() => {
      FakeSocket.last.say(welcome);
      FakeSocket.last.onmessage?.({ data: "{not json" });
    });
    expect(result.current.status).toBe("open");
    expect(result.current.welcome?.max_v).toBe(0.3);
  });

  it("clears the welcome when the connection closes", () => {
    const { result } = renderHook(() => useRobot("ws://robot/ws", "tok", make));
    act(() => {
      FakeSocket.last.open();
      FakeSocket.last.say(welcome);
      FakeSocket.last.onclose?.({ code: 1006 });
    });
    expect(result.current.status).toBe("closed");
    expect(result.current.welcome).toBeNull();
  });

  it("stores the last refusal", () => {
    const { result } = renderHook(() => useRobot("ws://robot/ws", "tok", make));
    act(() => {
      FakeSocket.last.say({ type: "refused", rule: "stop_file", reason: "STOP exists" });
    });
    expect(result.current.refused?.rule).toBe("stop_file");
  });

  it("clears the refusal on a welcome and when a state shows the robot moving", () => {
    const { result } = renderHook(() => useRobot("ws://robot/ws", "tok", make));
    const refuse = () => {
      FakeSocket.last.say({ type: "refused", rule: "stop_file", reason: "STOP exists" });
    };
    act(() => {
      refuse();
    });
    act(() => {
      FakeSocket.last.say(welcome);
    });
    expect(result.current.refused).toBeNull();
    act(() => {
      refuse();
      FakeSocket.last.say({ ...stateJson, moving: false });
    });
    expect(result.current.refused?.rule).toBe("stop_file");
    act(() => {
      FakeSocket.last.say({ ...stateJson, moving: true });
    });
    expect(result.current.refused).toBeNull();
  });

  it("reports a bad token and never reconnects", () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useRobot("ws://robot/ws", "bad", make));
    act(() => {
      FakeSocket.last.onclose?.({ code: 4401 });
      vi.advanceTimersByTime(10_000);
    });
    expect(result.current.status).toBe("unauthorised");
    expect(FakeSocket.all).toHaveLength(1);
  });

  it("creates no socket when unmounted during a retry wait", () => {
    vi.useFakeTimers();
    const { unmount } = renderHook(() => useRobot("ws://robot/ws", "tok", make));
    act(() => {
      FakeSocket.last.onclose?.({ code: 1006 });
    });
    unmount();
    act(() => {
      vi.advanceTimersByTime(10_000);
    });
    expect(FakeSocket.all).toHaveLength(1);
  });

  it("drops send unless the socket is open, and sends on the new socket after a reconnect", () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useRobot("ws://robot/ws", "tok", make));
    const first = result.current.send;
    const a = FakeSocket.last;
    act(() => {
      first({ type: "stop" });
    });
    expect(a.sent).toEqual([]); // still connecting
    act(() => {
      a.open();
    });
    act(() => {
      first({ type: "stop" });
    });
    expect(types(a)).toEqual(["hello", "stop"]);
    act(() => {
      a.readyState = 3;
      a.onclose?.({ code: 1006 });
      vi.advanceTimersByTime(1000);
    });
    const b = FakeSocket.last;
    expect(b).not.toBe(a);
    act(() => {
      b.open();
    });
    act(() => {
      first({ type: "stop" });
    });
    expect(result.current.send).toBe(first);
    expect(types(b)).toEqual(["hello", "stop"]);
    expect(a.sent).toHaveLength(2);
  });

  it("ignores a late close or message from a discarded socket", () => {
    const { result } = renderHook(() => useRobot("ws://r/ws", "t", make), { wrapper: StrictMode });
    expect(FakeSocket.all).toHaveLength(2);
    const [old, live] = FakeSocket.all as [FakeSocket, FakeSocket];
    act(() => {
      live.open();
      live.say(welcome);
    });
    act(() => {
      old.onclose?.({ code: 1006 });
      old.say({ type: "refused", rule: "ghost" });
    });
    expect(result.current.status).toBe("open");
    expect(result.current.refused).toBeNull();
  });
});
