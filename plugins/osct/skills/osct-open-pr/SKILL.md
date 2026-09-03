---
name: osct-open-pr
description: Open a pull request from the CLI - branch off main, write a one-paragraph body, link the issue, and edit the body with the REST endpoint when gh pr edit fails. Use when asked to open, create or raise a PR, or to push a branch up for review.
---

# Opening a PR

The diff and CI carry the detail. The body is one short paragraph.

## Tools

- Work out the blast radius of the symbols you touched before pushing: it names the callers and the tests to run, including the ones the diff never mentions. `codegraph_explore` gives it in one call where the repo is indexed.
- Cut the diff back before you open. Anything there to serve a case nobody asked for comes out now, not in review.
- Commit subjects follow the repo's own style, check `git log --oneline`. Use Conventional Commits only if that log already does.

## 1. Branch first

`main` is usually covered by a ruleset: `non_fast_forward`, `deletion`, `pull_request`, `required_status_checks`. That means no direct push, no force-push, and no rewriting history that is already on the remote.

Branch before committing. If a commit has already landed on `main` and you are asked to clean it up, say up front that the ruleset forbids a rewrite rather than proposing a force-push.

The classic branch-protection endpoint returns 404 "Branch not protected" even when `/branches/main` reports `protected: true`. Check `/repos/<owner>/<repo>/rulesets`, not `/branches/main/protection`.

## 2. Commit messages

Short verb phrase, plain words. No em dashes. Never add `Co-Authored-By: Claude`, a "Generated with Claude Code" footer, or any other mention of AI, in the commit, the body, or anywhere else.

## 3. The body is one paragraph

Say what changed. That is all.

No `## What was wrong` / `## What changed` / `## Verification` headings. No pasted test output, no before/after command transcripts, no note about local environment quirks. Aim for a third of what feels complete: a body that starts at 370 words should ship at 60.

Link the issue on its own line, `Closes #123`, and let the issue carry the reasoning.

Short, plain, human. Simple everyday words. No "delve", "leverage", "robust", "comprehensive". It should read like a person wrote it quickly.

## 4. Where the history goes

A rename, a change of approach, "this used to be called X" - that belongs in the commit message, in the reply to the reviewer, and in the changelog fragment when it is a user-visible breaking change. Never in a docstring, a code comment, or a test name. When a reviewer says "edit the comment to explain", they mean the reply on the PR, not a comment in the source.

Before pushing, grep the diff for narration like "renamed", "used to be", "formerly", "was called", "on review".

## 5. Create

Write the body to `.osct/prs/<branch>.md`, not to the repo root. Keep it out of git without touching `.gitignore`, which is shared. Run this before writing anything under `.osct/`:

```bash
grep -qxF '.osct/' .git/info/exclude || echo '.osct/' >> .git/info/exclude
```

```bash
gh pr create --repo <owner>/<repo> --base main --title "<short verb phrase>" --body-file .osct/prs/<branch>.md
```

## 6. Editing the body

`gh pr edit <n> --body-file <file>` fails on a repo with a Projects (classic) board attached:

```
GraphQL: Projects (classic) is being deprecated ... (repository.pullRequest.projectCards)
```

It reports the error and silently does not write the body. Use REST instead:

```bash
gh api -X PATCH /repos/<owner>/<repo>/pulls/<n> -F body=@.osct/prs/<branch>.md
```

Read it back with `gh pr view <n> --json body` either way. The failed GraphQL path looks like a warning rather than a failure.
