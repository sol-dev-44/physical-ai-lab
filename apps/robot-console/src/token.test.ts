import { takeToken } from "./token";

describe("takeToken", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("moves the token from the pairing link into local storage", () => {
    const replace = vi.fn();
    expect(takeToken("http://robot.local:8080/#token=abc", replace)).toBe("abc");
    expect(localStorage.getItem("robot-token")).toBe("abc");
    expect(replace).toHaveBeenCalledWith("http://robot.local:8080/");
  });

  it("falls back to the stored token", () => {
    localStorage.setItem("robot-token", "kept");
    expect(takeToken("http://robot.local:8080/", vi.fn())).toBe("kept");
  });

  it("is null when the browser was never paired", () => {
    expect(takeToken("http://robot.local:8080/", vi.fn())).toBeNull();
  });
});
