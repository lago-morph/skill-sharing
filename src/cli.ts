#!/usr/bin/env node
import { Command } from "commander";

const program = new Command();

program
  .name("skillctl")
  .description("Inventory, share, and merge AI agent skills.")
  .version("0.1.0");

program
  .command("list")
  .description("List all skills found on this machine.")
  .action(() => {
    console.log("skillctl list — not yet implemented (Iteration 1)");
  });

program
  .command("show <name>")
  .description("Print the resolved skill frontmatter and body.")
  .action((name: string) => {
    console.log(`skillctl show ${name} — not yet implemented (Iteration 1)`);
  });

program.parse();
