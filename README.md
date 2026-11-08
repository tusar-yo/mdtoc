# mdtoc

Generate (and keep up to date) a table of contents for any Markdown file. Zero dependencies, pure Python.

- GitHub-compatible anchors, including duplicate headings (`#usage`, `#usage-1`)
- Ignores `#` lines inside fenced code blocks
- `--check` mode for CI so a stale TOC fails the build

## Install

```
pip install git+https://github.com/tusar-yo/mdtoc.git
```

## Usage

Print a TOC for a file:

```
$ mdtoc README.md
- [mdtoc](#mdtoc)
  - [Install](#install)
  - [Usage](#usage)
```

Keep one inside the file. Add these two markers where you want it:

```
<!-- toc -->
<!-- tocstop -->
```

then run:

```
mdtoc README.md --write      # update in place
mdtoc README.md --check      # exit 1 if out of date (CI / pre-commit)
```

Options: `--min-depth N` and `--max-depth N` limit which heading levels are included.

Exit codes: `0` ok, `1` stale (`--check` only), `2` file or marker error.

## Develop

```
python -m unittest discover -s tests -v
```

MIT licensed.
