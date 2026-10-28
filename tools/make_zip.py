#!/usr/bin/env python3
"""Build a deterministic ZIP with a fixed root directory."""

import stat
import sys
import zipfile
from pathlib import Path


FIXED_DATE_TIME = (1984, 1, 24, 0, 0, 0)


def add_directory(archive, source_root, archive_root):
    files = sorted(
        (path for path in source_root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(source_root).as_posix(),
    )
    for path in files:
        if path.is_symlink():
            raise RuntimeError(f"refusing to package symlink: {path}")
        relative = path.relative_to(source_root).as_posix()
        info = zipfile.ZipInfo(f"{archive_root}/{relative}", FIXED_DATE_TIME)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.create_system = 3
        mode = stat.S_IFREG | stat.S_IMODE(path.stat().st_mode)
        info.external_attr = mode << 16
        archive.writestr(
            info,
            path.read_bytes(),
            compress_type=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        )


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: make_zip.py SOURCE_DIR ARCHIVE_ROOT OUTPUT_ZIP")
    source_root = Path(sys.argv[1]).resolve()
    archive_root = sys.argv[2].strip("/")
    output_zip = Path(sys.argv[3]).resolve()
    if not source_root.is_dir():
        raise SystemExit(f"source directory does not exist: {source_root}")
    if not archive_root:
        raise SystemExit("archive root must not be empty")

    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        output_zip,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        add_directory(archive, source_root, archive_root)


if __name__ == "__main__":
    main()
