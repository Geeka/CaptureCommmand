"""
stitch.py
=========
Stitches page_XXXX.png screenshots into a single full_capture.png image.
Crops HEADER_ROWS from the top and BOTTOM_ROWS from the bottom of every page.
"""

import os
from PIL import Image

HEADER_ROWS = 60   # px to crop from top of every image before stitching
BOTTOM_ROWS = 40   # px to crop from bottom of every image before stitching


def stitch_folder(folder: str) -> str:
    """
    Read all page_XXXX.png files in folder, stitch into full_capture.png.
    Returns the path to full_capture.png.
    """
    png_files = sorted(
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().startswith("page_") and f.lower().endswith(".png")
    )

    if not png_files:
        print(f"[ERROR] No page_XXXX.png files found in: {folder}")
        return None

    print(f"\n{'='*56}")
    print(f"  Stitching {len(png_files)} page(s) ...")
    print(f"{'='*56}\n")

    images = []

    for i, path in enumerate(png_files):
        img = Image.open(path).convert("RGB")
        w, h = img.size
        cropped = img.crop((0, HEADER_ROWS, w, h - BOTTOM_ROWS))  # crop header and bottom
        images.append(cropped)
        img.close()
        print(f"  page {i+1:>3}: cropped top={HEADER_ROWS}px bottom={BOTTOM_ROWS}px  kept={h - HEADER_ROWS - BOTTOM_ROWS}px")

    total_width  = max(img.width  for img in images)
    total_height = sum(img.height for img in images)

    stitched = Image.new("RGB", (total_width, total_height))
    y_offset = 0
    for img in images:
        stitched.paste(img, (0, y_offset))
        y_offset += img.height

    out_path = os.path.join(folder, "full_capture.png")
    stitched.save(out_path)

    for img in images:
        img.close()

    print(f"\n[DONE] Stitched image saved: {out_path}")
    return out_path
