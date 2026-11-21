#!/usr/bin/env python3
"""Entrypoint: write the passport spread to the grader's output dir.

The spread is pre-rendered (see render.py) and shipped in the repo as
entry.png; this program only copies it out. It uses the standard library
alone, so it runs in the grader sandbox with no extra packages.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    src = os.path.join(HERE, "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.copyfile(src, dst)
    # fail loudly rather than hand the grader a corrupt file
    with open(dst, "rb") as fh:
        if fh.read(8) != b"\x89PNG\r\n\x1a\n":
            raise SystemExit("entry.png is not a PNG")
    print(f"wrote {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
