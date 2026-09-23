import os
import shutil
from datetime import datetime
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────
DESKTOP = Path(r"C:\Users\zoya\Desktop")
PICTURES_FOLDER = DESKTOP / "my pictures"
FILES_FOLDER    = DESKTOP / "my files"
REPORT_FOLDER   = Path(r"C:\Users\zoya\.gemini\antigravity\scratch\desktop-classifier\reports")

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".webp", ".svg", ".heic", ".ico", ".tiff",
    ".tif", ".raw", ".cr2", ".nef", ".arw",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def ensure_dirs():
    PICTURES_FOLDER.mkdir(exist_ok=True)
    FILES_FOLDER.mkdir(exist_ok=True)
    REPORT_FOLDER.mkdir(parents=True, exist_ok=True)

def classify_and_move():
    moved_pictures = []
    moved_files    = []
    skipped        = []

    for item in DESKTOP.iterdir():
        # Skip the two managed folders and the report folder itself
        if item.is_dir():
            skipped.append(f"[FOLDER] {item.name}  ← skipped (directory)")
            continue

        ext = item.suffix.lower()

        if ext in IMAGE_EXTENSIONS:
            dest = PICTURES_FOLDER / item.name
            if dest.exists():
                dest = PICTURES_FOLDER / f"{item.stem}_{datetime.now().strftime('%H%M%S')}{item.suffix}"
            shutil.move(str(item), str(dest))
            moved_pictures.append(item.name)
        else:
            dest = FILES_FOLDER / item.name
            if dest.exists():
                dest = FILES_FOLDER / f"{item.stem}_{datetime.now().strftime('%H%M%S')}{item.suffix}"
            shutil.move(str(item), str(dest))
            moved_files.append(item.name)

    return moved_pictures, moved_files, skipped

def generate_report(moved_pictures, moved_files, skipped):
    now       = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    filename  = now.strftime("report_%Y%m%d_%H%M%S.md")
    report_path = REPORT_FOLDER / filename

    lines = [
        f"# 🗂️ Desktop Classification Report",
        f"**Run at:** {timestamp}",
        f"",
        f"---",
        f"",
        f"## 🖼️ Moved to `my pictures`  ({len(moved_pictures)} files)",
    ]
    if moved_pictures:
        for f in moved_pictures:
            lines.append(f"- {f}")
    else:
        lines.append("- *(none)*")

    lines += [
        f"",
        f"## 📄 Moved to `my files`  ({len(moved_files)} files)",
    ]
    if moved_files:
        for f in moved_files:
            lines.append(f"- {f}")
    else:
        lines.append("- *(none)*")

    lines += [
        f"",
        f"## ⏭️ Skipped  ({len(skipped)} items)",
    ]
    if skipped:
        for s in skipped:
            lines.append(f"- {s}")
    else:
        lines.append("- *(none)*")

    lines += [
        f"",
        f"---",
        f"**Total processed:** {len(moved_pictures) + len(moved_files)} files",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("🔍 Scanning Desktop...")
    ensure_dirs()
    moved_pictures, moved_files, skipped = classify_and_move()
    report_path = generate_report(moved_pictures, moved_files, skipped)

    print(f"✅ Done!")
    print(f"   🖼️  Pictures moved : {len(moved_pictures)}")
    print(f"   📄  Files moved    : {len(moved_files)}")
    print(f"   ⏭️  Skipped        : {len(skipped)}")
    print(f"   📋  Report saved to: {report_path}")

if __name__ == "__main__":
    main()
