---
name: osct-audit
description: Audit all or selected areas of a repo across correctness, API, performance, maintainability, documentation, test coverage, CI and packaging, then write verified issue drafts under .osct/issue-ideas/. Defaults to every area and focus. Use when asked to audit, scan or sweep a project, named modules, docs, tests or another focus for work worth filing.
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

Scope has two independent axes:

- **Areas** are modules, packages, subsystems or paths such as `compilers` and `qprogram`.
- **Focuses** are correctness, API and features, performance, maintainability, documentation, test coverage, and CI and packaging.

The default is every area across every focus. A user can narrow either axis or both, and can name more than one value on either axis. Apply a named focus to every selected area.

Examples:

- "Audit `compilers` and `qprogram`" means those two areas across every focus.
- "Audit documentation" means the documentation focus across every area.
- "Audit `qprogram` for test coverage and performance" means those two focuses in that area only.

Do not silently widen a narrowed axis. For a full audit, work through the area-focus combinations one at a time so a strong pass in one module or theme does not stand in for the rest.

Areas are the folders under `.osct/issue-ideas/`; on the first pass in a repo, create them from the project's own top-level modules and say which ones you chose.

**Assign an area by where the fix goes, not by where the problem surfaces.** The adapter or backend layer is the trap: almost any behavioural bug shows up through it, and almost none of them get fixed there.

An area filter controls what is inspected, while the draft area still records where the fix belongs. A documentation gap found while auditing `compilers` may therefore be filed under `docs`.

Keep the drafts out of git without touching `.gitignore`, which is shared:

```bash
grep -qxF '.osct/' .git/info/exclude || echo '.osct/' >> .git/info/exclude
```

## 2. What each focus covers

When every focus is active, use this order. User-visible correctness on default paths remains the highest-value work.

1. **Correctness:** wrong results with no error, crashes on ordinary input, broken state and unsafe boundary behaviour. Silent failures on default paths come first.
2. **API and features:** a public API that cannot do the obvious thing, refuses input already supported internally, or is inconsistent with the rest of the project.
3. **Performance:** normal workloads made impractical by time, memory, I/O or needless repeated work. Measure against a relevant baseline.
4. **Maintainability:** duplicate core logic, dead code, needless dependencies and abstractions, or complexity with a concrete cost. Do not turn personal style preferences into tasks.
5. **Documentation:** false, missing or unusable public docs, tutorials, examples and docstrings. Compare every claim with the current API, run examples where practical, and use the docs checker or site build when the project has one. Do not file requests for more prose without a specific user-facing gap.
6. **Test coverage:** meaningful public behaviour, error paths or regression boundaries that the suite cannot detect. Use the project's coverage tooling when present, but never file a percentage by itself; name the behaviour that can regress and the test that should protect it.
7. **CI and packaging:** gaps that can ship a broken build, artifact or supported environment. Exercise the build and install path rather than inferring from configuration alone.

Read the module's public surface first, then the paths its own docs and tutorials take. Bugs live where the tests are thin and the defaults are implicit.

One problem may cross several focuses. Write one draft under its primary focus and mention the other effects there instead of duplicating it.

## 3. Check before you write

- **Bug: run the repro.** Write the script, run it, paste the real output. If it does not reproduce, it is not a bug.
- **Feature: grep first.** Half of "this is missing" turns out to exist under another name.
- **Documentation: prove the mismatch.** Quote the current claim and the code or runnable result that contradicts it. For a missing page or docstring, name the public task that cannot be completed from the existing docs.
- **Test coverage: name the unprotected behaviour.** Show why the existing suite would miss the regression and state the focused test to add. A low line count alone is not a finding.
- **Nothing already open.** `gh issue list --state all --search "<keywords>"` before writing the draft.
- **Measure any claim about speed or size.** A number you did not measure is a guess.

If the check kills the idea, it does not just get dropped. Append it to `.osct/issue-ideas/rejected.md` with the claim and a `Verdict:` paragraph saying what you measured and why it does not hold. That file exists so nobody spends the time twice.

## 4. One file per idea

`.osct/issue-ideas/<area>/<id>-<slug>.md`. `id` is the next free three-digit number across all areas. `slug` is the title lowercased and hyphenated, cut to 62 characters, mid-word is fine.

Title is the issue title, with the template prefix already on it: `[Bug]: `, `[Feature]: `, `[Task]: `. Then the header line:

```markdown
# [Bug]: Schedule.eig returns spectra of the wrong size when a coefficient is zero

Area: `analog` | Focus: `correctness` | Effort: S | Value: high | Checked: reproduced
```

Focus is the primary focus that found the issue. Effort is S, M or L. Value is high, medium or low. Checked is `reproduced` when a script was run, `gap confirmed` when it was verified by reading the code.

Sections, bugs:

`## What happens` (2 to 4 sentences, what breaks and the cause) · `## Why it matters` (which real path hits it) · `## Where it comes from` (the code, with `file.py:line` refs, and what you verified) · `## Repro` (the script, then its real output in a second block) · `## Suggested fix` (what to change, plus the regression test to add) · `## Code refs` (bullet list of `file:line`) · `## How this was checked`

Sections, features and tasks:

`## Summary` · `## Motivation` · `## How it works today` · `## Proposal` · `## Code refs` · `## How this was checked`

These drafts are research notes and they are allowed to be long. The cutting happens at filing time, not here.

## 5. Keep the README in step

`.osct/issue-ideas/README.md` is the index. After a pass, update:

- The header count line: how many ideas, split into bugs, features and tasks.
- **Pick these up first**: confirmed bugs that give wrong results with no error, on default paths. That table only.
- The per-area table, one row per idea, linking the file and naming its primary focus. Add a `Focus` column when an older index does not have one.
- The filed count, `N of these are filed`, which the filing skill maintains after that.

A title appears in both the pick-first list and its area table. Both rows move when a draft is filed.

## 6. Report

Answer with the counts per area and focus, then the pick-first ones by title, nothing else. The drafts carry the detail.

Do not file anything from this skill. The user picks what gets filed.
