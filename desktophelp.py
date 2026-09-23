"""
DESKTOPHELP v3.0 — desktophelp.py
Entry point. Run this file to launch the agent.

Usage:
    python desktophelp.py
"""

import sys
import io
from datetime import datetime
from pathlib import Path
from classifier import classify_and_move, ensure_folders

# Fix Windows terminal encoding so emoji and box characters display correctly
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ── Report config ─────────────────────────────────────────────────────────────
REPORT_DIR = Path(__file__).parent / "reports"

# ── Banner ────────────────────────────────────────────────────────────────────
BANNER = """
╔══════════════════════════════════════╗
║         DESKTOPHELP  v3.0            ║
║  Organized + Smart + Time-Aware. 📅  ║
╚══════════════════════════════════════╝
"""

# ── Report generator ──────────────────────────────────────────────────────────
def generate_report(faces_detected, no_faces, moved_files, skipped, year_summary) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    now       = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    filename  = now.strftime("report_%Y%m%d_%H%M%S.md")
    path      = REPORT_DIR / filename

    total_pictures = len(faces_detected) + len(no_faces)

    lines = [
        "# 🗂️ DESKTOPHELP — Run Report",
        "**Agent:** DESKTOPHELP v3.0",
        f"**Run at:** {timestamp}",
        "",
        "---",
        "",
        f"## 🖼️ Pictures processed  ({total_pictures} total)",
        "",
        f"### 🧑 With human or animal face  ({len(faces_detected)} files)",
    ]
    lines += [f"- {f}" for f in faces_detected] if faces_detected else ["- *(none)*"]

    # ── Year breakdown section ─────────────────────────────────────────────────
    if year_summary:
        lines += [
            "",
            f"### 📅 Faces sorted by year",
        ]
        for year in sorted(k for k in year_summary if k != "unknown year"):
            lines.append(f"- **{year}** → {year_summary[year]} photo(s)")
        if "unknown year" in year_summary:
            lines.append(f"- **unknown year** → {year_summary['unknown year']} photo(s)")

    lines += [
        "",
        f"### 🌄 No face detected  ({len(no_faces)} files)",
    ]
    lines += [f"- {f}" for f in no_faces] if no_faces else ["- *(none)*"]

    lines += [
        "",
        f"## 📄 Moved to `my files`  ({len(moved_files)} files)",
    ]
    lines += [f"- {f}" for f in moved_files] if moved_files else ["- *(none)*"]

    lines += [
        "",
        f"## ⏭️ Skipped  ({len(skipped)} items)",
    ]
    lines += [f"- {s}" for s in skipped] if skipped else ["- *(none)*"]

    lines += [
        "",
        "---",
        f"**Total files processed:** {total_pictures + len(moved_files)}",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(BANNER)
    print("🔍 Scanning Desktop and Pictures...\n")

    try:
        ensure_folders()
        faces_detected, no_faces, moved_files, skipped, year_summary = classify_and_move()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

    report_path = generate_report(faces_detected, no_faces, moved_files, skipped, year_summary)

    total_pictures = len(faces_detected) + len(no_faces)

    print()
    print("─" * 42)
    print(f"  ✅  DESKTOPHELP v3.0 finished!")
    print(f"  🧑   Faces detected : {len(faces_detected)}")
    if year_summary:
        for year in sorted(k for k in year_summary if k != "unknown year"):
            print(f"       📅 {year}  →  {year_summary[year]} photo(s)")
        if "unknown year" in year_summary:
            print(f"       ❓ unknown year  →  {year_summary['unknown year']} photo(s)")
    print(f"  🌄   No faces       : {len(no_faces)}")
    print(f"  📄   Files moved    : {len(moved_files)}")
    print(f"  ⏭️   Skipped        : {len(skipped)}")
    print(f"  📋   Report saved   : {report_path.name}")
    print("─" * 42)


if __name__ == "__main__":
    main()
