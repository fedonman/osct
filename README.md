# Open Source Contribution Toolkit

Six skills for Codex and Claude Code that handle the work around a change rather
than the change itself: finding what is worth fixing, filing it, opening the
pull request, reviewing one, addressing review comments, and keeping the
documentation true. The all-in-one plugin also includes `osct-init`.

Each skill writes its working files under `.osct/` in the repo it is used in,
and adds `.osct/` to `.git/info/exclude` rather than to the shared
`.gitignore`, so drafts never reach a commit.

## Installing

### Codex

```bash
codex plugin marketplace add fedonman/osct
codex plugin add osct@osct
```

### Claude Code

```
/plugin marketplace add fedonman/osct
/plugin install osct@osct
```

`osct` bundles all six skills. Claude Code also exposes them as standalone
plugins, so you can install only what you need:

```
/plugin install osct-docs@osct
/plugin install osct-pr-review@osct
/plugin install osct-address-pr-comments@osct
```

## Setting up a repository

Once per project, ask Codex to use `$osct-init`, or run this in Claude Code:

```
/osct-init
```

It creates the `.osct/` tree, adds `.osct/` and `.codegraph/` to
`.git/info/exclude` rather than to the shared `.gitignore`, writes
`.github/ISSUE_TEMPLATE/` if the project has none, and installs and indexes
[CodeGraph](https://github.com/colbymchenry/codegraph). Then it reads the repo
to work out the areas issues are filed under and to write the documentation
conventions into `.osct/docs/`.

Re-running it changes nothing that already exists. `--no-codegraph` skips the
part that edits your agent configuration.

## The skills

| Skill | What it does |
|---|---|
| `osct-init` | Sets a repository up: the `.osct/` tree, the git exclusions, the issue templates, and CodeGraph. Ships with `osct`. |
| `osct-audit` | Sweeps the repo for bugs, features and tasks and writes issue drafts to `.osct/issue-ideas/`, one file each, every bug carrying a repro that was actually run. |
| `osct-open-issue` | Turns a draft into a filed GitHub issue: the right template, a body under a minute of reading, the type and module label, and the draft moved to the filed folder. |
| `osct-open-pr` | Branches off main, writes a one-paragraph body, links the issue, and opens the pull request. |
| `osct-pr-review` | Reviews a pull request into numbered, pasteable `file:line` comments with `suggestion` blocks, drafted to `.osct/reviews/` for approval before anything is posted. |
| `osct-address-pr-comments` | Checks reviewer comments against the issue, PR, code and tests, implements the ones that hold, and drafts terse replies for approval before posting. |
| `osct-docs` | Carries a house writing style and a documentation checker. Per-project conventions, terminology and checker settings live in `.osct/docs/`, generated on first use. |

## Maintaining the Codex bundle

The standalone plugin folders are the source for the six workflow skills. After
changing one, refresh and check the all-in-one bundle:

```bash
python3 scripts/sync_codex_bundle.py
python3 scripts/sync_codex_bundle.py --check
```

## The documentation checker

`osct-docs` ships `scripts/check_docs.py`, which checks that code examples still
parse and still name symbols that exist, that internal links and the site nav
resolve, and that prose follows the style rules. It is configured per project in
`.osct/docs/config.toml`: the importable module, the import aliases the pages
use, the classes whose instances appear in examples, the site config holding the
nav, and the header of the project's own DSL where it has one. With no config it
falls back to style, links and syntax.

## License

Apache-2.0.
