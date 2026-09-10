"""Normalize an MDX page into plain GFM markdown.

Every component that carries content the site renders is expanded rather than
dropped: partials are inlined, both sides of a tab pair survive as labelled sections
(the rendered HTML keeps only the default one, D-001), and `SectionTab` headings
become ATX headings carrying the anchor the site deep-links to (D-003).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin

import structlog

from . import SITE_ORIGIN
from .anchors import AnchorAllocator, faq_slugify, section_tab_level
from .fences import collapse_blank_lines, iter_lines, map_outside_fences, trim_blank_edges
from .frontmatter import split as split_frontmatter
from .jsx import Element, Fence, Node, Text, parse

log = structlog.get_logger(__name__)

MAX_PARTIAL_DEPTH = 12

_IMPORT_LINE = re.compile(r"^(import|export)\s")
_IMPORT_DEFAULT = re.compile(
    r"^import\s+(?P<name>[A-Za-z_$][\w$]*)\s*(?:,\s*\{[^}]*\})?\s*from\s*['\"](?P<module>[^'\"]+)['\"]",
    re.DOTALL,
)
_FROM_CLAUSE = re.compile(r"from\s*['\"][^'\"]+['\"]")
_DIRECTIVE_OPEN = re.compile(r"^:::(?P<kind>[A-Za-z]+)(?:\[(?P<title>.*)\])?\s*$")
_DIRECTIVE_CLOSE = re.compile(r"^:::\s*$")
_LINK_TARGET = re.compile(r"(?P<open>\]\()(?P<target>[^)\s]*)")
# A target that already names a scheme (http, mailto, tel, data) is absolute.
_HAS_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_JS_STRING = re.compile(r"['\"]([^'\"]*)['\"]")

# Callout labels for `:::type` directives, keyed by the type the docs use.
_DIRECTIVE_LABELS = {
    "info": "Info",
    "note": "Note",
    "tip": "Tip",
    "warning": "Warning",
    "caution": "Caution",
    "important": "Important",
    "danger": "Danger",
}

# Tab values are language slugs; these render with their conventional casing.
_TAB_LABELS = {
    "python": "Python",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "ts": "TypeScript",
    "curl": "cURL",
    "bash": "Bash",
    "shell": "Shell",
    "json": "JSON",
    "go": "Go",
    "java": "Java",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "csharp": "C#",
    "output": "Output",
}

# Wrappers that only carry layout; their children are the content.
_TRANSPARENT = frozenset(
    {
        "Heading",
        "InterfaceCards",
        "InterfaceSection",
        "InterfaceSectionProvider",
        "NuqsAdapter",
        "Suspense",
        "UsefullLinkContainer",
        "article",
        "caption",
        "center",
        "div",
        "fieldset",
        "figcaption",
        "figure",
        "legend",
        "main",
        "p",
        "section",
        "span",
        "tbody",
        "thead",
    }
)

# Inline HTML that markdown either carries natively or does not need.
_INLINE_UNWRAP = frozenset(
    {"abbr", "b", "em", "font", "i", "kbd", "mark", "small", "sub", "sup", "u"}
)


@dataclass
class EmittedAnchor:
    """An anchor written into the page, with the site mechanism it came from."""

    anchor: str
    text: str
    kind: str  # section-tab | faq


@dataclass(frozen=True)
class Dropped:
    """One element the conversion could not carry over, and why."""

    component: str
    reason: str


@dataclass
class PageRender:
    """One normalized page plus what had to be dropped to produce it."""

    markdown: str
    anchors: list[EmittedAnchor] = field(default_factory=list)
    dropped: Counter[Dropped] = field(default_factory=Counter)
    partials: int = 0
    suppressed_anchors: int = 0


@dataclass
class _FileScope:
    """Per-file import bindings, so a partial resolves against its own directory."""

    directory: Path
    default_imports: dict[str, str]
    depth: int = 0


class MdxNormalizer:
    """Renders MDX files to markdown. One instance per page (state is per-page)."""

    def __init__(self, page_url: str, origin: str = SITE_ORIGIN) -> None:
        self.page_url = page_url
        self.origin = origin
        self.anchors = AnchorAllocator()
        self.emitted: list[EmittedAnchor] = []
        self.dropped: Counter[Dropped] = Counter()
        self.partials = 0
        self.suppressed_anchors = 0
        self._jsx_depth = 0

    def render_page(self, path: Path, title: str | None = None) -> PageRender:
        body = self._render_file(path, _FileScope(path.parent, {}, 0))
        # Links first: blockquoting a directive would otherwise indent its fenced code
        # behind a `>` prefix before the rewrite had a chance to skip it.
        body = self._absolutize_links(body)
        body = collapse_blank_lines(body)
        body = _apply_directives(body)
        body = collapse_blank_lines(body)
        body = _ensure_h1(body, title)
        return PageRender(
            markdown=body,
            anchors=list(self.emitted),
            dropped=Counter(self.dropped),
            partials=self.partials,
            suppressed_anchors=self.suppressed_anchors,
        )

    def _render_file(self, path: Path, scope: _FileScope) -> str:
        _, body = split_frontmatter(path.read_text(encoding="utf-8"))
        body, default_imports = _strip_imports(body)
        scope = _FileScope(path.parent, default_imports, scope.depth)
        return self._render_nodes(parse(body), scope)

    def _render_nodes(self, nodes: list[Node], scope: _FileScope) -> str:
        return "".join(self._render_node(node, scope) for node in nodes)

    def _render_node(self, node: Node, scope: _FileScope) -> str:
        if isinstance(node, Fence):
            return f"\n\n{node.raw}\n\n"
        if isinstance(node, Text):
            return node.value
        return self._render_element(node, scope)

    def _render_element(self, element: Element, scope: _FileScope) -> str:
        name = element.name
        module = scope.default_imports.get(name)
        if module is not None and module.endswith((".mdx", ".md")):
            return self._inline_partial(element, module, scope)

        handler = getattr(self, f"_el_{name.replace('.', '_').replace('-', '_')}", None)
        if handler is not None:
            return str(handler(element, scope))
        if name in _TRANSPARENT:
            return _block(self._children(element, scope))
        if name in _INLINE_UNWRAP:
            return self._children(element, scope)
        children = self._children(element, scope)
        if not children.strip():
            # Nothing textual survives, so the element's content lived in attributes
            # this converter does not understand. Record it rather than lose it silently.
            self._drop(name, "no text content")
        else:
            self._drop(name, "unsupported component, text kept")
        return _block(children)

    def _drop(self, component: str, reason: str) -> None:
        """The one place an element is written off, so the summary sees every loss."""
        self.dropped[Dropped(component=component, reason=reason)] += 1

    def _children(self, element: Element, scope: _FileScope) -> str:
        self._jsx_depth += 1
        try:
            return _dedent(self._render_nodes(element.children, scope))
        finally:
            self._jsx_depth -= 1

    def _inline_partial(self, element: Element, module: str, scope: _FileScope) -> str:
        if scope.depth >= MAX_PARTIAL_DEPTH:
            log.warning("partial nesting too deep", component=element.name, module=module)
            self._drop(element.name, "partial nesting deeper than the limit")
            return ""
        target = (scope.directory / module).resolve()
        if not target.is_file():
            log.warning("partial not found", component=element.name, path=str(target))
            self._drop(element.name, "partial file not found")
            return ""
        self.partials += 1
        child_scope = _FileScope(target.parent, {}, scope.depth + 1)
        return _block(_dedent(self._render_file(target, child_scope)))

    def _el_SectionTab(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        text = _plain_text(element.children).strip()
        if not text:
            return ""
        level = section_tab_level(element.attr("as"), element.attr("variant"))
        section_id = element.attr("sectionId")
        if not section_id:
            # The component sets its DOM id from `sectionId` alone. The site's table of
            # contents invents a slug when the prop is missing, but nothing on the page
            # carries that id, so linking to it would scroll nowhere.
            self.suppressed_anchors += 1
            return _block(f"{'#' * level} {text}")
        if self._jsx_depth > 0 or scope.depth > 0:
            # Nested in JSX or pulled in from a partial: the site renders such a
            # SectionTab only while its tab is open and leaves it out of the table of
            # contents, so the id is not a link anyone can follow.
            self.suppressed_anchors += 1
            return _block(f"{'#' * level} {text}")
        anchor = self.anchors.reserve(section_id)
        self.emitted.append(EmittedAnchor(anchor=anchor, text=text, kind="section-tab"))
        return _block(f"{'#' * level} {text} {{#{anchor}}}")

    def _el_HeadingTitle(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        text = _plain_text(element.children).strip()
        if not text:
            return ""
        as_prop = element.attr("as") or "h2"
        level = int(as_prop[1]) if re.fullmatch(r"h[1-6]", as_prop) else 2
        return _block(f"{'#' * level} {text}")

    def _el_Faq(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        return _block(self._children(element, scope))

    def _el_FaqItem(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        question = (element.attr("question") or "").strip()
        body = self._children(element, scope)
        if not question:
            return _block(body)
        # The Faq accordion renders `id = id ?? slugify(question)`, so this anchor is
        # a real deep link even though the question is not a markdown heading.
        anchor = self.anchors.reserve(element.attr("id") or faq_slugify(question))
        self.emitted.append(EmittedAnchor(anchor=anchor, text=question, kind="faq"))
        return _block(f"### {question} {{#{anchor}}}") + _block(body)

    def _el_Tabs(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        return _block(self._children(element, scope))

    def _el_ExplorerTabs(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        return _block(self._children(element, scope))

    def _el_TabItem(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        return self._labelled_tab(element, scope)

    def _el_ExplorerTab(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        return self._labelled_tab(element, scope)

    def _el_ExplorerTabItem(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        return self._labelled_tab(element, scope)

    def _labelled_tab(self, element: Element, scope: _FileScope) -> str:
        label = element.attr("label") or element.attr("value") or ""
        label = _TAB_LABELS.get(label.strip().lower(), label.strip())
        body = self._children(element, scope)
        if not label:
            return _block(body)
        # A bold line, never a heading: tab variants are alternatives, not sections.
        return _block(f"**{label}**") + _block(body)

    def _el_LinkCard(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        title = (element.attr("title") or "").strip()
        href = _href_value(element)
        description = (element.attr("description") or "").strip()
        text = title or _plain_text(element.children).strip() or href
        if not href:
            return _block(text)
        line = f"- [{text}]({href})"
        if description:
            line += f" — {description}"
        return f"\n{line}\n"

    def _el_AppLink(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        href = _href_value(element)
        text = _plain_text(element.children).strip()
        if not text:
            text = " > ".join(_JS_STRING.findall(element.attr("path") or "")) or href
        return f"[{text}]({href})" if href else text

    def _el_CtaButton(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        href = _href_value(element)
        text = _plain_text(element.children).strip() or href
        return _block(f"[{text}]({href})") if href else _block(text)

    def _el_CollabButton(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        url = (element.attr("colabUrl") or "").strip()
        return _block(f"[Open in Google Colab]({url})") if url else ""

    def _el_a(self, element: Element, scope: _FileScope) -> str:
        href = _href_value(element)
        text = self._children(element, scope).strip()
        return f"[{text}]({href})" if href else text

    def _el_img(self, element: Element, scope: _FileScope) -> str:
        return self._image(element)

    def _el_Image(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        return self._image(element)

    def _el_iframe(self, element: Element, scope: _FileScope) -> str:
        return self._embed(element, "Embedded media")

    def _el_video(self, element: Element, scope: _FileScope) -> str:
        return self._embed(element, "Video")

    def _el_audio(self, element: Element, scope: _FileScope) -> str:
        return self._embed(element, "Audio sample")

    def _embed(self, element: Element, fallback: str) -> str:
        """An embed carries its content in attributes; keep it as a titled link."""
        src = _first_source(element, ("src", "url"))
        if not src:
            self._drop(element.name, "no resolvable source")
            return ""
        # The children of an embed are the "your browser cannot play this" fallback,
        # so the title comes from the attribute or from the kind of embed it is.
        title = _attr_value(element, "title") or fallback
        return _block(f"[{title}]({src})")

    def _image(self, element: Element) -> str:
        src = _first_source(element, ("src", "url"))
        if not src:
            self._drop(element.name, "image source is an expression")
            return ""
        alt = (element.attr("alt") or "").strip()
        return f"\n\n![{alt}]({src})\n\n"

    def _el_br(self, element: Element, scope: _FileScope) -> str:
        # A cell break in a GFM table; a space keeps the row on one line.
        return " "

    def _el_hr(self, element: Element, scope: _FileScope) -> str:
        return "\n\n---\n\n"

    def _el_details(self, element: Element, scope: _FileScope) -> str:
        return _block(self._children(element, scope))

    def _el_summary(self, element: Element, scope: _FileScope) -> str:
        text = _plain_text(element.children).strip()
        return _block(f"**{text}**") if text else ""

    def _el_code(self, element: Element, scope: _FileScope) -> str:
        text = _plain_text(element.children).strip()
        return f"`{text}`" if text else ""

    def _el_Table(self, element: Element, scope: _FileScope) -> str:  # noqa: N802
        header: list[str] = []
        rows: list[list[str]] = []
        for row in _find_elements(element, {"TableRow"}):
            heads = [self._cell(cell, scope) for cell in _find_elements(row, {"TableHead"})]
            cells = [self._cell(cell, scope) for cell in _find_elements(row, {"TableCell"})]
            if heads and not header:
                header = heads
            elif cells:
                rows.append(cells)
        if not header and not rows:
            return _block(self._children(element, scope))
        width = max(len(header), *(len(row) for row in rows), 0)
        header = header or [""] * width
        lines = [
            "| " + " | ".join(_pad(header, width)) + " |",
            "| " + " | ".join(["---"] * width) + " |",
        ]
        lines += ["| " + " | ".join(_pad(row, width)) + " |" for row in rows]
        return _block("\n".join(lines))

    def _el_table(self, element: Element, scope: _FileScope) -> str:
        return _block(self._children(element, scope))

    def _el_tr(self, element: Element, scope: _FileScope) -> str:
        """A row of a raw HTML table.

        These hold prompt transcripts whose cells contain fenced code, so the row
        becomes a labelled block rather than a GFM row that would break the fence.
        """
        cells = [
            child
            for child in element.children
            if isinstance(child, Element) and child.name in {"td", "th"}
        ]
        if len(cells) == 2:
            label = _plain_text(cells[0].children).strip()
            body = self._children(cells[1], scope)
            if label and "\n" not in label:
                return _block(f"**{label}**") + _block(body)
        return "".join(_block(self._children(cell, scope)) for cell in cells)

    def _el_td(self, element: Element, scope: _FileScope) -> str:
        return _block(self._children(element, scope))

    def _el_th(self, element: Element, scope: _FileScope) -> str:
        text = _plain_text(element.children).strip()
        return _block(f"**{text}**") if text else ""

    def _cell(self, element: Element, scope: _FileScope) -> str:
        text = self._render_nodes(element.children, scope)
        return " ".join(text.split()).replace("|", "\\|")

    def _absolutize_links(self, markdown: str) -> str:
        """Resolve every link and image target against the page's own URL.

        Site-absolute (`/x`), fragment (`#x`), sibling (`./x`, `../x`) and bare
        relative targets all appear in the MDX. Once the page is a file in the corpus
        rather than a URL on the site, only an absolute target still points anywhere.
        """

        def replace(match: re.Match[str]) -> str:
            target = absolutize_target(match.group("target"), self.page_url)
            return match.group("open") + target

        def rewrite(line: str) -> str:
            return _LINK_TARGET.sub(replace, line)

        return map_outside_fences(markdown, rewrite)


def _attr_value(element: Element | None, name: str) -> str:
    """An attribute's literal value, or empty when it is a JavaScript expression."""
    if element is None:
        return ""
    value = (element.attr(name) or "").strip().strip("\"'")
    return "" if value.startswith("{") else value


def _href_value(element: Element) -> str:
    """The `href` an element points at, resolving a concatenation of string literals.

    A few links are written as `href={"https://" + "admin.mistral.ai/..."}`; joining the
    literals reproduces what the browser gets, and an expression with no literals at all
    has no address this converter can recover.
    """
    literal = _attr_value(element, "href")
    if literal:
        return literal
    raw = (element.attr("href") or "").strip()
    if raw.startswith("{"):
        return "".join(_JS_STRING.findall(raw))
    return ""


def _first_source(element: Element, names: tuple[str, ...]) -> str:
    """The first media URL the element names, looking inside `{...}` expressions.

    The docs write `url={'/img/x.svg'}` and `url={['/img/light.png', '/img/dark.png']}`
    as well as plain attributes; all three name a real file, and only the light variant
    of a pair carries content.
    """
    for name in (*names, *(f"{name}Set" for name in names)):
        literal = _attr_value(element, name)
        if literal:
            return literal
        raw = (element.attr(name) or "").strip()
        if raw.startswith("{"):
            found = _JS_STRING.findall(raw)
            if found:
                return str(found[0])
    child = next(
        (node for node in element.children if isinstance(node, Element) and node.name == "source"),
        None,
    )
    return _attr_value(child, "src") if child is not None else ""


def absolutize_target(target: str, page_url: str) -> str:
    """Resolve one link target against `page_url`, leaving already-absolute ones alone."""
    if not target or _HAS_SCHEME.match(target):
        return target
    return urljoin(page_url, target)


def _block(text: str) -> str:
    """Surround a block-level rendering with blank lines; empty stays empty."""
    return f"\n\n{text.strip()}\n\n" if text.strip() else ""


def _pad(cells: list[str], width: int) -> list[str]:
    return [*cells, *([""] * (width - len(cells)))]


def _find_elements(element: Element, names: set[str]) -> list[Element]:
    """Depth-first search for the named descendants, not descending into matches."""
    found: list[Element] = []
    for child in element.children:
        if isinstance(child, Element):
            if child.name in names:
                found.append(child)
            else:
                found.extend(_find_elements(child, names))
    return found


def _plain_text(nodes: list[Node]) -> str:
    parts: list[str] = []
    for node in nodes:
        if isinstance(node, Text):
            parts.append(node.value)
        elif isinstance(node, Element):
            parts.append(_plain_text(node.children))
    return " ".join("".join(parts).split())


def _dedent(text: str) -> str:
    """Remove the common indent so nested JSX children are not indented code blocks."""
    lines = text.split("\n")
    indents = [len(line) - len(line.lstrip(" ")) for line in lines if line.strip()]
    if not indents:
        return text
    common = min(indents)
    if common == 0:
        return text
    return "\n".join(line[common:] if line.strip() else line for line in lines)


def _strip_imports(body: str) -> tuple[str, dict[str, str]]:
    """Remove `import`/`export` statements, returning the default-import bindings."""
    lines = list(iter_lines(body))
    out: list[str] = []
    default_imports: dict[str, str] = {}
    index = 0
    while index < len(lines):
        line, in_fence = lines[index]
        if in_fence or not _IMPORT_LINE.match(line):
            out.append(line)
            index += 1
            continue
        statement = [line]
        while not _statement_complete("\n".join(statement)) and index + 1 < len(lines):
            next_line, next_in_fence = lines[index + 1]
            if next_in_fence or not next_line.strip():
                break
            index += 1
            statement.append(next_line)
        match = _IMPORT_DEFAULT.match("\n".join(statement))
        if match is not None:
            default_imports[match.group("name")] = match.group("module")
        out.append("")
        index += 1
    return "\n".join(out), default_imports


def _statement_complete(statement: str) -> bool:
    if statement.count("{") != statement.count("}"):
        return False
    return statement.rstrip().endswith(";") or _FROM_CLAUSE.search(statement) is not None


def _apply_directives(markdown: str) -> str:
    """Turn `:::info` ... `:::` containers into labelled blockquotes."""
    lines = list(iter_lines(markdown))
    out: list[str] = []
    index = 0
    while index < len(lines):
        line, in_fence = lines[index]
        opener = None if in_fence else _DIRECTIVE_OPEN.match(line.strip())
        if opener is None:
            out.append(line)
            index += 1
            continue
        kind = opener.group("kind").lower()
        label = (opener.group("title") or _DIRECTIVE_LABELS.get(kind, kind.title())).strip()
        body: list[str] = []
        index += 1
        while index < len(lines):
            inner, inner_fence = lines[index]
            if not inner_fence and _DIRECTIVE_CLOSE.match(inner.strip()):
                index += 1
                break
            body.append(inner)
            index += 1
        quoted = [f"> **{label}**", ">"]
        quoted += [f"> {entry}".rstrip() for entry in trim_blank_edges(body)]
        out.extend(["", *quoted, ""])
    return "\n".join(out)


def _ensure_h1(markdown: str, title: str | None) -> str:
    """Prepend the frontmatter title as the H1 unless the body already opens with one."""
    if title is None:
        return markdown
    for line, in_fence in iter_lines(markdown):
        if in_fence or not line.strip():
            continue
        return markdown if line.startswith("# ") else f"# {title}\n\n{markdown}"
    return f"# {title}"
