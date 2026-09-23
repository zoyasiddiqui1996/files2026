"""
DESKTOPHELP v3.0 — classifier.py
Core classification logic. Imported by desktophelp.py.

Stages:
  1. Scan Desktop root → sort images to 'my pictures', others to 'my files'
  2. Scan 'my pictures' root → classify any unclassified images already there
  3. For each image → detect faces → move to 'faces' or 'no faces'
  4. For each face image → read EXIF → move to 'faces/YYYY/' subfolder
"""

import sys
import shutil
from datetime import datetime
from pathlib import Path
from face_detector import has_face
from year_extractor import get_year

# Fix Windows terminal encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ── Config — works on ANY Windows/Mac/Linux user's machine ────────────────────
DESKTOP         = Path.home() / "Desktop"
PICTURES_FOLDER = DESKTOP / "my pictures"
FILES_FOLDER    = DESKTOP / "my files"
FACES_FOLDER    = PICTURES_FOLDER / "faces"
NO_FACES_FOLDER = PICTURES_FOLDER / "no faces"

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".webp", ".heic", ".ico", ".tiff",
    ".tif", ".raw", ".cr2", ".nef", ".arw",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def ensure_folders():
    """Create all target folders if they don't exist."""
    PICTURES_FOLDER.mkdir(exist_ok=True)
    FILES_FOLDER.mkdir(exist_ok=True)
    FACES_FOLDER.mkdir(exist_ok=True)
    NO_FACES_FOLDER.mkdir(exist_ok=True)


def safe_destination(target_dir: Path, filename: str) -> Path:
    """Return a unique destination path — never overwrites existing files."""
    dest = target_dir / filename
    if not dest.exists():
        return dest
    stem, suffix = Path(filename).stem, Path(filename).suffix
    timestamp = datetime.now().strftime("%H%M%S")
    return target_dir / f"{stem}_{timestamp}{suffix}"


def _year_sort(image_path: Path, year_summary: dict) -> Path:
    """
    Read EXIF year from image and move it into faces/YYYY/ subfolder.
    Returns the final destination path.
    """
    year = get_year(str(image_path))
    year_folder = FACES_FOLDER / year
    year_folder.mkdir(exist_ok=True)
    dest = safe_destination(year_folder, image_path.name)
    shutil.move(str(image_path), str(dest))
    year_summary[year] = year_summary.get(year, 0) + 1
    print(f"      📅  {year}  →  faces/{year}/")
    return dest


def _face_sort(item: Path, faces_detected: list, no_faces: list,
               skipped: list, year_summary: dict):
    """Run face detection on a single image, then year-sort if face found."""
    ext = item.suffix.lower()

    # SVG and GIF are not readable by OpenCV — send straight to no faces
    if ext in {".svg", ".gif"}:
        try:
            dest = safe_destination(NO_FACES_FOLDER, item.name)
            shutil.move(str(item), str(dest))
            no_faces.append(item.name)
            print(f"   🌄  {item.name}  →  no faces/  (format skipped face scan)")
        except PermissionError:
            skipped.append(f"[LOCKED]  {item.name}")
        return

    try:
        print(f"   🔍  Scanning {item.name} for faces...", end=" ", flush=True)
        face_found = has_face(str(item))

        if face_found:
            # First move to faces/ root temporarily, then year-sort
            temp_dest = safe_destination(FACES_FOLDER, item.name)
            shutil.move(str(item), str(temp_dest))
            faces_detected.append(item.name)
            print(f"🧑 face detected", end="  ", flush=True)
            _year_sort(temp_dest, year_summary)
        else:
            dest = safe_destination(NO_FACES_FOLDER, item.name)
            shutil.move(str(item), str(dest))
            no_faces.append(item.name)
            print(f"🌄 no face  →  no faces/")

    except PermissionError:
        skipped.append(f"[LOCKED]  {item.name}")
        print(f"   ⚠️  {item.name}  →  skipped (file is locked)")


def classify_existing_pictures(faces_detected: list, no_faces: list,
                               skipped: list, year_summary: dict):
    """
    Scan 'my pictures' root for unclassified images and run face + year detection.
    """
    if not PICTURES_FOLDER.exists():
        return

    unclassified = [
        item for item in PICTURES_FOLDER.iterdir()
        if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS | {".svg", ".gif"}
    ]

    if not unclassified:
        return

    print(f"\n📂 Found {len(unclassified)} unclassified image(s) in 'my pictures' — scanning...\n")
    for item in unclassified:
        _face_sort(item, faces_detected, no_faces, skipped, year_summary)


def classify_existing_faces(faces_detected: list, skipped: list, year_summary: dict):
    """
    Scan 'faces/' root for images not yet sorted into year subfolders.
    Runs EXIF year extraction on each and moves them into faces/YYYY/.
    """
    if not FACES_FOLDER.exists():
        return

    unclassified = [
        item for item in FACES_FOLDER.iterdir()
        if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS | {".svg", ".gif"}
    ]

    if not unclassified:
        return

    print(f"\n📅 Found {len(unclassified)} photo(s) in 'faces/' not yet sorted by year — classifying...\n")
    for item in unclassified:
        try:
            print(f"   📷  {item.name}", end="  ", flush=True)
            _year_sort(item, year_summary)
            faces_detected.append(item.name)
        except PermissionError:
            skipped.append(f"[LOCKED]  {item.name}")
            print(f"   ⚠️  {item.name}  →  skipped (file is locked)")


def classify_and_move():
    """
    Stage 1: Scan Desktop root → move images to 'my pictures', others to 'my files'.
    Stage 2: Scan 'my pictures' root → classify any images already there.
    Stage 3: For each image → detect faces → year-sort into 'faces/YYYY/'.
    Stage 4: Scan 'faces/' root → year-sort any previously detected but unsorted photos.

    Returns:
        faces_detected  — list of image filenames with faces
        no_faces        — list of image filenames without faces
        moved_files     — list of non-image filenames moved to 'my files'
        skipped         — list of skipped items (dirs, locked files)
        year_summary    — dict of {year: count} for face photos
    """
    faces_detected = []
    no_faces       = []
    moved_files    = []
    skipped        = []
    year_summary   = {}

    # ── Stage 1: Scan Desktop root ────────────────────────────────────────────
    for item in DESKTOP.iterdir():
        if item.is_dir():
            skipped.append(f"[DIR]  {item.name}")
            continue

        ext = item.suffix.lower()

        try:
            if ext in IMAGE_EXTENSIONS | {".svg", ".gif"}:
                temp_dest = safe_destination(PICTURES_FOLDER, item.name)
                shutil.move(str(item), str(temp_dest))
                _face_sort(temp_dest, faces_detected, no_faces, skipped, year_summary)
            else:
                dest = safe_destination(FILES_FOLDER, item.name)
                shutil.move(str(item), str(dest))
                moved_files.append(item.name)
                print(f"   📄  {item.name}  →  my files/")

        except PermissionError:
            skipped.append(f"[LOCKED]  {item.name}")
            print(f"   ⚠️  {item.name}  →  skipped (file is locked)")

    # ── Stage 2: Classify images already in 'my pictures' root ───────────────
    classify_existing_pictures(faces_detected, no_faces, skipped, year_summary)

    # ── Stage 3: Year-sort photos already in 'faces/' root ────────────────────
    classify_existing_faces(faces_detected, skipped, year_summary)

    return faces_detected, no_faces, moved_files, skipped, year_summary
