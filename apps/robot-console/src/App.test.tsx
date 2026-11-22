import { act, render, screen } from "@testing-library/react";
import { App } from "./App";

class FakeSocket {
  static OPEN = 1;
  static all: FakeSocket[] = [];
  readyState = 0;
  onopen: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  onclose: ((e: { code: number }) => void) | null = null;
  constructor(public url: string) {
    FakeSocket.all.push(this);
  }
  send() {
    // not needed
  }
  close() {
    // not needed
  }
}

beforeEach(() => {
  FakeSocket.all = [];
  localStorage.clear();
  window.history.replaceState(null, "", "/");
  vi.stubGlobal("WebSocket", FakeSocket);
});
afterEach(() => {
  vi.unstubAllGlobals();
});

describe("App", () => {
  it("asks for the pairing link when never paired", () => {
    render(<App />);
    expect(screen.getByText(/pairing link/i)).toBeInTheDocument();
    expect(FakeSocket.all).toHaveLength(0);
  });

  it("forgets a rejected token and asks for the new link", () => {
    localStorage.setItem("robot-token", "old");
    render(<App />);
    expect(FakeSocket.all).toHaveLength(1);
    act(() => {
      FakeSocket.all[0]?.onclose?.({ code: 4401 });
    });
    expect(localStorage.getItem("robot-token")).toBeNull();
    expect(screen.getByText(/new link/i)).toBeInTheDocument();
  });

  it("keeps the token and reconnects after a hello timeout (4408)", () => {
    vi.useFakeTimers();
    try {
      localStorage.setItem("robot-token", "good");
      render(<App />);
      act(() => {
        FakeSocket.all[0]?.onclose?.({ code: 4408 });
        vi.advanceTimersByTime(1000);
      });
      expect(localStorage.getItem("robot-token")).toBe("good");
      expect(FakeSocket.all).toHaveLength(2);
    } finally {
      vi.useRealTimers();
    }
  });

  it("pairs from a new link opened in the same tab (only the fragment changes)", () => {
    localStorage.setItem("robot-token", "old");
    render(<App />);
    act(() => {
      FakeSocket.all[0]?.onclose?.({ code: 4401 });
    });
    expect(screen.getByText(/new link/i)).toBeInTheDocument();
    act(() => {
      window.location.hash = "#token=fresh";
      window.dispatchEvent(new HashChangeEvent("hashchange"));
    });
    expect(localStorage.getItem("robot-token")).toBe("fresh");
    expect(screen.queryByText(/new link/i)).not.toBeInTheDocument();
    expect(FakeSocket.all.length).toBeGreaterThan(1);
  });
});
