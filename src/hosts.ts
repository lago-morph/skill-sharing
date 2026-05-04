/**
 * Path registry — one entry per supported host.
 * Prototype scope: Codex CLI only.
 * To add a host, append entries here and extend substrate.ts targets.
 */

import { homedir } from "os";
import { join } from "path";

export interface SkillPath {
  host: "codexcli";
  scope: "user" | "project";
  /** Absolute path to the skills directory for this scope */
  dir: string;
}

export function codexSkillPaths(cwd = process.cwd()): SkillPath[] {
  return [
    {
      host: "codexcli",
      scope: "project",
      dir: join(cwd, ".codex", "skills"),
    },
    {
      host: "codexcli",
      scope: "user",
      dir: join(homedir(), ".codex", "skills"),
    },
  ];
}
