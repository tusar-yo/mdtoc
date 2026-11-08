import re
from typing import List, Tuple

START = "<!-- toc -->"
END = "<!-- tocstop -->"

_HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_FENCE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})")


def slugify(text: str) -> str:
    """GitHub-style heading anchor."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # [label](url) -> label
    text = text.replace("`", "")
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def headings(markdown: str) -> List[Tuple[int, str]]:
    """Return (level, text) for each heading, skipping fenced code and the TOC block."""
    out: List[Tuple[int, str]] = []
    fence = None
    in_toc = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped == START:
            in_toc = True
            continue
        if stripped == END:
            in_toc = False
            continue
        if in_toc:
            continue
        m = _FENCE.match(line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = marker[0] * 3
            elif marker.startswith(fence):
                fence = None
            continue
        if fence:
            continue
        h = _HEADING.match(line)
        if h:
            out.append((len(h.group(1)), h.group(2)))
    return out


def build_toc(markdown: str, max_depth: int = 6, min_depth: int = 1) -> str:
    items = [(lvl, txt) for lvl, txt in headings(markdown) if min_depth <= lvl <= max_depth]
    if not items:
        return ""
    base = min(lvl for lvl, _ in items)
    seen = {}
    lines = []
    for lvl, txt in items:
        slug = slugify(txt)
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        anchor = slug if n == 0 else f"{slug}-{n}"
        lines.append(f"{'  ' * (lvl - base)}- [{txt}](#{anchor})")
    return "\n".join(lines)


def update_document(markdown: str, max_depth: int = 6, min_depth: int = 1) -> str:
    """Replace the content between the toc markers. Returns input unchanged if no markers."""
    lines = markdown.split("\n")
    try:
        s = next(i for i, l in enumerate(lines) if l.strip() == START)
        e = next(i for i, l in enumerate(lines) if i > s and l.strip() == END)
    except StopIteration:
        return markdown
    toc = build_toc(markdown, max_depth, min_depth)
    middle = [""] + toc.split("\n") + [""] if toc else [""]
    return "\n".join(lines[: s + 1] + middle + lines[e:])
