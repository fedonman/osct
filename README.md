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
/plugin install osct-pr-review@osct
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

<table>
  <thead>
    <tr>
      <th width="240" nowrap="nowrap">Skill</th>
      <th>What it does</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td width="240" nowrap="nowrap"><code>osct-init</code></td>
      <td>Sets a repository up: the <code>.osct/</code> tree, the git exclusions, the issue templates, and CodeGraph. Ships with <code>osct</code>.</td>
    </tr>
    <tr>
      <td width="240" nowrap="nowrap"><code>osct-audit</code></td>
      <td>Audits all or selected project areas across correctness, API, performance, maintainability, documentation, test coverage, CI and packaging, then writes verified issue drafts to <code>.osct/issue-ideas/</code>.</td>
    </tr>
    <tr>
      <td width="240" nowrap="nowrap"><code>osct-open-issue</code></td>
      <td>Turns a draft into a filed GitHub issue: the right template, a body under a minute of reading, the type and module label, and the draft moved to the filed folder.</td>
    </tr>
    <tr>
      <td width="240" nowrap="nowrap"><code>osct-open-pr</code></td>
      <td>Branches off main, writes a one-paragraph body, links the issue, and opens the pull request.</td>
    </tr>
    <tr>
      <td width="240" nowrap="nowrap"><code>osct-pr-review</code></td>
      <td>Reviews a pull request into numbered, pasteable <code>file:line</code> comments with <code>suggestion</code> blocks, drafted to <code>.osct/reviews/</code> for approval before anything is posted.</td>
    </tr>
    <tr>
      <td width="240" nowrap="nowrap"><code>osct-address-pr-comments</code></td>
      <td>Checks reviewer comments against the issue, PR, code and tests, implements the ones that hold, and drafts terse replies for approval before posting.</td>
    </tr>
    <tr>
      <td width="240" nowrap="nowrap"><code>osct-docs</code></td>
      <td>Carries a house writing style and a documentation checker. Per-project conventions, terminology and checker settings live in <code>.osct/docs/</code>, generated on first use.</td>
    </tr>
  </tbody>
</table>

## Maintaining the Codex bundle

The standalone plugin folders are the source for the six workflow skills. After
changing one, refresh and check the all-in-one bundle:

```bash
python3 scripts/sync_codex_bundle.py
python3 scripts/sync_codex_bundle.py --check
```

## Releasing

Run the **Release** workflow from the GitHub Actions tab and enter a stable
semantic version without the `v` prefix, such as `0.2.0`. The workflow updates
every plugin manifest, synchronizes and validates the Codex bundle, commits the
version, tags that commit, and creates the GitHub Release with generated notes.

The current manifest version can also be checked locally:

```bash
python3 scripts/set_plugin_version.py --current
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
