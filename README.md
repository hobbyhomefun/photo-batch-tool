# Product Photo Batch Tool

Normalize a folder of raw supplier photos into store-ready JPEGs in one pass: trim baked-in white borders, fit everything inside a consistent box, convert formats, and get a dimension report for every file.

## Why this exists

Supplier photos arrive in every size, wrapped in uneven white padding, sometimes as PNGs the size of a billboard. A store needs them uniform. Doing it by hand for 100+ products is an evening gone; this is the batch step from a real store's photo workflow (the same shop also enforces ~720p-or-better product photos — the dimension report is how you spot the ones that fall short).

## The white-border rule (read this before trimming)

There are two kinds of "white around the product," and they are **not** the same:

- **A white border** — padding added around a photo. It looks sloppy in a catalog. **Trim it.**
- **A white background** — the photo was shot on white; the white *is* the picture. **Never trim it** — you'd crop the photo down to the product's silhouette and destroy the framing.

The tool trims by default, and `--keep-white-bg` turns trimming off. Sorting which images get which treatment is a human glance per folder — the tool can't tell padding from a studio background, and the self-test below shows exactly why it matters.

## Usage

```bash
pip install pillow

python3 photo_batch.py ./raw-photos --out ./store-ready
python3 photo_batch.py ./raw-photos --out ./store-ready --box 1000x1500
python3 photo_batch.py ./white-bg-shots --out ./store-ready --keep-white-bg
```

Options: `--box WxH` (default `1200x1200`, aspect always preserved) · `--keep-white-bg` (skip trim) · `--allow-upscale` (off by default — enlarging a small photo makes it blurry, not better) · `--quality N` (JPEG quality, default 88).

## Self-test output (real run)

Three test images: a photo with a baked-in white border (800×600, product is the middle 400×300), a small borderless photo, and a white-background shot (600×600, product centered).

```
$ python3 photo_batch.py ./test --out ./out
bordered.png: 800x600 -> trimmed 400x300 -> final 400x300  =>  bordered.jpg
small.jpg:    300x200 -> trimmed 300x200 -> final 300x200  =>  small.jpg
whitebg.png:  600x600 -> trimmed 100x100 -> final 100x100  =>  whitebg.jpg
```

Border trimmed perfectly, small photo left alone (no upscale) — and look at the third line: trimming cropped the white-background shot down to the product alone. Technically correct, photographically wrong. Now with the flag:

```
$ python3 photo_batch.py ./test/whitebg.png --out ./out2 --keep-white-bg
whitebg.png: 600x600 -> trimmed 600x600 -> final 600x600  =>  whitebg.jpg
```

Full frame preserved. That one flag is the whole lesson of the tool.

## License

MIT.
