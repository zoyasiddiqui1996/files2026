"""
DESKTOPHELP v2.0 — face_detector.py
AI module that detects human and animal faces inside images using OpenCV.
Imported by classifier.py.
"""

import cv2
from pathlib import Path

# ── Load OpenCV Haar Cascade classifiers ─────────────────────────────────────
# These are built into OpenCV — no download needed
_CASCADE_DIR = Path(cv2.data.haarcascades)

_CASCADES = {
    "human_face" : cv2.CascadeClassifier(str(_CASCADE_DIR / "haarcascade_frontalface_default.xml")),
    "human_face2": cv2.CascadeClassifier(str(_CASCADE_DIR / "haarcascade_profileface.xml")),
    "cat_face"   : cv2.CascadeClassifier(str(_CASCADE_DIR / "haarcascade_frontalcatface.xml")),
    "cat_face_ex": cv2.CascadeClassifier(str(_CASCADE_DIR / "haarcascade_frontalcatface_extended.xml")),
}

# ── Main detection function ───────────────────────────────────────────────────
def has_face(image_path: str) -> bool:
    """
    Returns True if a human or animal face is detected in the image.
    Returns False if no face found, or if the image cannot be read.
    """
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            # Unreadable or corrupt image
            return False

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        for name, cascade in _CASCADES.items():
            if cascade.empty():
                continue  # skip if cascade failed to load
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
            )
            if len(faces) > 0:
                return True

        return False

    except Exception:
        # Never crash the main agent due to a bad image
        return False
