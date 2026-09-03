---
name: osct-audit
description: Audit the repo for bugs, features and tasks and write them up as issue drafts under .osct/issue-ideas/, one file each, every bug carrying a repro that was actually run. Takes the whole project or a list of modules. Use when asked to audit, scan or sweep the codebase for problems, or to find work worth filing.
---

# Auditing the repo

The output is a folder of drafts, not filed issues. Filing is a separate step, see `osct-open-issue`.

A draft is only worth writing if someone else can trust it without redoing the work. That means a repro that was run, or a quote from the file that proves the gap.

## Tools

- **A code index first, where there is one.** One `codegraph_explore` call over an area returns the symbols, the call paths between them and their blast radius, which is how you pick what to read. Without an index, start from the module's public surface and follow the callers by grep.
- Blast radius is audit signal. A defect in a symbol with 60 callers is worth more than the same defect in a leaf, and the caller count belongs in `## Why it matters`.
- Send the wide reading sweeps to a read-only subagent so a whole-repo pass does not fill the context with file dumps. What comes back is `path:line` citations, which is what `## Code refs` wants anyway.
- Keep every `## Suggested fix` to the smallest change at the root: one guard in the shared function rather than one per caller, and no new abstraction. If the honest fix is a deletion, say that.

## 1. Scope

Default is the whole project, one area at a time. If the user names modules, do only those. Areas are the folders under `.osct/issue-ideas/`; on the first pass in a repo, create them from the project's own top-level modules and say which ones you chose.

**Assign an area by where the fix goes, not by where the problem surfaces.** The adapter or backend layer is the trap: almost any behavioural bug shows up through it, and almost none of them get fixed there.

Keep the drafts out of git without touching `.gitignore`, which is shared:

```bash
grep -qxF '.osct/' .git/info/exclude || echo '.osct/' >> .git/info/exclude
```

## 2. What to look for

In rough order of worth:

1. Wrong results with no error, on a default code path. Silent is worse than loud.
2. Crashes on ordinary input.
3. A public API that cannot do the obvious thing, or refuses input it already supports internally.
4. Performance that makes a normal size unusable, with the numbers to show it.
5. Missing coverage, CI or packaging gaps that let the above ship.

Read the module's public surface first, then the paths its own docs and tutorials take. Bugs live where the tests are thin and the defaults are implicit.

## 3. Check before you write

- **Bug: run the repro.** Write the script, run it, paste the real output. If it does not reproduce, it is not a bug.
- **Feature: grep first.** Half of "this is missing" turns out to exist under another name.
- **Nothing already open.** `gh issue list --state all --search "<keywords>"` before writing the draft.
- **Measure any claim about speed or size.** A number you did not measure is a guess.

If the check kills the idea, it does not just get dropped. Append it to `.osct/issue-ideas/rejected.md` with the claim and a `Verdict:` paragraph saying what you measured and why it does not hold. That file exists so nobody spends the time twice.

## 4. One file per idea

`.osct/issue-ideas/<area>/<id>-<slug>.md`. `id` is the next free three-digit number across all areas. `slug` is the title lowercased and hyphenated, cut to 62 characters, mid-word is fine.

Title is the issue title, with the template prefix already on it: `[Bug]: `, `[Feature]: `, `[Task]: `. Then the header line:

```markdown
# [Bug]: Schedule.eig returns spectra of the wrong size when a coefficient is zero

Area: `analog` | Effort: S | Value: high | Checked: reproduced
```

Effort is S, M or L. Value is high, medium or low. Checked is `reproduced` when a script was run, `gap confirmed` when it was verified by reading the code.

Sections, bugs:

`## What happens` (2 to 4 sentences, what breaks and the cause) · `## Why it matters` (which real path hits it) · `## Where it comes from` (the code, with `file.py:line` refs, and what you verified) · `## Repro` (the script, then its real output in a second block) · `## Suggested fix` (what to change, plus the regression test to add) · `## Code refs` (bullet list of `file:line`) · `## How this was checked`

Sections, features and tasks:

`## Summary` · `## Motivation` · `## How it works today` · `## Proposal` · `## Code refs` · `## How this was checked`

These drafts are research notes and they are allowed to be long. The cutting happens at filing time, not here.

## 5. Keep the README in step

`.osct/issue-ideas/README.md` is the index. After a pass, update:

- The header count line: how many ideas, split into bugs, features and tasks.
- **Pick these up first**: confirmed bugs that give wrong results with no error, on default paths. That table only.
- The per-area table, one row per idea, linking the file.
- The filed count, `N of these are filed`, which the filing skill maintains after that.

A title appears in both the pick-first list and its area table. Both rows move when a draft is filed.

## 6. Report

Answer with the counts per area and the pick-first ones by title, nothing else. The drafts carry the detail.

Do not file anything from this skill. The user picks what gets filed.
