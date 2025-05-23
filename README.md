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
🔹 [Download for Linux](portable/Linux/UtillBuddy)
<!-- Other platform builds are planned and will be added here once available. -->
<!-- BUILDS END -->

---

## 🛠️ How to Build Locally

### Prerequisites
- Python 3.x installed on your system.
- Pip (Python package installer), usually included with Python.

### Steps
It's highly recommended to use a Python virtual environment to manage dependencies and avoid conflicts with other projects or your global Python installation.

```bash
# 1. Create and activate a virtual environment (optional but recommended)
# On macOS and Linux:
python3 -m venv venv
source venv/bin/activate
# On Windows:
python -m venv venv
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install PyInstaller (if not already included or for a specific version)
pip install pyinstaller

# 4. Run PyInstaller to build the executable
#    The output will be in a 'dist' folder.
pyinstaller --name UtillBuddy --onefile utill_buddy.py
```

---

## 🚀 Usage

After successfully building the application:

1.  Navigate to the `dist` folder created by PyInstaller (usually located in the project's root directory).
2.  Run the `UtillBuddy` executable:
    *   On **Linux**: `./UtillBuddy`
    *   On **Windows**: `UtillBuddy.exe`
    *   On **macOS**: Open `UtillBuddy.app` (Note: macOS builds typically require signing for distribution if built on macOS).

Utill Buddy will start, and an icon will appear in the system tray. Right-click the tray icon to access its features like mouse jiggling, clipboard utilities, and to customize shortcuts or exit the application.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve Utill Buddy or add new features:

1.  Fork the repository on GitHub.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with clear messages.
4.  Push your branch to your fork.
5.  Submit a pull request to the main Utill Buddy repository.

Alternatively, you can open an issue on GitHub to report bugs or suggest features.
