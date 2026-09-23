# DESKTOPHELP v1.0

> Your Desktop, Organized.

DESKTOPHELP is a command-triggered agent that scans your Desktop, organizes files into two folders, and generates a report every time it runs.

---

## 📁 What it creates on your Desktop

| Folder | Contents |
|---|---|
| `my pictures` | All image files (`.jpg`, `.png`, `.gif`, `.webp`, `.heic`, `.svg`, etc.) |
| `my files` | All other files (`.pdf`, `.docx`, `.txt`, `.mp3`, `.zip`, `.exe`, etc.) |

---

## ▶️ How to run

Open PowerShell or Command Prompt and run:

```powershell
python "C:\Users\zoya\.gemini\antigravity\scratch\desktop-classifier\desktophelp.py"
```

That's it. DESKTOPHELP will:
1. Scan your Desktop
2. Create `my pictures` and `my files` if they don't exist
3. Move every file into the correct folder
4. Save a report in the `reports/` folder

---

## 📋 Reports

Every run generates a timestamped Markdown report:

```
desktop-classifier/
└── reports/
    ├── report_20260831_125300.md
    └── report_20260831_140000.md
```

Each report lists:
- Files moved to `my pictures`
- Files moved to `my files`
- Items skipped (folders, locked files)
- Total count

---

## 🛠️ Customize file types

To add or remove recognized image extensions, edit [`classifier.py`](classifier.py):

```python
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ...
    # add your extension here, e.g. ".psd"
}
```

---

## 📂 Project structure

```
desktop-classifier/
├── desktophelp.py   ← run this
├── classifier.py    ← core logic (edit to customize)
├── README.md        ← this file
└── reports/         ← auto-created, one report per run
```
