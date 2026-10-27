"""Render synthetic placeholder photos from data/photo_manifest.json.

Run from the repo root:  python scripts/make_placeholder_photos.py
Writes data/photos/<file>.jpg for every manifest entry. Each image carries the
part id, the shot number and the manifest's "shows" text, and is clearly
labelled SYNTHETIC so nobody mistakes it for a real part photo.
"""
import json
import os
import sys
import textwrap

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required: python -m pip install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "data", "photo_manifest.json")
OUT = os.path.join(ROOT, "data", "photos")
os.makedirs(OUT, exist_ok=True)

W, H = 800, 600
SHOT_COLOURS = {
    "1": (52, 73, 94),    # front
    "2": (84, 62, 90),    # back / mounting
    "3": (44, 90, 104),   # glass
    "4": (96, 76, 48),    # label
}


def font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


with open(MANIFEST, encoding="utf-8") as f:
    manifest = json.load(f)

big, mid, small = font(44), font(26), font(18)
for entry in manifest:
    fname = entry["file"]
    part_id, shot = fname.rsplit(".", 1)[0].rsplit("_", 1)
    bg = SHOT_COLOURS.get(shot, (70, 70, 70))
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    # mirror-ish silhouette so the thumbnails are distinguishable at a glance
    d.rounded_rectangle((250, 170, 560, 400), radius=60, outline=(230, 230, 230), width=4)
    d.ellipse((300, 210, 510, 360), outline=(230, 230, 230), width=3)
    d.rectangle((560, 260, 640, 310), outline=(230, 230, 230), width=3)
    if "crack" in entry["shows"] or "bent" in entry["shows"] or "chip" in entry["shows"]:
        d.line((430, 330, 470, 400), fill=(255, 120, 80), width=5)
        d.line((470, 400, 455, 430), fill=(255, 120, 80), width=5)

    d.text((30, 25), part_id, font=big, fill=(255, 255, 255))
    d.text((30, 80), f"photo {shot}", font=mid, fill=(220, 220, 220))
    y = 430
    for line in textwrap.wrap(entry["shows"], 60):
        d.text((30, y), line, font=mid, fill=(255, 255, 255))
        y += 34
    d.text((30, H - 35), "SYNTHETIC PLACEHOLDER - hackathon test data, not a real part photo",
           font=small, fill=(255, 210, 120))

    img.save(os.path.join(OUT, fname), "JPEG", quality=85)

print(f"wrote {len(manifest)} images to {OUT}")
