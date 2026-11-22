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
});
