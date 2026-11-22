import { useCallback, useEffect, useRef, useState } from "react";
import { type ClientMessage, type Refused, ServerMessage, type State, type Welcome } from "./protocol";

export type Status = "connecting" | "open" | "closed" | "unauthorised";
const UNAUTHORISED = 4401;
const RETRY_MS = 1000;

const browserSocket = (url: string): WebSocket => new WebSocket(url);

/** One WebSocket to the robot console: says hello, goes "open" on the welcome, keeps the latest state, reconnects.
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
      // A discarded socket (an earlier effect run, or one replaced by a reconnect) may still
      // fire late events; they must not touch the live state.
      ws.onopen = () => {
        if (ws !== current) return;
        ws.send(JSON.stringify({ type: "hello", token }));
      };
      ws.onmessage = (e: MessageEvent<string> | { data: string }) => {
        if (ws !== current) return;
        let data: unknown;
        try {
          data = JSON.parse(e.data);
        } catch {
          return;
        }
        const msg = ServerMessage.safeParse(data);
        if (!msg.success) return;
        if (msg.data.type === "welcome") {
          setWelcome(msg.data);
          setRefused(null);
          setStatus("open"); // connected and authorised: only now may the stick drive
        }
        else if (msg.data.type === "state") {
          setState(msg.data);
          if (msg.data.moving) setRefused(null); // it is driving again: the old refusal is stale
        }
        else setRefused(msg.data);
      };
      ws.onclose = (e: CloseEvent | { code: number }) => {
        if (ws !== current) return;
        setWelcome(null);
        setState(null);
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
      if (current) {
        current.onopen = null;
        current.onmessage = null;
        current.onclose = null;
        current.close();
      }
      current = null;
    };
  }, [url, token, makeSocket]);

  const send = useCallback((msg: ClientMessage) => {
    if (socket.current?.readyState === WebSocket.OPEN) socket.current.send(JSON.stringify(msg));
  }, []);

  return { status, welcome, state, refused, send };
}
