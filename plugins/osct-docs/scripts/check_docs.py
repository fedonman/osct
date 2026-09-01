# Copyright 2026 Qilimanjaro Quantum Tech
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Check documentation for broken examples, broken links, and style drift.

Three groups of checks:

  code    Python fences must parse. Bare fences that open with the project's DSL header
          must load through the real parser. Attributes read off the project's module,
          or off an instance of one of its configured classes, must exist on the
          installed package. A dotted read such as `qp.waveforms.Gaussian` is resolved
          one attribute at a time, descending while each hop is a module, so a typo at
          any depth is reported.
  links   Relative `.md` links and their anchors must resolve. Every page under docs_dir
          must appear in the site nav.
  style   House writing rules: no em dashes, no filler vocabulary, sentence-case
          headings, wrapped prose, bullets only where they enumerate something.

Code and link findings are errors, because they are objectively broken. Style findings
are warnings, because an existing tree usually carries a backlog of them. `--strict`
promotes warnings to errors, which is what a CI gate should use once the backlog is
cleared.

What is project-specific lives in `.osct/docs/config.toml`, which is found by walking up
from the working directory. Run the checker from the directory that config sits beside,
so the project's own package is importable:

    uv run python "${CLAUDE_PLUGIN_ROOT}/scripts/check_docs.py" docs

Without the configured module on the path the code group degrades to syntax checking
only and says so. Exit status is 1 when anything at error severity is reported.
"""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import re
import sys
import tomllib
import types
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

Severity = Literal["error", "warning"]

CONFIG_PATH = Path(".osct/docs/config.toml")


@dataclass
class Config:
    """The per-project knobs, read from ``.osct/docs/config.toml``.

    Every field has a default that degrades to a weaker but still correct check, so a
    repo with no config file is checked for style, links, and Python syntax.
    """

    module: str = ""
    aliases: list[str] = field(default_factory=list)
    instances: list[str] = field(default_factory=list)
    site_config: str = ""
    dsl_header: str = ""
    dsl_loader: str = "loads"
    vendor_group: str = ""
    vendor_registry: str = ""

    @classmethod
    def load(cls, path: Path | None = None) -> Config:
        """Read the config, searching upwards from the working directory when unnamed.

        Args:
            path (Path | None): An explicit config file, or None to search for one.

        Returns:
            Config: The parsed config, or defaults when no file was found.
        """
        if path is None:
            for parent in (Path.cwd(), *Path.cwd().parents):
                candidate = parent / CONFIG_PATH
                if candidate.is_file():
                    path = candidate
                    break
        if path is None or not path.is_file():
            return cls()
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        dsl = data.get("dsl", {})
        # Heading capitalisation is checked in one place well below this, so the project's
        # own product names are folded into the shared set rather than threaded through.
        PROPER_NOUNS.update(data.get("proper_nouns", []))
        return cls(
            module=data.get("module", ""),
            aliases=list(data.get("aliases", [])),
            instances=list(data.get("instances", [])),
            site_config=data.get("site_config", ""),
            dsl_header=dsl.get("header", ""),
            dsl_loader=dsl.get("loader", "loads"),
            vendor_group=dsl.get("vendor_group", ""),
            vendor_registry=dsl.get("vendor_registry", ""),
        )

# Words and phrases that read as generated text. Curated to stay quiet on this repo's
# vocabulary: technical terms that happen to sound emphatic ("real-time", "canonical")
# are not listed, and neither are words with a precise meaning here ("ensure", "handle").
FILLER_PATTERNS: dict[str, str] = {
    r"\bhonestly\b": "drop it",
    r"\bseamless(ly)?\b": "say what actually happens",
    r"\bpowerful\b": "say what it does instead",
    r"\brobust\b": "say what it tolerates instead",
    r"\bunlock(s|ing)?\b": "say what becomes possible",
    r"\bdelve\b": "use 'look at' or just start",
    r"\bleverag(e|es|ing)\b": "use",
    r"\bgame[- ]chang\w*": "drop it",
    r"\bat its core\b": "drop it",
    r"\bit(\u2019|')?s worth noting\b": "state the fact directly",
    r"\bit is worth noting\b": "state the fact directly",
    r"\bin today(\u2019|')?s world\b": "drop it",
    r"\bwhether you(\u2019|')?re? (a|an) \w+ or\b": "drop the audience framing",
    r"\bdive (in|into)\b": "use 'look at' or just start",
    r"\bembark\b": "drop it",
    r"\bcutting[- ]edge\b": "drop it",
    r"\bstate[- ]of[- ]the[- ]art\b": "drop it",
    r"\beffortless(ly)?\b": "say what the work is",
    r"\bsupercharge\w*": "drop it",
    r"\brevolution(ise|ize|ary|ises|izes)\b": "drop it",
    r"\bplethora\b": "use 'many'",
    r"\bmyriad\b": "use 'many'",
    r"\butilis(e|es|ing)\b|\butiliz(e|es|ing)\b": "use 'use'",
    r"\bcrucial(ly)?\b": "say why it matters instead",
    r"\bvital(ly)?\b": "say why it matters instead",
    r"\ba testament to\b": "drop it",
    r"\bin conclusion\b": "drop it",
    r"\bto sum up\b": "drop it",
    r"\bthat(\u2019|')?s (it|all there is to it)\b": "drop it",
    r"\blet(\u2019|')?s (dive|explore|take a look)\b": "just start",
    r"\bsimply\b": "drop it, or say what makes it simple",
    r"\bjust works\b": "say what it does",
}

# Words allowed to stay capitalised mid-heading. Anything else capitalised mid-heading
# looks like Title Case, which the house style does not use.
PROPER_NOUNS = {
    "Python",
    "GitHub",
    "Markdown",
    "VS",
    "Code",
    "LSP",
    "CI",
    "API",
    "AST",
    "DSL",
    "JSON",
    "YAML",
    "TOML",
}

MAX_LINE = 88
MAX_BULLET_RUN = 12

# Checks that describe the machine running them rather than the page being checked.
# `--strict` leaves these at warning, so a CI gate does not depend on which vendor
# extensions happen to be installed in the environment.
ENVIRONMENTAL_CHECKS = frozenset({"dsl-vendor"})


@dataclass
class Finding:
    """One reported problem, at one line of one file."""

    path: Path
    line: int
    severity: Severity
    check: str
    message: str

    def format(self, root: Path) -> str:
        """Render as ``path:line: severity: check: message``, relative to ``root``.

        Returns:
            str: The one-line rendering.
        """
        try:
            shown = self.path.relative_to(root)
        except ValueError:
            shown = self.path
        return f"{shown}:{self.line}: {self.severity}: {self.check}: {self.message}"


@dataclass
class Fence:
    """One fenced code block, with the 1-based line of its first content line."""

    lang: str
    line: int
    text: str
    skip: bool = False


@dataclass
class Doc:
    """A parsed Markdown file: its lines, its fences, and which lines are not prose."""

    path: Path
    lines: list[str]
    fences: list[Fence] = field(default_factory=list)
    # 1-based line numbers that sit inside a fence, including the fence markers.
    fenced_lines: set[int] = field(default_factory=set)


FENCE_RE = re.compile(r"^(\s*)```(\S*)\s*$")
SKIP_RE = re.compile(r"<!--\s*check:\s*skip\s*-->")
# Signals that a snippet is illustrative rather than runnable: an elision line, an
# elided argument, or an angle-bracket placeholder. Consulted only when a fence fails
# to parse, so valid code is never waved through.
PLACEHOLDER_RES = (
    re.compile(r"^\s*\.\.\.,?\s*(#.*)?$", re.MULTILINE),
    re.compile(r"[(,]\s*\.\.\.\s*[,)]"),
    re.compile(r"<[a-z_][a-z0-9_]*>"),
)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
LINK_RE = re.compile(r"\]\(([^)#\s]*\.md)?(#[^)\s]+)?\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
DIRECTIVE_RE = re.compile(r"^:::\s+(\S+)")
BULLET_RE = re.compile(r"^\s*([-*+]|\d+\.)\s+\S")
# A definition-style item names something and then explains it. A run of these is a
# glossary, which the style rules allow; a run of prose sentences is chopped-up prose,
# which they do not. Only the second kind is worth flagging.
DEFINITION_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+(?:\*\*[^*]+\*\*|`[^`]+`)[^.]{0,120}?[:.]")


def read_doc(path: Path) -> Doc:
    """Read ``path`` and mark its fences, frontmatter and directive blocks.

    Args:
        path (Path): The Markdown file to read.

    Returns:
        Doc: The parsed document.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    doc = Doc(path=path, lines=lines)
    open_at: int | None = None
    lang = ""
    buf: list[str] = []
    skip = False
    skip_next = False

    # YAML frontmatter is metadata, not prose. Skills carry it; docs pages do not.
    if lines and lines[0].strip() == "---":
        closing = next((i for i, line in enumerate(lines[1:51], start=2) if line.strip() == "---"), None)
        if closing:
            doc.fenced_lines.update(range(1, closing + 1))

    # A `::: symbol` directive is followed by an indented YAML option block. That is
    # mkdocstrings configuration, not prose, and its `members:` list is not a bullet list.
    in_directive = False
    for i, line in enumerate(lines, start=1):
        if DIRECTIVE_RE.match(line):
            in_directive = True
            doc.fenced_lines.add(i)
            continue
        if in_directive:
            if not line.strip() or line.startswith((" ", "\t")):
                doc.fenced_lines.add(i)
                continue
            in_directive = False

    for i, line in enumerate(lines, start=1):
        m = FENCE_RE.match(line)
        if open_at is None:
            if SKIP_RE.search(line):
                skip_next = True
            elif m:
                open_at, lang, buf, skip = i, m.group(2), [], skip_next
                skip_next = False
                doc.fenced_lines.add(i)
            elif line.strip():
                skip_next = False
            continue
        doc.fenced_lines.add(i)
        if m and not m.group(2):
            doc.fences.append(Fence(lang=lang, line=open_at + 1, text="\n".join(buf), skip=skip))
            open_at = None
            continue
        buf.append(line)
    if open_at is not None:
        doc.fences.append(Fence(lang=lang, line=open_at + 1, text="\n".join(buf), skip=skip))
    return doc


def prose_lines(doc: Doc) -> Iterator[tuple[int, str]]:
    """Yield (line number, text) for lines that carry prose, not code."""
    for i, line in enumerate(doc.lines, start=1):
        if i in doc.fenced_lines:
            continue
        yield i, line


def slugify(heading: str) -> str:
    """Convert heading text to the anchor a Markdown renderer would generate.

    Args:
        heading (str): The heading text, without its leading hashes.

    Returns:
        str: The anchor slug.
    """
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = re.sub(r"[`*_]", "", text).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text).strip("-")


# --------------------------------------------------------------------------- style


def check_style(doc: Doc) -> Iterator[Finding]:
    """Yield the writing-style findings for one document.

    Args:
        doc (Doc): The parsed document.

    Yields:
        Finding: One finding per style rule broken.
    """

    def finding(line: int, check: str, message: str) -> Finding:
        return Finding(doc.path, line, "warning", check, message)

    bullet_run = 0
    bullet_run_start = 0
    definitions = 0
    last_level = 0
    in_table = False

    for i, raw in prose_lines(doc):
        stripped = INLINE_CODE_RE.sub("``", raw)

        for ch, name in (("\u2014", "em dash"), ("\u2013", "en dash")):
            if ch in stripped:
                yield finding(i, "em-dash", f"{name} in prose; use a comma, colon, parentheses, or two sentences")
                break

        lowered = stripped.lower()
        for pattern, advice in FILLER_PATTERNS.items():
            m = re.search(pattern, lowered)
            if m:
                yield finding(i, "filler", f"{m.group(0)!r}: {advice}")

        in_table = raw.lstrip().startswith("|")
        # A line holding nothing but links cannot be wrapped: each URL is one token. The
        # label may itself be an image, which is what a row of README badges is, and a
        # badge row puts several of them on one line.
        is_link_only = bool(
            re.fullmatch(r"\s*(?:[-*]|\d+\.)?\s*(?:!?\[(?:!?\[[^\]]*\]\([^)]*\)|[^\]])*\]\([^)]*\)\s*)+[.,;:]?\s*", raw)
        )
        if len(raw) > MAX_LINE and not in_table and not is_link_only:
            yield finding(i, "long-line", f"{len(raw)} chars; wrap prose near 80")

        heading = HEADING_RE.match(raw)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2)
            if last_level and level > last_level + 1:
                yield finding(i, "heading-depth", f"h{last_level} to h{level} skips a level")
            last_level = level
            if title_cased(title):
                yield finding(i, "heading-case", f"{title!r} reads as Title Case; use sentence case")

        if BULLET_RE.match(raw):
            if bullet_run == 0:
                bullet_run_start = i
                definitions = 0
            bullet_run += 1
            if DEFINITION_RE.match(raw):
                definitions += 1
        elif raw.strip() and not raw.startswith(("  ", "\t")):
            if bullet_run > MAX_BULLET_RUN and definitions * 2 < bullet_run:
                yield finding(
                    bullet_run_start,
                    "bullet-run",
                    f"{bullet_run} consecutive list items; prose carries reasoning better than a long list",
                )
            bullet_run = 0

    if bullet_run > MAX_BULLET_RUN and definitions * 2 < bullet_run:
        yield finding(bullet_run_start, "bullet-run", f"{bullet_run} consecutive list items")


def title_cased(title: str) -> bool:
    """Report whether a heading reads as Title Case rather than sentence case.

    Args:
        title (str): The heading text.

    Returns:
        bool: True when two or more mid-heading words are capitalized.
    """
    text = re.sub(r"`[^`]*`", "", title)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    words = re.findall(r"[A-Za-z][\w'-]*", text)
    if len(words) < 3:
        return False
    capitalised = 0
    for word in words[1:]:
        if word in PROPER_NOUNS or word.isupper() or any(c.isdigit() for c in word):
            continue
        if word[0].isupper():
            capitalised += 1
    return capitalised >= 2


# ---------------------------------------------------------------------------- code


def _activate_installed_vendors(group: str) -> list[str]:
    """Import every package registered under an entry-point group.

    Args:
        group (str): The entry-point group, or empty to activate nothing.

    Returns:
        list[str]: The names of the vendors that activated.
    """
    from importlib.metadata import entry_points  # ruff: ignore[import-outside-top-level]

    activated: list[str] = []
    if not group:
        return activated
    try:
        found = entry_points(group=group)
    except Exception:  # ruff: ignore[blind-except] - a broken metadata cache must not fail the checks
        return activated
    for entry in found:
        try:
            entry.load()
        except Exception:  # ruff: ignore[blind-except, try-except-continue] - a broken extension is not this tool's problem
            continue
        activated.append(entry.name)
    return activated


class ApiIndex:
    """Attribute names reachable on the installed package, for staleness checks."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.available = False
        self.module: Any = None
        self.attrs: dict[str, set[str]] = {}
        self.note = ""
        if not config.module:
            self.note = f"no module named in {CONFIG_PATH}; examples were only syntax-checked"
            return
        try:
            self.module = importlib.import_module(config.module)
        except ImportError as exc:
            self.note = f"{config.module} not importable ({exc}); DSL parsing and API checks were skipped"
            return
        self.available = True
        # Activate every installed vendor extension, the same way the loader does. Without
        # this, a vendor repo's own examples (`program.qdac.play(...)`, a DSL file with
        # `require qdac`) look like references to things that do not exist.
        self.activated = _activate_installed_vendors(config.vendor_group)
        vendors: set[str] = set()
        if config.vendor_registry and config.instances:
            root = getattr(self.module, config.instances[0], None)
            vendors = set(getattr(root, config.vendor_registry, {}) or {})
        for name in config.instances:
            owner = getattr(self.module, name, None)
            if owner is None:
                self.note = f"{config.module} has no {name!r}; check the instances list in {CONFIG_PATH}"
                continue
            self.attrs[name] = set(dir(owner)) | vendors

    def has_module_attr(self, name: str) -> bool:
        """Report whether the configured module has this attribute.

        Args:
            name (str): The attribute name.

        Returns:
            bool: True when the attribute exists.
        """
        return hasattr(self.module, name)

    def has_attr(self, kind: str, name: str) -> bool:
        """Report whether a tracked class of object has this attribute.

        Args:
            kind (str): The class name, one of the configured ``instances``.
            name (str): The attribute name.

        Returns:
            bool: True when the attribute exists on that class.
        """
        return name in self.attrs.get(kind, set())


SKIPPED_LANGS = frozenset({"bash", "console", "shell", "toml", "text", "json", "yaml", "diff"})


def check_code(doc: Doc, api: ApiIndex) -> Iterator[Finding]:
    """Yield findings for the Python and DSL examples in one document.

    Args:
        doc (Doc): The parsed document.
        api (ApiIndex): The installed package surface to check names against.

    Yields:
        Finding: One finding per broken or stale example.
    """
    # Names bound anywhere in the page. Snippets read as one continuous script, which is
    # how a reader follows them, so a `program = qp.QProgram(...)` in an early fence still
    # tells us what `program.play(...)` is three fences later.
    aliases = {name: "module" for name in (api.config.module, *api.config.aliases) if name}
    local_defs = collect_local_definitions(doc)

    for fence in doc.fences:
        if fence.skip or fence.lang in SKIPPED_LANGS:
            continue
        if fence.lang == "python":
            yield from check_python_fence(doc, fence, api, aliases, local_defs)
        elif not fence.lang and api.config.dsl_header and fence.text.lstrip().startswith(api.config.dsl_header):
            yield from check_dsl_fence(doc, fence, api)


def collect_local_definitions(doc: Doc) -> set[str]:
    """Names the page itself defines, which the installed package is not expected to have.

    Returns:
        set[str]: Every name the page defines with ``def`` or ``class``.

    The developer guide walks through adding an operation, so it writes `def set_power`
    before any `program.set_power(...)` call. Those calls are correct documentation of
    code that does not exist yet, and must not be reported as stale.
    """
    names: set[str] = set()
    for fence in doc.fences:
        if fence.lang != "python":
            continue
        names.update(m.group(1) for m in re.finditer(r"^\s*(?:def|class)\s+([A-Za-z_]\w*)", fence.text, re.MULTILINE))
    return names


def looks_illustrative(text: str) -> bool:
    """Report whether a snippet uses elisions or placeholders rather than real code.

    Args:
        text (str): The snippet body.

    Returns:
        bool: True when the snippet is illustrative.
    """
    return any(p.search(text) for p in PLACEHOLDER_RES)


def check_python_fence(
    doc: Doc,
    fence: Fence,
    api: ApiIndex,
    aliases: dict[str, str],
    local_defs: set[str],
) -> Iterator[Finding]:
    """Parse one Python example and check the names it reads off the package.

    Args:
        doc (Doc): The document the fence came from.
        fence (Fence): The fence to check.
        api (ApiIndex): The installed package surface.
        aliases (dict[str, str]): Names bound earlier in the page, and what they are.
        local_defs (set[str]): Names the page defines itself.

    Yields:
        Finding: One finding per syntax error or stale name.
    """
    try:
        tree = ast.parse(fence.text)
    except SyntaxError as exc:
        if looks_illustrative(fence.text):
            return
        line = fence.line + (exc.lineno or 1) - 1
        yield Finding(
            doc.path,
            line,
            "error",
            "python-syntax",
            f"{exc.msg}; if the snippet is deliberately partial, put <!-- check: skip --> above the fence",
        )
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == api.config.module and alias.asname:
                    aliases[alias.asname] = "module"
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            func = node.value.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name in api.config.instances:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        aliases[target.id] = name

    if not api.available:
        return

    # An attribute node that is itself the base of a longer chain is covered by the outermost
    # node of that chain, so checking it again would report the same prefix twice.
    nested = {
        id(n.value) for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Attribute)
    }

    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute) or id(node) in nested:
            continue
        base, chain = dotted_chain(node)
        kind = aliases.get(base) if base else None
        if kind is None:
            continue
        for step, message in resolve_chain(api, local_defs, chain, kind):
            line = fence.line + step.lineno - 1
            yield Finding(doc.path, line, "warning", "stale-api", message)


def dotted_chain(node: ast.Attribute) -> tuple[str | None, list[ast.Attribute]]:
    """Split an attribute node into the name it starts from and the attributes read off it.

    Args:
        node (ast.Attribute): The outermost attribute node of the chain.

    Returns:
        tuple[str | None, list[ast.Attribute]]: The base name, or None when the chain does
            not start from a plain name, and the attribute nodes in source order.
    """
    chain: list[ast.Attribute] = []
    current: ast.expr = node
    while isinstance(current, ast.Attribute):
        chain.append(current)
        current = current.value
    if not isinstance(current, ast.Name):
        return None, []
    chain.reverse()
    return current.id, chain


def resolve_chain(
    api: ApiIndex,
    local_defs: set[str],
    chain: list[ast.Attribute],
    kind: str,
) -> Iterator[tuple[ast.Attribute, str]]:
    """Resolve ``qp.a.b.c`` attribute by attribute and report the first hop that is missing.

    Args:
        api (ApiIndex): The installed package surface.
        local_defs (set[str]): Names the page defines itself.
        chain (list[ast.Attribute]): The attribute nodes of one dotted read, outermost last.
        kind (str): What the base name is bound to: ``"module"``, or a configured class name.

    Yields:
        tuple[ast.Attribute, str]: The node the missing attribute was read on, and the message.

    Only a module is descended into. Once a hop resolves to a class or a function the rest of
    the chain is left alone, because a dataclass field and an instance attribute are both
    unreachable from the class object, and reporting them would be wrong.
    """
    attr = chain[0].attr
    if attr in local_defs or attr.startswith("_"):
        return

    if kind != "module":
        if not api.has_attr(kind, attr):
            yield chain[0], f"{kind} has no attribute {attr!r}"
        return

    owner: Any = api.module
    path = chain[0].value.id if isinstance(chain[0].value, ast.Name) else api.config.module
    for step in chain:
        attr = step.attr
        if attr in local_defs or attr.startswith("_"):
            return
        found = api.has_module_attr(attr) if owner is api.module else hasattr(owner, attr)
        if not found:
            if owner is api.module:
                yield step, f"the {api.config.module} package has no {attr!r}"
            else:
                yield step, f"{path} has no attribute {attr!r}"
            return
        owner = getattr(owner, attr)
        path = f"{path}.{attr}"
        if not isinstance(owner, types.ModuleType):
            return


def check_dsl_fence(doc: Doc, fence: Fence, api: ApiIndex) -> Iterator[Finding]:
    """Parse one complete DSL example with the project's real parser.

    Args:
        doc (Doc): The document the fence came from.
        fence (Fence): The fence to parse.
        api (ApiIndex): The installed package surface.

    Yields:
        Finding: One finding when the example does not parse.
    """
    loader = getattr(api.module, api.config.dsl_loader, None) if api.available else None
    if loader is None:
        return
    try:
        loader(fence.text)
    except Exception as exc:  # ruff: ignore[blind-except] - a parse error, or anything from a vendor
        message = str(exc).splitlines()[0]
        if "requires vendor" in message:
            yield Finding(doc.path, fence.line, "warning", "dsl-vendor", f"vendor not installed here: {message}")
            return
        yield Finding(doc.path, fence.line, "error", "dsl-parse", message)


# --------------------------------------------------------------------------- links


def check_links(docs: list[Doc], docs_dir: Path) -> Iterator[Finding]:
    """Yield findings for internal links and anchors that do not resolve.

    Args:
        docs (list[Doc]): The documents to report on.
        docs_dir (Path): The site root every relative link resolves against.

    Yields:
        Finding: One finding per unresolvable link or anchor.
    """
    # The index covers the whole site, not just the pages being checked, so that
    # checking one page resolves its links the same way checking the tree does.
    site = [read_doc(p) for p in collect_markdown([docs_dir])]
    known = {d.path.resolve().relative_to(docs_dir).as_posix() for d in site}
    anchors: dict[str, set[str]] = defaultdict(set)
    generated: dict[str, set[str]] = defaultdict(set)

    for doc in site:
        rel = doc.path.resolve().relative_to(docs_dir).as_posix()
        for _i, line in prose_lines(doc):
            heading = HEADING_RE.match(line)
            if heading:
                anchors[rel].add(slugify(heading.group(2)))
        # Directives are skipped as prose, so read them off the raw lines. The symbols
        # they name become page anchors at build time.
        for line in doc.lines:
            directive = DIRECTIVE_RE.match(line)
            if directive:
                generated[rel].add(directive.group(1))

    for doc in docs:
        rel_path = doc.path.resolve().relative_to(docs_dir)
        for i, line in prose_lines(doc):
            for m in LINK_RE.finditer(line):
                target, anchor = m.group(1), m.group(2)
                if target:
                    candidate = (docs_dir / rel_path.parent / target).resolve()
                    try:
                        dest = candidate.relative_to(docs_dir).as_posix()
                    except ValueError:
                        yield Finding(doc.path, i, "error", "link", f"{target} points outside docs/")
                        continue
                    if dest not in known:
                        yield Finding(doc.path, i, "error", "link", f"{target} does not exist")
                        continue
                else:
                    dest = rel_path.as_posix()
                if not anchor:
                    continue
                name = anchor[1:]
                if name in anchors[dest]:
                    continue
                if any(name == root or name.startswith(root + ".") for root in generated[dest]):
                    continue
                yield Finding(doc.path, i, "error", "anchor", f"{(target or '')}{anchor} has no matching heading")


def check_nav(docs: list[Doc], docs_dir: Path, config: Path) -> Iterator[Finding]:
    """Yield findings for pages missing from the nav, and nav entries missing from disk.

    Args:
        docs (list[Doc]): The documents found on disk.
        docs_dir (Path): The site root.
        config (Path): The site config holding the nav, read as TOML.

    Yields:
        Finding: One finding per mismatch between the nav and the tree.
    """
    if not config.exists():
        return
    data = tomllib.loads(config.read_text(encoding="utf-8"))
    nav = data.get("project", {}).get("nav", [])
    listed: set[str] = set()

    def collect(entry: object) -> None:
        if isinstance(entry, str):
            listed.add(entry)
        elif isinstance(entry, list):
            for item in entry:
                collect(item)
        elif isinstance(entry, dict):
            for value in entry.values():
                collect(value)

    collect(nav)

    on_disk = {d.path.resolve().relative_to(docs_dir).as_posix() for d in docs}
    for page in sorted(listed - on_disk):
        yield Finding(config, 1, "error", "nav", f"nav lists {page}, which does not exist")
    for page in sorted(on_disk - listed):
        yield Finding(docs_dir / page, 1, "warning", "nav", "not reachable from the site nav")


# ---------------------------------------------------------------------------- main


def infer_docs_dir(path: Path) -> Path:
    """Find the site root a path belongs to, so ``../reference/x.md`` resolves.

    Returns:
        Path: The site root.

    Checking one page must use the same root as checking the whole tree, or every
    link that climbs out of the page's own directory reads as a link out of the site.
    """
    resolved = path.resolve()
    for parent in (resolved, *resolved.parents):
        if parent.name == "docs" and parent.is_dir():
            return parent
    return resolved if resolved.is_dir() else resolved.parent


def collect_markdown(paths: Iterable[Path]) -> list[Path]:
    """Expand files and directories into the Markdown files to check.

    Args:
        paths (Iterable[Path]): Files or directories named on the command line.

    Returns:
        list[Path]: Every Markdown file named or contained by ``paths``.
    """
    found: list[Path] = []
    for path in paths:
        if path.is_dir():
            found.extend(sorted(path.rglob("*.md")))
        elif path.suffix == ".md":
            found.append(path)
    return found


def main(argv: list[str] | None = None) -> int:
    """Run the checks named on the command line.

    Args:
        argv (list[str] | None): Argument list, or None to read ``sys.argv``.

    Returns:
        int: 1 when anything at error severity was reported, else 0.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", type=Path, default=[Path("docs")], help="markdown files or directories")
    parser.add_argument("--only", choices=["style", "code", "links"], action="append", help="run one group only")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--json", action="store_true", dest="as_json", help="machine-readable output")
    parser.add_argument("--docs-dir", type=Path, help="site root for link and nav checks (default: the first path)")
    parser.add_argument("--config", type=Path, help="site config for the nav check (default: from the project config)")
    parser.add_argument("--project-config", type=Path, help=f"project config (default: nearest {CONFIG_PATH})")
    args = parser.parse_args(argv)

    config = Config.load(args.project_config)
    site_config = args.config or Path(config.site_config or "zensical.toml")
    paths = args.paths or [Path("docs")]
    groups = set(args.only or ["style", "code", "links"])
    files = collect_markdown(paths)
    if not files:
        print("no markdown files found", file=sys.stderr)
        return 2

    docs = [read_doc(p) for p in files]
    findings: list[Finding] = []
    api = ApiIndex(config)

    if "style" in groups:
        for doc in docs:
            findings.extend(check_style(doc))
    if "code" in groups:
        for doc in docs:
            findings.extend(check_code(doc, api))
    if "links" in groups:
        docs_dir = (args.docs_dir or infer_docs_dir(paths[0])).resolve()
        inside = [d for d in docs if d.path.resolve().is_relative_to(docs_dir)]
        findings.extend(check_links(inside, docs_dir))
        if len(inside) == len(collect_markdown([docs_dir])):
            findings.extend(check_nav(inside, docs_dir, site_config))

    if args.strict:
        # `dsl-vendor` reports which extensions this environment has, not a defect in the
        # page, so it stays a warning even under strict. Nothing an author writes fixes it.
        findings = [
            f if f.check in ENVIRONMENTAL_CHECKS else Finding(f.path, f.line, "error", f.check, f.message)
            for f in findings
        ]

    findings.sort(key=lambda f: (str(f.path), f.line, f.check))
    root = Path.cwd()

    if args.as_json:
        print(
            json.dumps(
                {
                    "note": api.note,
                    "findings": [
                        {
                            "path": str(f.path),
                            "line": f.line,
                            "severity": f.severity,
                            "check": f.check,
                            "message": f.message,
                        }
                        for f in findings
                    ],
                },
                indent=2,
            )
        )
    else:
        for f in findings:
            print(f.format(root))
        errors = sum(1 for f in findings if f.severity == "error")
        warnings = len(findings) - errors
        print(f"\n{len(files)} files, {errors} errors, {warnings} warnings")
        if api.note:
            print(api.note)

    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
