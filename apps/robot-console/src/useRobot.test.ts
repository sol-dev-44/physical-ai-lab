import { act, renderHook } from "@testing-library/react";
import { useRobot } from "./useRobot";

class FakeSocket {
  static last: FakeSocket;
  sent: string[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  onclose: ((e: { code: number }) => void) | null = null;
  readyState = 0;
  constructor(public url: string) {
    FakeSocket.last = this;
  }
  send(data: string) {
    this.sent.push(data);
  }
  close() {
    // nothing to release in the fake
  }
}

const make = (url: string) => new FakeSocket(url) as unknown as WebSocket;

describe("useRobot", () => {
  it("says hello with the token when the socket opens", () => {
    renderHook(() => useRobot("ws://robot/ws", "tok", make));
    act(() => {
      FakeSocket.last.onopen?.();
    });
    expect(JSON.parse(FakeSocket.last.sent[0] ?? "{}")).toEqual({ type: "hello", token: "tok" });
  });

  it("keeps the latest welcome and state, and ignores malformed messages", () => {
    const { result } = renderHook(() => useRobot("ws://robot/ws", "tok", make));
    act(() => {
      FakeSocket.last.onopen?.();
      FakeSocket.last.onmessage?.({
        data: JSON.stringify({ type: "welcome", run_id: "r", max_v: 0.3, max_w: 1.5, lease_s: 0.3 }),
      });
      FakeSocket.last.onmessage?.({ data: "{not json" });
    });
    expect(result.current.status).toBe("open");
    expect(result.current.welcome?.max_v).toBe(0.3);
  });

  it("reports a bad token instead of reconnecting", () => {
    const { result } = renderHook(() => useRobot("ws://robot/ws", "bad", make));
    act(() => {
      FakeSocket.last.onclose?.({ code: 4401 });
    });
    expect(result.current.status).toBe("unauthorised");
  });

  it("keeps the same send function across a reconnect", () => {
    vi.useFakeTimers();
    try {
      const { result } = renderHook(() => useRobot("ws://robot/ws", "tok", make));
      const first = result.current.send;
      act(() => {
        FakeSocket.last.onopen?.();
        FakeSocket.last.onclose?.({ code: 1006 });
        vi.advanceTimersByTime(1000);
      });
      expect(result.current.send).toBe(first);
    } finally {
      vi.useRealTimers();
    }
  });
});
