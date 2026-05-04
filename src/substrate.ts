/**
 * Thin wrapper around rulesync so the rest of skillctl never imports
 * rulesync directly. If we ever need to swap the substrate out, this is
 * the only file that changes.
 */

import { generate } from "rulesync";
import type { GenerateOptions } from "rulesync";

export type { GenerateOptions };

/**
 * Fan out skills from a rulesync input root to one or more output roots
 * targeting only the Codex CLI.
 *
 * @param inputRoot  Directory containing `.rulesync/`
 * @param outputRoots  Directories to write `.codex/` into (defaults to inputRoot)
 */
export async function generateToCodex(
  inputRoot: string,
  outputRoots?: string[],
): Promise<void> {
  await generate({
    inputRoot,
    outputRoots: outputRoots ?? [inputRoot],
    targets: ["codexcli"],
    features: ["skills"],
    silent: false,
  });
}
