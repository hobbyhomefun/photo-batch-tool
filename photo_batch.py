#!/usr/bin/env python3
"""Product Photo Batch Tool — normalize a folder of supplier photos for a store.

For every image in the input folder it:
  1. Trims a uniform white border (the padding suppliers bake into photos).
     Cropping a border OUT is different from cropping a photo whose
     background IS white — pass --keep-white-bg for those images and the
     trim step is skipped entirely; they stay full-frame.
  2. Fits the image inside a target box (default 1200x1200), preserving
     aspect ratio. Never upscales unless --allow-upscale is given.
  3. Converts to JPEG and writes to the output folder.
  4. Prints a per-file report: original -> trimmed -> final dimensions.

Requires Pillow (pip install pillow). Everything else is standard library.

Usage:
  python3 photo_batch.py ./raw-photos --out ./store-ready
  python3 photo_batch.py ./raw-photos --out ./store-ready --box 1000x1500
  python3 photo_batch.py ./one-photo.png --out ./store-ready --keep-white-bg
"""
import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: pip install pillow")

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def trim_white_border(img: Image.Image, tolerance: int = 12) -> Image.Image:
    """Crop away a near-white border. Returns the image unchanged if the
    whole frame is near-white (nothing to keep) or no border is found."""
    gray = img.convert("L")
    mask = gray.point(lambda p: 255 if p < 255 - tolerance else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return img
    if bbox == (0, 0, img.width, img.height):
        return img
    return img.crop(bbox)


def fit_box(img: Image.Image, box_w: int, box_h: int, allow_upscale: bool) -> Image.Image:
    scale = min(box_w / img.width, box_h / img.height)
    if scale >= 1 and not allow_upscale:
        return img
    new = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
    return img.resize(new, Image.LANCZOS)


def process(path: Path, out_dir: Path, box, keep_white_bg: bool,
            allow_upscale: bool, quality: int) -> str:
    with Image.open(path) as im:
        original = im.size
        img = im.convert("RGB")
        trimmed = img.size
        if not keep_white_bg:
            img = trim_white_border(img)
            trimmed = img.size
        img = fit_box(img, box[0], box[1], allow_upscale)
        out_path = out_dir / (path.stem + ".jpg")
        img.save(out_path, "JPEG", quality=quality)
        return (f"{path.name}: {original[0]}x{original[1]}"
                f" -> trimmed {trimmed[0]}x{trimmed[1]}"
                f" -> final {img.width}x{img.height}  =>  {out_path.name}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="Image file or folder of images")
    ap.add_argument("--out", required=True, help="Output folder (created if missing)")
    ap.add_argument("--box", default="1200x1200",
                    help="Target box WxH the image must fit inside (default 1200x1200)")
    ap.add_argument("--keep-white-bg", action="store_true",
                    help="Skip white-border trimming (use when the white IS the background)")
    ap.add_argument("--allow-upscale", action="store_true",
                    help="Allow enlarging images smaller than the box (default: never upscale)")
    ap.add_argument("--quality", type=int, default=88, help="JPEG quality (default 88)")
    args = ap.parse_args()

    try:
        box_w, box_h = (int(v) for v in args.box.lower().split("x"))
    except ValueError:
        ap.error("--box must look like 1200x1200")

    src = Path(args.input)
    files = ([src] if src.is_file()
             else sorted(p for p in src.iterdir() if p.suffix.lower() in EXTS))
    if not files:
        print(f"No images found at {src}")
        return 2

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for f in files:
        try:
            print(process(f, out_dir, (box_w, box_h), args.keep_white_bg,
                          args.allow_upscale, args.quality))
        except Exception as e:  # keep going through the batch
            failures += 1
            print(f"{f.name}: FAILED ({e})")
    print(f"\nDone: {len(files) - failures}/{len(files)} processed -> {out_dir}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
