---
name: osct-pr-review
description: Review a pull request against its issue, repository standards, documentation and regressions; produce numbered, pasteable file:line comments or a clean approval, drafted to .osct/reviews/ before anything is posted. Use when asked to review a PR, "review #123", "look at this PR", or given a GitHub pull request URL.
---

# PR review

Findings go into a draft file first. Nothing reaches GitHub until the user approves it.

## Tools

- Where the repo is indexed by CodeGraph, `codegraph_explore` the changed symbols before you read the diff. It shows the callers the diff does not, which is where "the same defect is in three files" comes from. Without it, grep the callers of every symbol the diff touches.
- Every ```suggestion block is the shortest thing that works, in the idiom of the code around it.

## 1. Does it solve the issue?

This is the primary review question. A PR can be tidy and well tested but still be wrong because it does not fix or implement the issue.

A PR usually addresses an issue the team filed, and the issue holds the problem, scope and intended design. Find it in the PR body, the branch name, or the issue list, and read its full discussion before the diff. Reproduce the issue on the base branch when practical, then verify that the PR head changes that result. Check every acceptance criterion and important case the issue names.

Judge the result, not mechanical obedience to a proposed implementation. A different approach is fine when it solves the same problem cleanly. Missing the issue, fixing only its example rather than its cause, or silently changing its scope is a finding even when the code itself looks sound. If there is no linked issue, use the PR's stated goal and do not invent a broader one.

## 2. Is the implementation a good fit?

Once the issue is satisfied, check the change against the repository rather than personal preference:

- It follows the code around it: naming, structure, error handling, public API conventions, types, formatting and test style.
- It uses the language standard library and existing project helpers where they already solve the problem. Flag a new dependency, duplicate helper, one-use abstraction or dead flexibility only when the simpler existing option really fits.
- New or changed public symbols have the docstrings the repository expects. Docstrings describe the contract and important constraints, not a line-by-line retelling of the implementation.
- User-facing behaviour is reflected in the relevant guides, API reference, examples and changelog when the project normally maintains them. Documentation must describe what the code actually does.
- Tests cover the issue and the meaningful boundaries of the fix without pinning incidental implementation details.

Treat a style difference as a finding only when the repository has a clear convention or it materially hurts correctness or maintenance. Do not turn taste into a review comment.

## 3. Did the PR introduce a bug?

Trace the changed symbols into their callers and exercise the paths the diff can affect. Look for wrong results, newly reachable errors, broken compatibility, unsafe boundary behaviour and state that now leaks across calls.

Report regressions introduced by the PR. When causality is unclear, run the same repro against the base and head revisions: if it passes on base and fails on head, it belongs in the review. If it fails on both, it is pre-existing and does not need a PR comment. The exception is when that behaviour is the issue this PR claims to fix, because then it proves the PR has not completed its main job.

## 4. A review has no comment quota

Do not hunt for comments to make the review look thorough. Skip speculative edge cases, harmless nits and observations that do not ask for a useful change. If the PR solves the issue, fits the repository, is documented as needed and introduces no regression, approve it with no inline comments. That is a complete review.

## 5. Verify, don't guess

Check the diff out in a worktree, install, and run the suite, the linter, and the type checker. Then exercise the changed logic directly: sweep the boundaries, write the repro, run the fix you are about to suggest. A suggestion you have actually run is worth five you have reasoned about.

Read the CI checks too. A red gate usually names the finding for you.

## 6. Draft to `.osct/reviews/<pr-number>-<slug>.md`

Keep it out of git without touching `.gitignore`, which is shared. Run this before writing anything under `.osct/`:

```bash
grep -qxF '.osct/' .git/info/exclude || echo '.osct/' >> .git/info/exclude
```

Structure:

```markdown
# PR #79 review: <PR title>

General review (post as the review body):

> Thanks <author>. Left some comments.

If there are no comments:

> Thanks <author>. Looks good.

---

## 1. `path/to/file.py:146-149`

<one or two sentences on what is wrong>

```suggestion
<the fixed lines>
```

## 2. `path/to/other.py:98`

...

---

## Notes

<everything that is context rather than a comment>
```

With no findings, omit the numbered comment sections and say in `## Notes` what established that the issue is fixed. Number comments when there are any. Use the same numbers in the chat answer so "post 1, 3 and 5" is unambiguous.

## 7. Comment rules

- Anchor to the line the finding is about. `file:line`, or `file:start-end` for a range.
- A couple of sentences, casual. No preamble, no restating the diff back.
- Include a ```suggestion block whenever the fix fits in a few lines. The block must contain the exact replacement for the anchored lines, nothing else.
- **A bug finding carries a minimal repro, or better, the test the PR should add.** "The two backends are inverted" is not a finding until the reviewer can paste something and see it. Put the snippet in the comment itself.
- Fix the root cause. If the same defect appears in three files, say so in one comment and name the other two, rather than filing three.
- Measurements, timings and verification detail go in `## Notes`, not in the comment. The repro is the exception.

Every comment must identify a change worth making. Do not include praise, neutral observations, pre-existing bugs or comments whose only purpose is to show that a file was reviewed.

## 8. The review body is short and thankful

"Thanks Flavie. Left some comments." or "Thanks Flavie. Looks good." is the whole body. Merge-order warnings, what you verified, what you decided was out of scope, all of it goes in `## Notes` in the file, not on GitHub.

## 9. Writing style

Short, plain, human. Simple everyday words. No em dashes. No "delve", "leverage", "robust", "comprehensive". No bullet-padded summaries. It should read like a person wrote it quickly.

**Never hard-wrap the draft file.** One paragraph is one line, however wide. Code blocks keep their own breaks.

Never mention Claude or AI anywhere in a comment, review body, commit, or PR text.

## 10. Answer in chat as the comments themselves

When there are findings, the chat answer is the list of comments, numbered, each headed by `file:line`, ready to paste. Not a prose review, not a summary table, not a findings essay.

When there are no findings, show the exact approval body and say there are no inline comments. In both cases, wait for the user's approval before posting.

## 11. Posting, once approved

Inline comments must land on real diff lines, which `gh pr review` cannot do. Use the API:

```bash
cat > /tmp/review.json <<'EOF'
{
  "event": "COMMENT",
  "body": "Thanks Flavie. Left some comments.",
  "comments": [
    {"path": "src/pkg/mod.py", "line": 149, "side": "RIGHT", "body": "..."},
    {"path": "src/pkg/other.py", "start_line": 171, "line": 247, "side": "RIGHT", "body": "..."}
  ]
}
EOF
gh api -X POST repos/<owner>/<repo>/pulls/<n>/reviews --input /tmp/review.json
```

Post only the numbers the user named. A comment on a line outside the diff is rejected, so anchor to lines the PR actually touches.

For a clean review, post an approval only after the user approves the draft:

```bash
gh pr review <n> --approve --body "Thanks Flavie. Looks good."
```
