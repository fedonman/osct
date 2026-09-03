---
name: osct-pr-review
description: Review a pull request and produce numbered, pasteable file:line comments with ```suggestion blocks, drafted to .osct/reviews/ for approval before anything is posted. Use when asked to review a PR, "review #123", "look at this PR", or given a GitHub pull request URL.
---

# PR review

Findings go into a draft file first. Nothing reaches GitHub until the user approves it.

## Tools

- Where the repo is indexed by CodeGraph, `codegraph_explore` the changed symbols before you read the diff. It shows the callers the diff does not, which is where "the same defect is in three files" comes from. Without it, grep the callers of every symbol the diff touches.
- Review the over-engineering axis too: reinvented stdlib, a new dependency for what a few lines do, an interface with one implementation, dead flexibility. Fold what you find in as normal numbered comments.
- Every ```suggestion block is the shortest thing that works, in the idiom of the code around it.

## 1. Read the issue before the diff

A PR usually addresses an issue the team filed, and the issue holds the reasoning and the intended design. Find it in the PR body, the branch name, or the issue list, and read it. Then judge the PR against the proposal in it, not only against the code: does it solve the stated problem, does it take the suggested approach, and where it deviates, is the deviation better or a miss.

## 2. Verify, don't guess

Check the diff out in a worktree, install, and run the suite, the linter, and the type checker. Then exercise the changed logic directly: sweep the boundaries, write the repro, run the fix you are about to suggest. A suggestion you have actually run is worth five you have reasoned about.

Read the CI checks too. A red gate usually names the finding for you.

## 3. Draft to `.osct/reviews/<pr-number>-<slug>.md`

Keep it out of git without touching `.gitignore`, which is shared. Run this before writing anything under `.osct/`:

```bash
grep -qxF '.osct/' .git/info/exclude || echo '.osct/' >> .git/info/exclude
```

Structure:

```markdown
# PR #79 review: <PR title>

General comment (post as the review body):

> Thanks <author>. Left some comments.

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

Number the comments. Use the same numbers in the chat answer so "post 1, 3 and 5" is unambiguous.

## 4. Comment rules

- Anchor to the line the finding is about. `file:line`, or `file:start-end` for a range.
- A couple of sentences, casual. No preamble, no restating the diff back.
- Include a ```suggestion block whenever the fix fits in a few lines. The block must contain the exact replacement for the anchored lines, nothing else.
- **A bug finding carries a minimal repro, or better, the test the PR should add.** "The two backends are inverted" is not a finding until the reviewer can paste something and see it. Put the snippet in the comment itself.
- Fix the root cause. If the same defect appears in three files, say so in one comment and name the other two, rather than filing three.
- Measurements, timings and verification detail go in `## Notes`, not in the comment. The repro is the exception.

## 5. The review body is short and thankful

"Thanks Flavie. Left some comments." That is the whole body. Merge-order warnings, what you verified, what you decided was out of scope, all of it goes in `## Notes` in the file, not on GitHub.

## 6. Writing style

Short, plain, human. Simple everyday words. No em dashes. No "delve", "leverage", "robust", "comprehensive". No bullet-padded summaries. It should read like a person wrote it quickly.

**Never hard-wrap the draft file.** One paragraph is one line, however wide. Code blocks keep their own breaks.

Never mention Claude or AI anywhere in a comment, review body, commit, or PR text.

## 7. Answer in chat as the comments themselves

The chat answer is the list of comments, numbered, each headed by `file:line`, ready to paste. Not a prose review, not a summary table, not a findings essay.

## 8. Posting, once approved

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
