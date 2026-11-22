import { useEffect, useState } from "react";
import { DriveScreen } from "./DriveScreen";
import { forgetToken, takeToken } from "./token";
import { useRobot } from "./useRobot";

const wsUrl = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws`;

export function App() {
  const pair = () =>
    takeToken(window.location.href, (u) => {
      window.history.replaceState(null, "", u);
    });
  const [token, setToken] = useState(pair);
  // A new pairing link opened in this same tab changes only the #fragment, so no page load.
  useEffect(() => {
    const onHash = () => {
      const fresh = pair();
      if (fresh) setToken(fresh);
    };
    window.addEventListener("hashchange", onHash);
    return () => {
      window.removeEventListener("hashchange", onHash);
    };
  }, []);
  if (!token) {
    return (
      <main className="drive">
        <p>
          Open the new link that <code>lab console</code> printed on the robot. This pairing link
          is needed once per browser.
        </p>
      </main>
    );
  }
  return (
    <Connected
      token={token}
      onRejected={() => {
        forgetToken();
        setToken(null);
      }}
    />
  );
}

function Connected({ token, onRejected }: { token: string; onRejected: () => void }) {
  const robot = useRobot(wsUrl, token);
  const rejected = robot.status === "unauthorised";
  useEffect(() => {
    if (rejected) onRejected();
  }, [rejected, onRejected]);
  return (
    <DriveScreen
      send={robot.send}
      status={robot.status}
      state={robot.state}
      refused={robot.refused}
      maxV={robot.welcome?.max_v ?? null}
      maxW={robot.welcome?.max_w ?? null}
    />
  );
}
