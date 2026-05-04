/**
 * Smoke test for Iteration 0.
 *
 * Copies an example skill into a temporary .rulesync/skills/ tree, runs
 * rulesync generate targeting Codex CLI, and verifies the skill lands in
 * .codex/skills/. Cleans up on exit.
 *
 * Usage: npm run smoke
 */

import { mkdtemp, cp, readdir, rm } from "fs/promises";
import { join } from "path";
import { tmpdir } from "os";
import { fileURLToPath } from "url";
import { generateToCodex } from "../src/substrate.js";

const ROOT = join(fileURLToPath(import.meta.url), "..", "..");
const EXAMPLES = join(ROOT, "examples");

async function run(): Promise<void> {
  const tmp = await mkdtemp(join(tmpdir(), "skillctl-smoke-"));
  console.log(`\nSmoke test working dir: ${tmp}\n`);

  try {
    // Set up .rulesync/skills/<name>/SKILL.md
    const skillName = "write-commit-message";
    const rulesyncSkillsDir = join(tmp, ".rulesync", "skills");
    await cp(
      join(EXAMPLES, skillName),
      join(rulesyncSkillsDir, skillName),
      { recursive: true },
    );
    console.log(`Copied examples/${skillName} → .rulesync/skills/${skillName}`);

    // Run rulesync targeting Codex CLI
    console.log("Running rulesync generate --targets codexcli --features skills...");
    await generateToCodex(tmp);

    // Verify output
    const outputDir = join(tmp, ".codex", "skills");
    const entries = await readdir(outputDir).catch(() => [] as string[]);

    if (entries.includes(skillName)) {
      console.log(`\n✓  .codex/skills/${skillName}/ exists — rulesync round-trip works.\n`);
    } else {
      console.error(`\n✗  Expected .codex/skills/${skillName}/ but found: ${entries.join(", ") || "(empty)"}\n`);
      process.exitCode = 1;
    }
  } finally {
    await rm(tmp, { recursive: true, force: true });
    console.log("Cleaned up temp dir.");
  }
}

run().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
