"""
DESKTOPHELP v3.0 — year_extractor.py
Reads EXIF metadata from an image to determine the year it was taken.
Imported by classifier.py.

Priority:
  1. EXIF DateTimeOriginal  — exact moment photo was clicked (camera/phone)
  2. EXIF DateTime          — fallback EXIF field
  3. File modification date — fallback for screenshots / no-EXIF images
  4. "unknown year"         — if everything fails
"""

from pathlib import Path
from datetime import datetime

UNKNOWN = "unknown year"

# EXIF tag IDs for date fields
EXIF_DATE_ORIGINAL = 36867   # DateTimeOriginal — when photo was taken
EXIF_DATE_DIGITIZED = 36868  # DateTimeDigitized
EXIF_DATE_MODIFIED  = 306    # DateTime — file change date in camera

def get_year(image_path: str) -> str:
    """
    Returns a 4-digit year string (e.g. '2024') for the given image.
    Falls back gracefully — never raises an exception.
    """
    path = Path(image_path)

    # ── Method 1: Read EXIF data with Pillow ──────────────────────────────────
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS

        with Image.open(str(path)) as img:
            exif_data = img._getexif()

        if exif_data:
            for tag_id in (EXIF_DATE_ORIGINAL, EXIF_DATE_DIGITIZED, EXIF_DATE_MODIFIED):
                raw = exif_data.get(tag_id)
                if raw:
                    # EXIF date format: "YYYY:MM:DD HH:MM:SS"
                    year_str = str(raw).split(":")[0].strip()
                    if year_str.isdigit() and len(year_str) == 4:
                        return year_str

    except Exception:
        pass  # Pillow can't read this file — try fallback

    # ── Method 2: File modification date as fallback ──────────────────────────
    try:
        mtime = path.stat().st_mtime
        year = datetime.fromtimestamp(mtime).year
        return str(year)
    except Exception:
        pass

    return UNKNOWN
