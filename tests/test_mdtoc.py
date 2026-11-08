import os
import tempfile
import unittest

from mdtoc import START, END, build_toc, headings, slugify, update_document
from mdtoc.cli import main

DOC = """# Title

## Install

Some text.

```bash
# not a heading
## also not
```

## Usage

### Flags

## Usage
"""


class SlugTests(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(slugify("Hello, World!"), "hello-world")
        self.assertEqual(slugify("The `foo` [bar](http://x)"), "the-foo-bar")
        self.assertEqual(slugify("Under_score & more"), "under_score--more")


class HeadingTests(unittest.TestCase):
    def test_skips_code_fences(self):
        texts = [t for _, t in headings(DOC)]
        self.assertEqual(texts, ["Title", "Install", "Usage", "Flags", "Usage"])

    def test_tilde_fence_and_closing_hashes(self):
        doc = "~~~\n# no\n~~~\n## Yes ##\n"
        self.assertEqual(headings(doc), [(2, "Yes")])


class TocTests(unittest.TestCase):
    def test_build_nested(self):
        toc = build_toc(DOC)
        self.assertIn("- [Title](#title)", toc)
        self.assertIn("  - [Install](#install)", toc)
        self.assertIn("    - [Flags](#flags)", toc)

    def test_duplicate_anchors(self):
        toc = build_toc(DOC)
        self.assertIn("(#usage)", toc)
        self.assertIn("(#usage-1)", toc)

    def test_depth_limits(self):
        toc = build_toc(DOC, max_depth=2)
        self.assertNotIn("Flags", toc)
        toc = build_toc(DOC, min_depth=2)
        self.assertTrue(toc.startswith("- [Install]"))

    def test_empty(self):
        self.assertEqual(build_toc("just text"), "")


class UpdateTests(unittest.TestCase):
    def test_no_markers_unchanged(self):
        self.assertEqual(update_document(DOC), DOC)

    def test_replaces_block_and_is_idempotent(self):
        doc = f"{START}\nold stuff\n{END}\n\n{DOC}"
        once = update_document(doc)
        self.assertNotIn("old stuff", once)
        self.assertIn("[Install](#install)", once)
        self.assertEqual(update_document(once), once)

    def test_toc_block_not_counted_as_headings(self):
        doc = f"{START}\n# Fake\n{END}\n# Real\n"
        self.assertEqual(headings(doc), [(1, "Real")])


class CliTests(unittest.TestCase):
    def _file(self, content):
        fd, path = tempfile.mkstemp(suffix=".md")
        os.close(fd)
        open(path, "w").write(content)
        self.addCleanup(os.remove, path)
        return path

    def test_write_then_check(self):
        path = self._file(f"{START}\n{END}\n\n# A\n## B\n")
        self.assertEqual(main([path, "--check"]), 1)
        self.assertEqual(main([path, "--write"]), 0)
        self.assertEqual(main([path, "--check"]), 0)
        self.assertIn("[B](#b)", open(path).read())

    def test_missing_markers(self):
        path = self._file("# A\n")
        self.assertEqual(main([path, "--write"]), 2)

    def test_missing_file(self):
        self.assertEqual(main(["/nonexistent.md"]), 2)


if __name__ == "__main__":
    unittest.main()
