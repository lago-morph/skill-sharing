import { describe, it, expect } from "vitest";
import { homedir } from "os";
import { join } from "path";
import { codexSkillPaths } from "../src/hosts.js";

describe("codexSkillPaths", () => {
  it("returns two entries: project then user", () => {
    const paths = codexSkillPaths("/some/project");
    expect(paths).toHaveLength(2);
    expect(paths[0].scope).toBe("project");
    expect(paths[1].scope).toBe("user");
  });

  it("project entry points into cwd/.codex/skills", () => {
    const paths = codexSkillPaths("/my/project");
    expect(paths[0].dir).toBe(join("/my/project", ".codex", "skills"));
  });

  it("user entry points into ~/.codex/skills", () => {
    const paths = codexSkillPaths("/irrelevant");
    expect(paths[1].dir).toBe(join(homedir(), ".codex", "skills"));
  });

  it("both entries report host as codexcli", () => {
    const paths = codexSkillPaths("/any");
    expect(paths.every((p) => p.host === "codexcli")).toBe(true);
  });

  it("defaults cwd to process.cwd()", () => {
    const paths = codexSkillPaths();
    expect(paths[0].dir).toBe(join(process.cwd(), ".codex", "skills"));
  });
});
