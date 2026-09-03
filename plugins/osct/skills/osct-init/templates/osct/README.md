# .osct

Working files for the Open Source Contribution Toolkit skills. None of it is
tracked: `osct-init` adds `.osct/` to `.git/info/exclude` rather than to the
shared `.gitignore`, so nothing here can reach a commit by accident.

| Path | What lives there | Yours to edit |
|---|---|---|
| `docs/project.md` | Documentation surfaces, the change checklist, the project's terminology. | Yes, and you should. |
| `docs/config.toml` | What the documentation checker needs to know about this project. | Yes. |
| `issue-ideas/` | Audit drafts, one file per idea, in a folder per area. `README.md` is the index. | The index is maintained by the skills. |
| `filed/` | Drafts that became GitHub issues, moved here with the issue link. | No. |
| `prs/` | Pull request bodies, one per branch. | No. |
| `reviews/` | Drafted review comments, waiting for your approval before anything is posted. | Read them before they go out. |
| `review-replies/` | Verified reviewer comments and exact reply drafts, waiting for your approval before anything is posted. | Read them before they go out. |

The two files under `docs/` are written once from what the repo contains and
then corrected by hand. Everything else is generated per task and safe to
delete.
