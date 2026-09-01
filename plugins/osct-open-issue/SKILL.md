---
name: osct-open-issue
description: File a GitHub issue from the CLI - pick the template, keep the body under a minute of reading, set the type and the module label, and move the draft to the filed folder. Use when asked to open, file or create an issue, or to turn a draft or a finding into one.
---

# Filing an issue

A filed issue is short. A maintainer reads it in under a minute or it is too long.

## Tools

- Collect the `file:line` refs you name in the body from the source, and settle "is this really missing" before you file a feature. `codegraph_explore` does both in one call where the repo is indexed.
- Ponytail the Proposed Solution. The wanted API in as few lines as possible, no scaffolding, no config knob nobody asked for.
- Caveman is for the chat, never for the issue. Issue text is plain human English.

## 1. Pick the template

Read `.github/ISSUE_TEMPLATE/` and match the kind of issue to the template there. The usual three:

| Kind | Template | Title prefix | Fields |
|---|---|---|---|
| Bug | `bug_report.yml` | `[Bug]: ` | Description, Minimal Reproducible Example, Expected, Actual, System Information |
| Feature | `feature_request.yml` | `[Feature]: ` | Summary, Motivation. Proposed Solution optional |
| Chore, refactor, perf | `task.yml` | `[Task]: ` | What needs doing, Why |

Fill the required fields. Leave optional ones empty unless they carry something the required ones do not.

Title is a short verb phrase after the prefix. No sentence, no `file.py:` prefix.

`gh issue create` bypasses templates entirely, so reproduce the template's headings yourself in the body file.

## 2. Keep it short

This is the hard rule, and completeness is the failure mode, not accuracy.

- Bug Description: 2 to 4 sentences. What breaks, and the cause. Nothing else.
- Feature Summary: 1 to 2 sentences. Motivation: 2 to 4.
- Code example: the smallest thing that shows the point, 5 to 10 lines. Strip imports, prints and setup that are not load bearing.
- Actual Behavior: only the lines that matter. Trim a traceback to the final frame and the error.
- System Information: 3 or 4 lines, not a full environment dump.
- Proposed Solution: a short snippet of the wanted API plus a sentence or two.

Never include: scope tables, affected-symbol lists, `file:line` reference lists, "files to touch" lists, numbered multi-step fix plans, measurement sweeps, or a paragraph on why the bug matters.

Never put a `file:line` reference in parentheses. No human writes "X does Y (`analog/schedule.py:341`), so Z". If the reader cannot follow without the location, name the file or the function in the sentence: "`Schedule.eig` calls `to_qtensor()` with no `total_nqubits`". Otherwise leave it out, the maintainer can find it.

Never add a supporting-evidence bullet list, however factual. Install sizes, version pins, affected-platform counts, all verified and all unwanted. Pick the one fact that makes the case, put it in the prose, drop the rest.

## 3. Writing style

Short, plain, human. Simple everyday words. No em dashes. No "delve", "leverage", "robust", "comprehensive". No bullet-padded summaries, no restating the obvious. It should read like a person wrote it quickly.

Never mention Claude or AI anywhere in the issue.

## 4. Labels

Every issue gets at least one module label. Get the set with `gh label list`, and pass it on create so it never needs backfilling.

**Label where the fix goes, not everywhere the bug surfaces.** The backend or driver layer is the trap: almost any behavioural bug shows up through it, but that is rarely where the fix lands.

Two labels are fine when the fix genuinely spans both, e.g. a seed frozen in Python and the RNG stream in C++.

If the repo has issue types, there is no kind label. `bug` and `enhancement` are redundant with the type.

## 5. Create, then set the type

```bash
gh issue create --repo <owner>/<repo> --title "[Bug]: <short verb phrase>" --body-file body.md --label <module>
```

`gh` has no `--type` flag on `issue create` or `issue edit`, and the `type:` key in the template does not apply to CLI-filed issues. PATCH it afterwards:

```bash
gh api -X PATCH /repos/<owner>/<repo>/issues/<n> -f type=Feature
```

Type names must match the org's exactly, usually `Bug`, `Feature`, `Task`. Same call shape works for the body if `gh issue edit` fails.

## 6. Move the draft

Keep it out of git without touching `.gitignore`, which is shared. Run this before writing anything under `.osct/`:

```bash
grep -qxF '.osct/' .git/info/exclude || echo '.osct/' >> .git/info/exclude
```

Drafts live in `.osct/issue-ideas/<area>/<id>-<slug>.md` and are deliberately verbose research notes. Cut hard when filing, never paste one straight in.

Once filed, in the same turn:

1. Insert `Filed: <issue url>` as the second line of the draft, under the `#` title.
2. Move it to `.osct/filed/<area>/<same-filename>.md`, keeping the area subfolder.
3. In `.osct/issue-ideas/README.md`, repoint the row's link to `../filed/<area>/<file>` and append ` #<number>`. The title appears in two tables, the "pick these up first" list and the per-area table. Both rows need it.
4. Update the "N of these are filed" count in the README header.

Never leave a filed draft sitting in its area folder.
