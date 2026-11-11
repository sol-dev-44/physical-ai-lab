/** The Wall-e Robot panel: shows only the moves the agent registered, and queues {seconds}. */
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

vi.mock("../app/admin/(console)/actions", () => ({ requestCommand: vi.fn() }));
const { RobotPanel } = await import("../app/admin/(console)/robot-panel");

const tool = (name: string) => ({ name, description: "", requires_confirmation: false, args_schema: {} });

describe("RobotPanel", () => {
  it("renders nothing until the agent registers a robot tool", () => {
    expect(renderToStaticMarkup(<RobotPanel tools={[tool("tv.power")]} />)).toBe("");
  });

  it("labels the panel and offers forward and reverse", () => {
    const html = renderToStaticMarkup(<RobotPanel tools={[tool("robot.forward"), tool("robot.reverse")]} />);
    expect(html).toContain("Wall-e Robot");
    const buttons = html.match(/<button[^>]*>/g) ?? [];
    expect(buttons).toHaveLength(2);
    for (const [b, tool] of buttons.map((b, i) => [b, ["robot.forward", "robot.reverse"][i]])) {
      expect(b).toContain('name="tool"');
      expect(b).toContain(`value="${tool}"`);
    }
    expect(html).toContain('name="args" value="{&quot;seconds&quot;:1}"');
    expect(html).toContain('max="3"');
  });

  it("hides a move the agent did not register", () => {
    const html = renderToStaticMarkup(<RobotPanel tools={[tool("robot.forward")]} />);
    expect(html).not.toContain("robot.reverse");
  });
});
