#!/usr/bin/env bash
# Set up .osct/ in the current repository and wire up CodeGraph.
# Safe to re-run: nothing already present is overwritten.
set -euo pipefail

skip_codegraph=0
for arg in "$@"; do
  case "$arg" in
    --no-codegraph) skip_codegraph=1 ;;
    -h|--help) sed -n '2,4p' "$0"; echo "usage: init.sh [--no-codegraph]"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

here=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
root=$(git rev-parse --show-toplevel) || { echo "not a git repository" >&2; exit 1; }
cd "$root"

say() { printf '  %s\n' "$*"; }

# `cp -n` warns on newer GNU coreutils and its replacement `--update=none` does
# not exist on BSD, so copy file by file and skip whatever is already there.
seed() { # seed <src-dir> <dest-dir>
  local src=$1 dest=$2 rel
  while IFS= read -r rel; do
    if [ -e "$dest/$rel" ]; then continue; fi
    mkdir -p "$dest/$(dirname "$rel")"
    cp "$src/$rel" "$dest/$rel"
  done < <(cd "$src" && find . -type f | sed 's|^\./||')
}

echo "osct init in $root"

# The working tree. cp -n leaves anything that already exists alone, so a second
# run never clobbers a project.md somebody has edited.
mkdir -p .osct/docs .osct/issue-ideas .osct/filed .osct/prs .osct/reviews .osct/review-replies
seed "$here/templates/osct" .osct
say ".osct/ ready (docs, issue-ideas, filed, prs, reviews, review-replies)"

# Keep it out of git without touching .gitignore, which is shared. --git-path
# resolves correctly inside a worktree, where .git is a file.
exclude=$(git rev-parse --git-path info/exclude)
mkdir -p "$(dirname "$exclude")"
touch "$exclude"
for pattern in '.osct/' '.codegraph/'; do
  if grep -qxF "$pattern" "$exclude"; then
    say "$pattern already excluded"
  else
    printf '%s\n' "$pattern" >> "$exclude"
    say "excluded $pattern"
  fi
done

# Issue templates, only when the project has none of its own. These are tracked
# files, so they are the one thing here that reaches a commit.
if compgen -G ".github/ISSUE_TEMPLATE/*" > /dev/null; then
  say ".github/ISSUE_TEMPLATE/ already exists, left alone"
else
  seed "$here/templates/github" .github
  say "wrote .github/ISSUE_TEMPLATE/ — tracked, review before committing"
fi

if [ "$skip_codegraph" = 1 ]; then
  say "skipped CodeGraph"
  exit 0
fi

# CodeGraph: the index the skills read instead of grepping. Installing wires the
# MCP server into Claude Code globally, which is a change outside this repo.
if ! command -v codegraph > /dev/null 2>&1; then
  if ! command -v npm > /dev/null 2>&1; then
    say "npm not found, skipped CodeGraph: install it from https://github.com/colbymchenry/codegraph"
    exit 0
  fi
  say "installing @colbymchenry/codegraph"
  npm install -g @colbymchenry/codegraph
fi

if [ -d .codegraph ]; then
  codegraph install --target claude --location global --yes
  say "CodeGraph wired into Claude Code; this project was already indexed"
else
  codegraph install --target claude --location global --yes --init
  say "CodeGraph wired into Claude Code and this project indexed"
fi
