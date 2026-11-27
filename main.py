#!/usr/bin/env python3
"""Make.fun news-image-20261126 entry program (account b63, layout V61).

The entry is a single pre-rendered image, "THE WORLD IN ONE PAGE", that
sums up Thursday 26 November 2026 in 50 stories:

    3 heroes  - Macy's 100th Thanksgiving parade postponed by the storm,
                the IRGC mine claim in the Strait of Hormuz, and the
                global market rebound after the Trump tariff salvo
    10 cards  - the day's top stories (Gaza, Kyiv, Bogor, Netanyahu,
                North Korea, SpaceX Starmind, UK migration, Russia's
                record defence budget, Bangkok, Germany)
    37 ALSO   - more stories of the day, tagged [C] confirmed,
                [R] reported, [CL] claim / 25 Nov event
    12 pins   - a world map with every pin tied to a story in the image

This program does one thing only: it copies the bundled entry.png into
the output directory the grader provides. It draws nothing and reads
nothing else.

Standard library only. No network, no third-party imports, no Pillow.
The grader runs it in a fresh container with a read-only repository,
so the source image is opened read-only and the destination is created
under MAKEFUN_OUTPUT_DIR (default "out"). The copy is verified
byte-for-byte: a mismatch fails loudly instead of shipping a bad file.

Usage:
    MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import shutil
import sys

ENTRY_NAME = "entry.png"
MAX_BYTES = 1048576  # the bounty caps the image at 1 MiB
# the rendered image is 1024 x 1024, inside the 1024 x 1024 cap
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def source_path():
    """Absolute path of the bundled entry image, next to this file."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, ENTRY_NAME)


def output_path():
    """Destination path inside MAKEFUN_OUTPUT_DIR (default "out")."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    return os.path.join(out_dir, ENTRY_NAME)


def sha256_of(path):
    """SHA-256 hex digest of a file, read in 64 KiB chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_png(path):
    """The bundled file must be a whole PNG of at most 1 MiB."""
    with open(path, "rb") as handle:
        magic = handle.read(8)
    if magic != PNG_MAGIC:
        raise SystemExit("not a PNG file: %s" % path)
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise SystemExit("entry.png is %d bytes, over the 1 MiB limit"
                         % size)
    return size


def copy_entry():
    """Copy entry.png to the output directory and verify the copy."""
    src = source_path()
    if not os.path.isfile(src):
        raise SystemExit("missing bundled image: %s" % src)
    size = check_png(src)
    dst = output_path()
    parent = os.path.dirname(dst)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.copyfile(src, dst)
    if sha256_of(src) != sha256_of(dst):
        raise SystemExit("copy mismatch: %s != %s" % (src, dst))
    return dst, size


def main():
    """Copy the image and report where it landed."""
    dst, size = copy_entry()
    print("wrote %s (%d bytes, sha256 %s)"
          % (dst, size, sha256_of(dst)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
