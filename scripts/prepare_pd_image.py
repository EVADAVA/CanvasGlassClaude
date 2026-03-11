#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import io
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps


TARGET_BYTES_DEFAULT = 12 * 1024 * 1024
HARD_MAX_BYTES_DEFAULT = 20 * 1024 * 1024
MAX_SIDE_STEPS = [4096, 3600, 3200, 2800, 2400, 2048, 1800, 1600, 1400, 1200]
QUALITY_STEPS = [85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a painting image for PD Agent review as a compressed base64 JPEG."
    )
    parser.add_argument("input", type=Path, help="Source painting image")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output JPEG path (default: <input>.pd.jpg next to the source file)",
    )
    parser.add_argument(
        "--base64-out",
        type=Path,
        help="Optional file path for the base64-encoded JPEG payload",
    )
    parser.add_argument(
        "--target-mb",
        type=float,
        default=12.0,
        help="Preferred maximum JPEG size in MB before base64 encoding (default: 12)",
    )
    parser.add_argument(
        "--hard-max-mb",
        type=float,
        default=20.0,
        help="Hard maximum JPEG size in MB before base64 encoding (default: 20)",
    )
    parser.add_argument(
        "--print-base64",
        action="store_true",
        help="Print the base64 payload to stdout after writing files",
    )
    return parser.parse_args()


def output_path_for(source: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    return source.with_name(f"{source.stem}.pd.jpg")


def save_jpeg(image: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
    return buf.getvalue()


def prepare_base_image(source: Path) -> Image.Image:
    image = Image.open(source)
    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    elif image.mode == "L":
        image = image.convert("RGB")
    return image


def resize_steps(image: Image.Image) -> Iterable[tuple[Image.Image, int]]:
    width, height = image.size
    original_max_side = max(width, height)
    seen: set[int] = set()

    for max_side in MAX_SIDE_STEPS:
        if max_side > original_max_side or max_side in seen:
            continue
        seen.add(max_side)
        if original_max_side == max_side:
            yield image, max_side
            continue
        resized = image.copy()
        resized.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        yield resized, max_side

    if original_max_side not in seen:
        yield image, original_max_side


def compress_image(source: Path, target_bytes: int, hard_max_bytes: int) -> tuple[bytes, int, int, tuple[int, int]]:
    image = prepare_base_image(source)
    best: tuple[bytes, int, int, tuple[int, int]] | None = None

    for resized, max_side in resize_steps(image):
        for quality in QUALITY_STEPS:
            jpeg = save_jpeg(resized, quality)
            candidate = (jpeg, max_side, quality, resized.size)
            best = candidate
            if len(jpeg) <= target_bytes:
                return candidate

    if best is None:
        raise RuntimeError("Failed to produce a JPEG candidate")

    jpeg, max_side, quality, size = best
    if len(jpeg) > hard_max_bytes:
        raise RuntimeError(
            f"Could not compress below the hard limit of {hard_max_bytes / (1024 * 1024):.1f} MB"
        )
    return jpeg, max_side, quality, size


def main() -> int:
    args = parse_args()
    source = args.input.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"Input file not found: {source}")

    target_bytes = int(args.target_mb * 1024 * 1024)
    hard_max_bytes = int(args.hard_max_mb * 1024 * 1024)
    if target_bytes > hard_max_bytes:
        raise SystemExit("--target-mb cannot be larger than --hard-max-mb")

    output_path = output_path_for(source, args.output.expanduser().resolve() if args.output else None)
    jpeg, max_side, quality, final_size = compress_image(source, target_bytes, hard_max_bytes)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(jpeg)

    payload = base64.b64encode(jpeg).decode("ascii")
    if args.base64_out:
        base64_path = args.base64_out.expanduser().resolve()
        base64_path.parent.mkdir(parents=True, exist_ok=True)
        base64_path.write_text(payload)

    print(f"Input: {source}")
    print(f"Output JPEG: {output_path}")
    print(f"Output size: {len(jpeg) / (1024 * 1024):.2f} MB")
    print(f"Resize max side: {max_side}px")
    print(f"Final dimensions: {final_size[0]}x{final_size[1]}")
    print(f"JPEG quality: {quality}")
    print(f"Base64 chars: {len(payload)}")
    print("Ready for PD Agent: yes")

    if args.base64_out:
        print(f"Base64 file: {args.base64_out.expanduser().resolve()}")

    if args.print_base64:
        print(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
