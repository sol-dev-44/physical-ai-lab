import { useCallback, useEffect, useRef, useState } from "react";
import { type ClientMessage, type Refused, ServerMessage, type State, type Welcome } from "./protocol";

export type Status = "connecting" | "open" | "closed" | "unauthorised";
const UNAUTHORISED = 4401;
const RETRY_MS = 1000;

const browserSocket = (url: string): WebSocket => new WebSocket(url);

/** One WebSocket to the robot console: says hello, keeps the latest state, reconnects.
 * `send` is stable for the life of the hook, across reconnects. */
export function useRobot(url: string, token: string, makeSocket: (url: string) => WebSocket = browserSocket) {
  const [status, setStatus] = useState<Status>("connecting");
  const [welcome, setWelcome] = useState<Welcome | null>(null);
  const [state, setState] = useState<State | null>(null);
  const [refused, setRefused] = useState<Refused | null>(null);
  const socket = useRef<WebSocket | null>(null);

  useEffect(() => {
    let stopped = false;
    let retry: ReturnType<typeof setTimeout> | undefined;
    let current: WebSocket | null = null;
    const connect = () => {
      const ws = makeSocket(url);
      current = ws;
      socket.current = ws;
      setStatus("connecting");
      ws.onopen = () => {
        ws.send(JSON.stringify({ type: "hello", token }));
        setStatus("open");
      };
      ws.onmessage = (e: MessageEvent<string> | { data: string }) => {
        let data: unknown;
        try {
          data = JSON.parse(e.data);
        } catch {
          return;
        }
        const msg = ServerMessage.safeParse(data);
        if (!msg.success) return;
        if (msg.data.type === "welcome") setWelcome(msg.data);
        else if (msg.data.type === "state") setState(msg.data);
        else setRefused(msg.data);
      };
      ws.onclose = (e: CloseEvent | { code: number }) => {
        if (e.code === UNAUTHORISED) {
          setStatus("unauthorised");
          return;
        }
        setStatus("closed");
        if (!stopped) retry = setTimeout(connect, RETRY_MS);
      };
    };
    connect();
    return () => {
      stopped = true;
      clearTimeout(retry);
      current?.close();
    };
  }, [url, token, makeSocket]);

  const send = useCallback((msg: ClientMessage) => {
    if (socket.current?.readyState === WebSocket.OPEN) socket.current.send(JSON.stringify(msg));
  }, []);

  return { status, welcome, state, refused, send };
}
