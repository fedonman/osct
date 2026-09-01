# Generating the project files

`.osct/docs/` holds what this skill cannot know from outside the repo: where the
documentation lives, what moves with a code change, the project's vocabulary, and
the handful of names the checker needs. Write both files once, from what the repo
actually contains, and correct them when the repo changes rather than rewriting
them from scratch.

Do not guess. Every line in `project.md` should come from something you read: the
site config, the CI workflow, `pyproject.toml`, the existing pages. A convention
you invented is worse than an absent one, because the next writer will follow it.

Commit both files. They are project documentation, not scratch, even though the
rest of `.osct/` is drafts.

## project.md

Fill this skeleton. Drop a section the repo has no answer for rather than padding
it. House style applies to this file too.

```markdown
# <Project> documentation

## Documentation surfaces

<One paragraph naming the prose surfaces and warning that they do not share
conventions.>

### The documentation site

<Which directory. Which builder, from the config file you found. The commands to
serve and to build, copied from the CI workflow so they cannot drift. What the
tree is: which sections exist and what each is for. How a page becomes reachable,
which is the nav config for most builders and is worth stating outright, since
adding a file is not enough. Which pages are generated rather than written.>

### The README

<What it is besides the front page: the PyPI long description, the crate
description, whatever the packaging metadata points at. What that implies for
links. What belongs on it and what belongs in the site instead.>

### Docstrings

<The convention and what enforces it. Whether they are rendered into the site,
and by what. The cross-reference syntax that resolves, and the one that silently
does not.>

## The change checklist

<A numbered list of what moves together when the DSL or the public API changes:
code, tests, any normative grammar or schema, the guide page, the reference page,
the docstrings behind a generated page, and any generated asset such as a figure,
with the command that rebuilds it. Order does not matter much; completeness does.>

If you are asked to do only part of this, do that part and say plainly which
steps are still outstanding.

## Terminology

<The load-bearing words, defined in connected prose rather than a glossary table.
Include the renames: the older spellings that were replaced and must not come
back. This is the section the writer reads most often, so keep it tight.>

## Local conventions

<Anything true here that a writer would otherwise get wrong: features the site
config enables but no page uses, a spelling the tree is consistent on, a fence
language the pages leave bare.>
```

## config.toml

Only `module` and `site_config` are usually needed. Everything else has a default
that degrades to a weaker but correct check.

```toml
# The importable package that examples are checked against. Omit it and the code
# group falls back to syntax checking only.
module = "qprogram"

# Import aliases the pages use for that module, beyond the module name itself.
aliases = ["qp"]

# Classes whose instances appear in examples. An assignment from a call to one of
# these binds the target name, so `program.play(...)` three fences later is checked
# against that class.
instances = ["QProgram", "Fragment"]

# Capitalised words allowed mid-heading, on top of the built-in list. Product
# names, vendors, acronyms the project uses.
proper_nouns = ["QProgram", "Qblox", "QDAC"]

# The site config holding the nav, relative to the repo root. Read as TOML.
site_config = "zensical.toml"

# The project's own DSL, if it has one. A bare fence opening with `header` is
# parsed by calling `module.<loader>(text)`.
[dsl]
header = "#!QProgram"
loader = "loads"
# Entry-point group of vendor extensions to activate first, and the attribute on
# the first `instances` class that lists what they registered.
vendor_group = "qprogram.vendors"
vendor_registry = "_vendor_registry"
```
