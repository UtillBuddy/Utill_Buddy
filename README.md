# Utill_Buddy

# 🧰 Utill Buddy

**Utill Buddy** is a lightweight cross-platform desktop utility tool designed to improve your productivity by offering features like:

- ✍️ Clipboard text and image copy/paste
- ✂️ Quick cut with shortcut keys
- 🖱️ Background mouse jiggler to prevent system sleep
- 🎯 Customizable keyboard shortcuts
- 🖼️ Image clipboard handling
- 🪟 System tray app with native look and feel

---

## 🚀 Features

- System tray integration (Windows, macOS, Linux)
- Portable – no installation required
- PyQt5 GUI with PyStray and PyAutoGUI support
- Runs silently in the background
- Build automation using GitHub Actions

---

## 📥 Downloads

<!-- BUILDS START -->
<<<<<<< Updated upstream
🔹 [Download for Linux](portable/Linux/UtillBuddy)
=======
🔹 [Download for Windows](portable/Windows/UtillBuddy.exe)
>>>>>>> Stashed changes
<!-- BUILDS END -->

---

## 🛠️ How to Build Locally

```bash
pip install -r requirements.txt
pyinstaller --name UtillBuddy --onefile main.py
