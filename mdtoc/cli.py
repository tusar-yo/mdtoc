import argparse
import sys

from .core import END, START, build_toc, update_document


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="mdtoc", description="Generate a Markdown table of contents.")
    ap.add_argument("file", help="Markdown file")
    ap.add_argument("-w", "--write", action="store_true",
                    help=f"update the block between {START} and {END} in place")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the in-file TOC is out of date (for CI)")
    ap.add_argument("--max-depth", type=int, default=6, help="deepest heading level to include (default 6)")
    ap.add_argument("--min-depth", type=int, default=1, help="shallowest heading level to include (default 1)")
    args = ap.parse_args(argv)

    try:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"mdtoc: {e}", file=sys.stderr)
        return 2

    if args.write or args.check:
        new = update_document(text, args.max_depth, args.min_depth)
        if START not in text or END not in text:
            print(f"mdtoc: no {START} / {END} markers in {args.file}", file=sys.stderr)
            return 2
        if args.check:
            if new != text:
                print(f"{args.file}: table of contents is out of date", file=sys.stderr)
                return 1
            return 0
        if new != text:
            with open(args.file, "w", encoding="utf-8") as f:
                f.write(new)
            print(f"updated {args.file}")
        else:
            print(f"{args.file} already up to date")
        return 0

    print(build_toc(text, args.max_depth, args.min_depth))
    return 0


if __name__ == "__main__":
    sys.exit(main())
