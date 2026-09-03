---
name: osct-init
description: Set up the Open Source Contribution Toolkit in a repository - create the .osct working tree, seed the issue templates if the project has none, keep both out of git, and install and index CodeGraph. Use when asked to run osct init, set up osct, or initialise the toolkit in a project.
---

# Setting up a repository

One script does the parts that are the same everywhere. What is left needs the
repo in front of you: the areas the project divides into, and the documentation
conventions it already follows.

Run it once per repository. It is safe to run again; nothing already present is
overwritten.

## 1. Run the script

Resolve `<osct-init-skill>` to the directory containing this `SKILL.md`, then run:

```bash
bash "<osct-init-skill>/scripts/init.sh" --target <agent>
```

Use `codex` as the target in Codex and `claude` in Claude Code.

It prints what it did, line by line. In order:

- Creates `.osct/` with `docs/`, `issue-ideas/`, `filed/`, `prs/` and
  `reviews/` and `review-replies/`, and seeds `.osct/README.md` and the issue-ideas index.
- Adds `.osct/` and `.codegraph/` to `.git/info/exclude`, not to `.gitignore`,
  which is shared with everybody else on the project.
- Writes `.github/ISSUE_TEMPLATE/` with a bug, feature, and task form, **only**
  when the project has none. These are tracked files and the one thing here that
  reaches a commit, so tell the user they are there and let them decide.
- Installs `@colbymchenry/codegraph` if the `codegraph` command is missing,
  wires it into the active agent, and indexes the project.

CodeGraph wiring is global: it edits the user's Codex or Claude Code configuration,
not just this repo. If they would rather not, or npm is unavailable, pass
`--no-codegraph` and the rest still runs.

## 2. Work out the areas

`osct-audit` files each draft under an area, and `osct-open-issue` labels the
issue with the same word. Areas are the folders under `.osct/issue-ideas/`, and
the script cannot guess them.

Read the repository: the top-level packages or modules, the labels already on
the GitHub repo (`gh label list`), and the directories the tests are grouped by.
Pick the smallest set that covers where a fix would land, usually between four
and a dozen. Create a folder per area under `.osct/issue-ideas/`, and tell the
user which ones you chose so they can correct you.

An area names where the fix goes, not where the problem surfaces. Keep the
adapter or backend layer as one area, and expect most bugs that appear through
it to belong somewhere else.

## 3. Generate the documentation files

`.osct/docs/` is left empty by the script because it needs the same reading.
Follow the bootstrap in the `osct-docs` skill to write `project.md` and
`config.toml` from what the repo actually contains, then show the user both.

If `osct-docs` is not installed, say so and skip this step rather than guessing
at the conventions.

## 4. Report

Say what was created, which areas you chose, whether the issue templates are new
tracked files, and whether CodeGraph was installed or was already there. Keep it
to a few lines; the user can read `.osct/README.md` for the rest.
