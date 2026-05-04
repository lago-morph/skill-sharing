import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock rulesync before importing substrate
vi.mock("rulesync", () => ({
  generate: vi.fn().mockResolvedValue(undefined),
}));

import { generate } from "rulesync";
import { generateToCodex } from "../src/substrate.js";

describe("generateToCodex", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls rulesync generate with codexcli target and skills feature", async () => {
    await generateToCodex("/some/root");

    expect(generate).toHaveBeenCalledOnce();
    expect(generate).toHaveBeenCalledWith(
      expect.objectContaining({
        inputRoot: "/some/root",
        targets: ["codexcli"],
        features: ["skills"],
      }),
    );
  });

  it("defaults outputRoots to inputRoot when not specified", async () => {
    await generateToCodex("/my/root");

    expect(generate).toHaveBeenCalledWith(
      expect.objectContaining({
        outputRoots: ["/my/root"],
      }),
    );
  });

  it("passes explicit outputRoots through to rulesync", async () => {
    await generateToCodex("/input", ["/out-a", "/out-b"]);

    expect(generate).toHaveBeenCalledWith(
      expect.objectContaining({
        inputRoot: "/input",
        outputRoots: ["/out-a", "/out-b"],
      }),
    );
  });
});
