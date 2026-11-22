import { DriveScreen } from "./DriveScreen";
import { takeToken } from "./token";
import { useRobot } from "./useRobot";

const token = takeToken(window.location.href, (u) => {
  window.history.replaceState(null, "", u);
});
const wsUrl = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws`;

export function App() {
  if (!token) {
    return (
      <main className="drive">
        <p>
          Open the pairing link that <code>lab console</code> printed on the robot.
        </p>
      </main>
    );
  }
  return <Connected token={token} />;
}

function Connected({ token }: { token: string }) {
  const robot = useRobot(wsUrl, token);
  return (
    <DriveScreen
      send={robot.send}
      status={robot.status}
      state={robot.state}
      refused={robot.refused}
      maxV={robot.welcome?.max_v ?? 0.3}
      maxW={robot.welcome?.max_w ?? 1.5}
    />
  );
}
