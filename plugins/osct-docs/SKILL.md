---
name: osct-docs
description: Write or edit documentation in this repo. Use when touching docs/, the README, or a public docstring, and whenever a change to the code needs its documentation brought along. Carries the house writing style, the per-project conventions kept in .osct/docs/, the change checklist, and the docs checker.
---

# Writing documentation

Documentation here is held to the same standard as the code. It has to be
correct first and readable second. A page that reads well and describes
behaviour the library does not have is worse than no page at all.

Two things are project-specific and live in the repo, under `.osct/docs/`:
`project.md` holds the surfaces, the change checklist, and the terminology;
`config.toml` holds the names the checker needs. Everything else is in this
skill and is the same in every repo.

## Before anything else

Read `.osct/docs/project.md`. If it is not there, generate it and
`.osct/docs/config.toml` from what the repo actually contains, following
[bootstrap.md](references/bootstrap.md), and show the user what you wrote before
going on. Both files are committed; the rest of `.osct/` is drafts and is not.

## Check the claim before you write it

The code is the authority on what the project does, and the tests pin the parts
that are settled. Read the implementation before writing about its details, and
verify names and signatures against the source rather than from memory. The
checker described below catches attributes that no longer exist, but only inside
Python fences, and only for the module and classes named in `config.toml`.

Where a page and the code disagree and you cannot tell which is wrong, say so
rather than picking one. A confident sentence about the wrong behaviour is the
expensive kind of documentation bug.

## The change checklist

A change to the public surface is not finished when the code is. What moves with
it is listed in `.osct/docs/project.md`, and it is not the same list in every
repo: a normative grammar, a generated API page, or a set of rebuilt figures only
exist where they exist. Work through that list, and when you are asked to do only
part of it, do that part and say plainly which steps are still outstanding.

## House style

The full rules, with the reasoning and the word list, are in
[style.md](references/style.md). Read that file before writing prose. The short
version:

Write the way an experienced engineer writes when explaining something to a
colleague. Professional, direct, specific. Say what a thing does, why it exists,
and when to use it, without claiming it is powerful or elegant. Do not use em
dashes; a comma, a colon, parentheses, or two sentences will do. Do not use the
vocabulary that marks generated text, and do not open or close a section with
filler.

Prefer connected paragraphs. Use a bulleted list when the content is a genuine
enumeration such as parameters, options, or independent items, and a numbered
list only when the order matters. Do not turn every sentence into a bullet.

Keep headings descriptive, in sentence case, and do not stack three levels of
heading over four sentences of text. Do not say the same thing in an
introduction, the body, and a summary.

Avoid comparative claims unless the comparison is on the page. "Faster" needs a
baseline, "simpler" needs the thing it is simpler than.

Use the project's own words for its own concepts. They are written down in the
terminology section of `.osct/docs/project.md`; a synonym you invented breaks the
link between an error message and the page that explains it.

Before handing anything back, reread it and cut what sounds generic, promotional,
or over-polished. That pass is part of the work, not an optional extra.

## Running the checker

`scripts/check_docs.py` checks three things: that Python and DSL examples still
parse and still name symbols that exist, that internal links and the site nav
resolve, and that prose follows the style rules. It reads `.osct/docs/config.toml`
by walking up from the working directory, and it needs the project's own
environment for the code group:

```bash
uv run python "${CLAUDE_PLUGIN_ROOT}/scripts/check_docs.py" docs
```

Narrow it to the files you touched, which is the normal case:

```bash
uv run python "${CLAUDE_PLUGIN_ROOT}/scripts/check_docs.py" docs/guide/waveforms.md
```

Broken examples, broken links, and broken nav entries are reported as errors and
set the exit status. Style findings are warnings; `--strict` promotes them to
errors, which is what a gate would use. The one check `--strict` leaves alone is
`dsl-vendor`, which fires when an example needs a vendor extension that is not
installed here. That describes the environment, not the page. `--only style`,
`--only code`, and `--only links` run one group, and `--json` gives
machine-readable output.

A snippet that is deliberately not valid Python, such as a before-and-after
column layout, is exempted with an HTML comment on the line above the fence:

```markdown
<!-- check: skip -->
```

Snippets that use `...` for an elision or `<placeholder>` for a name are detected
as illustrative and skipped without a marker.

The checker is not a substitute for building the site. A build fails on an
unresolved API cross-reference, which the checker cannot see. Build locally,
with the command in `.osct/docs/project.md`, before opening a PR that touches
docstrings or the reference pages.
