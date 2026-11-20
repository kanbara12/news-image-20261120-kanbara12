"""Run the news-image-20261120 front-page renderer and hand the PNG to the harness.

The page itself is drawn by render.py, which sits beside this file and
writes entry.png next to itself. All this entrypoint does is run that
renderer, then move the finished file into the directory the harness
names through MAKEFUN_OUTPUT_DIR (falling back to /output), using only
the standard library and no network at all. A second run writes the
same bytes, so the result is reproducible by construction.
"""

import os, runpy
from pathlib import Path as _Path

HERE = _Path(__file__).resolve().parent
DEST_DIR = _Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")


def _render_page() -> _Path:
    """Execute render.py as __main__ so it draws entry.png in HERE."""
    runpy.run_path(str(HERE / "render.py"), run_name="__main__")
    return HERE / "entry.png"


def _place(finished: _Path) -> _Path:
    """Copy the finished PNG into DEST_DIR and hand back its new path."""
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    target = DEST_DIR / finished.name
    target.write_bytes(finished.read_bytes())
    return target


def main() -> None:
    placed = _place(_render_page())
    print(f"entry ready: {placed} ({placed.stat().st_size} bytes)")


main()
