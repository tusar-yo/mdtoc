"""mdtoc: generate a table of contents for Markdown files."""
from .core import headings, slugify, build_toc, update_document, START, END

__all__ = ["headings", "slugify", "build_toc", "update_document", "START", "END"]
__version__ = "0.1.0"
