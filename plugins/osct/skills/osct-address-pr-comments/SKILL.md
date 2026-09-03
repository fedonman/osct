---
name: osct-address-pr-comments
description: Verify review comments on an existing GitHub pull request against the linked issues, PR context, current code and checks; implement comments that hold, and draft terse replies for approval before posting. Use when asked to handle, address or respond to reviewer feedback on a PR.
---

# Addressing PR review comments

A review comment is a claim to check, not an instruction to accept blindly. Fix the comments that hold and answer the ones that do not. Nothing is posted to GitHub until the user approves the exact replies.

## 1. Read the whole request

Collect every actionable, unresolved comment and its full thread, including the comment ID, author, path, line and diff hunk. Include a top-level review or PR conversation comment when it asks for a change. Ignore bot notices and status messages unless the user includes them.

Read the context that can settle each comment:

- The PR title, body, full diff, commits, checks and current head branch.
- Every issue the PR closes or cites, including its discussion. The issue normally carries the problem and intended design.
- The current implementation, tests and documentation around the changed symbols. Where the repo is indexed by CodeGraph, use `codegraph_explore` before grep or file-by-file reading so callers outside the diff are included.
- Repository history, blame, release notes or external documentation only when the comment depends on compatibility or past intent.

Use `gh pr view`, `gh pr diff`, `gh pr checks`, the REST API, and GraphQL `reviewThreads` as needed. Paginate API results instead of treating the first page as the whole review. Keep the remote comment and thread IDs because the displayed order is not a stable identifier.

## 2. Verify each comment

Reduce the comment to the factual or design claim it makes and check that claim independently. Run the smallest repro or focused test that can decide it, then run the relevant suite, linter or type checker for any fix.

Classify it as:

- **Correct:** the PR violates the intended behaviour, documented contract, linked issue, or established repository convention.
- **Incorrect:** the premise is contradicted by the current code or agreed scope.
- **Debatable:** more than one choice is sound, or the request changes a trade-off or scope that the available evidence does not settle.

If sources disagree, call it debatable instead of choosing the convenient one. If a newer commit already addressed a correct comment, verify the result and do not make the same change again.

## 3. Implement what is correct

For every correct comment, make the smallest fix at the root cause. Add or adjust a test when behaviour changes, and keep documentation in step when the public contract changes. Do not add source comments that narrate the review, and do not fold unrelated cleanup into the patch.

Preserve unrelated work in a dirty tree. A reply saying "done" may only be posted after its fix is on the PR head branch and the relevant checks pass. Never force-push review fixes.

Do not change the code for an incorrect or debatable comment unless the user chooses that trade-off after seeing the draft response.

## 4. Draft every reply

Keep the drafts out of git without touching `.gitignore`:

```bash
grep -qxF '.osct/' .git/info/exclude || echo '.osct/' >> .git/info/exclude
```

Write `.osct/review-replies/<pr-number>-<slug>.md`. Give every proposed reply a number, its remote comment ID, the location or thread, the verdict, the evidence used, any change made, the checks run, and the exact reply text. The evidence stays in the draft; it does not get pasted into GitHub unless it is needed to answer the reviewer.

For a correct comment, prefer exactly:

> Thanks, done.

For an incorrect comment, state the one fact that settles it. For a debatable comment, state the chosen trade-off and leave room for the reviewer:

> I kept this in `parse()` because both callers need the same check.

> I kept the current name to match the public API, but I can change it if you prefer.

Short, plain, human. No em dashes, throat-clearing, defensive language, or restatement of the review. Never mention Claude or AI.

## 5. Show the user, then stop

Display every exact proposed reply in chat, numbered the same way as the draft and headed by its `file:line` or thread. Beside it, say only whether it was fixed, already satisfied, incorrect or debatable, plus the focused check that supports that verdict. End by saying that nothing has been posted and asking the user to approve all replies, name the numbers to post, or edit their wording.

Do not treat silence, a request to reword, or approval of the code changes as approval to post. When wording changes, show the final text again unless the user explicitly says to post that wording.

## 6. Post only what was approved

Post only the numbered replies the user approved, with their exact approved text. Reply to an inline review comment through its comment ID:

```bash
gh api -X POST repos/<owner>/<repo>/pulls/<pr-number>/comments/<comment-id>/replies -f body='<approved reply>'
```

Use a normal PR conversation comment only for feedback that has no inline thread. Read the posted comments back and report their links. Do not resolve review threads, dismiss reviews, merge the PR, or post any unapproved draft unless the user separately asks.
