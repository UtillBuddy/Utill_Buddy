#!/usr/bin/env python3
"""
Utill Buddy – background utility that lives in the system tray.
Features:
• Mouse-jiggler to keep the system awake.
• Clipboard helpers (copy/paste/cut text, copy/paste image).
• User-configurable application-level shortcuts.
Everything runs silently – no main window, only a tray icon.
"""

import sys
import threading
import time
import platform
import logging
import random
from typing import Dict, Callable, Optional
import pyautogui
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import (
    QApplication, QWidget, QFileDialog, QMessageBox, QInputDialog, QShortcut
)
from PyQt5.QtGui import QKeySequence, QImage
from PyQt5.QtCore import QTimer, Qt, QObject, pyqtSignal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

APP_NAME = "Utill Buddy"
DEFAULT_JIGGLE_INTERVAL = 60  # seconds
MAX_RETRIES = 3  # For clipboard operations

# ────────────────────────────────────────────────────────────────────
# Mouse-jiggler
# ────────────────────────────────────────────────────────────────────
class MouseJiggler:
    """Keeps the pointer moving so the system doesn't sleep/lock."""

    def __init__(self, interval: int = DEFAULT_JIGGLE_INTERVAL):
        self.interval = interval
        self.jiggle_event = threading.Event()
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self._start_jiggling_immediately = False
        self._screen_width, self._screen_height = pyautogui.size()

    def _get_random_offset(self) -> tuple[int, int]:
        """Generate small random movement within screen bounds."""
        x, y = pyautogui.position()
        new_x = max(0, min(x + random.randint(-5, 5), self._screen_width - 1)
        new_y = max(0, min(y + random.randint(-5, 5), self._screen_height - 1)
        return (new_x, new_y)

    def _move_mouse(self) -> None:
        """Move mouse in a small random pattern."""
        try:
            x, y = self._get_random_offset()
            pyautogui.moveTo(x, y, duration=0.1)
            time.sleep(0.1)
            pyautogui.moveTo(*self._get_random_offset(), duration=0.1)
        except pyautogui.FailSafeException as fse:
            logger.error(f"Mouse movement failed due to PyAutoGUI FailSafeException: {fse}")
        except Exception as exc:
            logger.error(f"Mouse movement failed due to an unexpected error: {type(exc).__name__} - {exc}")

    def _loop(self) -> None:
        """Main jiggling loop."""
        if self._start_jiggling_immediately:
            self.jiggle_event.set()
            self._start_jiggling_immediately = False

        while not self.stop_event.is_set():
            if self.jiggle_event.is_set():
                self._move_mouse()

            for _ in range(self.interval):
                if self.stop_event.is_set():
                    break
                time.sleep(1)

    def start(self, jiggle_on_start: bool = True) -> None:
        """Start the jiggler thread."""
        self.jiggle_event.set()
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self._start_jiggling_immediately = jiggle_on_start
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            logger.info("Mouse jiggler started")

    def pause(self) -> None:
        """Pause jiggling."""
        self.jiggle_event.clear()
        logger.info("Mouse jiggler paused")

    def is_running(self) -> bool:
        """Check if jiggler is active."""
        return self.jiggle_event.is_set()

    def stop(self) -> None:
        """Stop the jiggler completely."""
        self.jiggle_event.clear()
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=self.interval + 2)
        self.thread = None
        logger.info("Mouse jiggler stopped")


# ────────────────────────────────────────────────────────────────────
# Shortcut manager
# ────────────────────────────────────────────────────────────────────
class ShortcutManager:
    """Manages application-wide keyboard shortcuts."""

    def __init__(self, app: QApplication, handlers: Dict[str, Callable]):
        self.app = app
        self.handlers = handlers
        self.default_map = {
            "copy": "Meta+C" if platform.system() == "Darwin" else "Ctrl+C",
            "paste": "Meta+V" if platform.system() == "Darwin" else "Ctrl+V",
            "cut": "Meta+X" if platform.system() == "Darwin" else "Ctrl+X",
            "copy_image": "Meta+Shift+C" if platform.system() == "Darwin" else "Ctrl+Shift+C",
            "paste_image": "Meta+Shift+V" if platform.system() == "Darwin" else "Ctrl+Shift+V",
        }
        self.user_map: Dict[str, str] = dict(self.default_map)
        self.shortcuts: Dict[str, QShortcut] = {}

        # Invisible parent widget for shortcuts
        self.parent_widget = QWidget()
        self.parent_widget.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.parent_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.parent_widget.hide()

        self._create_all()

    def _create_all(self) -> None:
        """Create all shortcuts from current mapping."""
        for action, seq_str in self.user_map.items():
            self._register_shortcut(action, seq_str)

    def _register_shortcut(self, action: str, sequence_str: str) -> None:
        """Register a single shortcut."""
        if action not in self.handlers:
            logger.warning(f"No handler for action: {action}")
            return

        qseq = QKeySequence(sequence_str)
        if qseq.isEmpty():
            logger.error(f"Invalid sequence '{sequence_str}' for {action}")
            return

        try:
            # Corrected shortcut initialization
            shortcut = QShortcut(qseq, self.parent_widget, self.handlers[action])
            self.shortcuts[action] = shortcut
            logger.info(f"Registered shortcut: {action} -> {sequence_str}")
        except Exception as exc:
            logger.error(f"Failed to set shortcut {action}: {exc}")

    def set_shortcut(self, action: str) -> None:
        """Prompt user to set a new shortcut."""
        if action not in self.handlers:
            QMessageBox.warning(None, "Unknown action", f"Action '{action}' not found")
            return

        current = self.user_map.get(action, "")
        seq_str, ok = QInputDialog.getText(
            None, "Set Shortcut",
            f"Shortcut for '{action}' (e.g., Ctrl+Shift+X).\nCurrent: '{current}':",
            text=current
        )
        if not ok:
            return

        # Remove existing shortcut
        if action in self.shortcuts:
            self.shortcuts[action].setEnabled(False)
            del self.shortcuts[action]

        if not seq_str:
            self.user_map.pop(action, None)
            QMessageBox.information(None, "Shortcut cleared", f"'{action}' shortcut removed")
            return

        if QKeySequence(seq_str).isEmpty():
            QMessageBox.warning(None, "Invalid", f"'{seq_str}' is not a valid shortcut")
            return

        self._register_shortcut(action, seq_str)
        self.user_map[action] = seq_str
        QMessageBox.information(None, "Shortcut set", f"{action} → {seq_str}")


# ────────────────────────────────────────────────────────────────────
# Qt signals
# ────────────────────────────────────────────────────────────────────
class Signals(QObject):
    """Central signal hub for application events."""
    copy = pyqtSignal()
    paste = pyqtSignal()
    cut = pyqtSignal()
    copy_image = pyqtSignal()
    paste_image = pyqtSignal()
    custom_shortcut = pyqtSignal(str)


signals = Signals()

# ────────────────────────────────────────────────────────────────────
# Clipboard helpers
# ────────────────────────────────────────────────────────────────────
def _with_retry(func: Callable, *args, **kwargs) -> bool:
    """Helper to retry clipboard operations."""
    for attempt in range(MAX_RETRIES):
        try:
            func(*args, **kwargs)
            return True
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(0.1)
    return False

def copy_text() -> None:
    """Copy text to clipboard with user input."""
    text, ok = QInputDialog.getText(None, "Copy Text", "Enter text:")
    if ok and text:
        if _with_retry(QApplication.clipboard().setText, text):
            QMessageBox.information(None, "Copied", "Text copied to clipboard")
        else:
            QMessageBox.warning(None, "Error", "Failed to copy text")

def paste_text() -> None:
    """Paste text from clipboard."""
    text = QApplication.clipboard().text()
    if text:
        QMessageBox.information(None, "Clipboard Text", text)
    else:
        QMessageBox.warning(None, "Clipboard", "No text in clipboard")

def cut_text() -> None:
    """Cut text (clear clipboard then show message)."""
    text = QApplication.clipboard().text()  # Store text before clearing
    if text:
        if _with_retry(QApplication.clipboard().clear):
            QMessageBox.information(None, "Cut Text", f"Cut: {text}")
        else:
            QMessageBox.warning(None, "Error", "Failed to cut text. Clipboard could not be cleared.")
    else:
        QMessageBox.warning(None, "Clipboard", "No text to cut")

def copy_image() -> None:
    """Copy image to clipboard from file."""
    path, _ = QFileDialog.getOpenFileName(
        None, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
    )
    if path:
        img = QImage(path)
        if img.isNull():
            QMessageBox.warning(None, "Error", "Invalid image file")
        elif _with_retry(QApplication.clipboard().setImage, img):
            QMessageBox.information(None, "Copied", "Image copied to clipboard")
        else:
            QMessageBox.warning(None, "Error", "Failed to copy image")

def paste_image() -> None:
    """Paste image from clipboard to file."""
    img = QApplication.clipboard().image()
    if img.isNull():
        QMessageBox.warning(None, "Clipboard", "No image in clipboard")
        return

    path, _ = QFileDialog.getSaveFileName(
        None, "Save Image", "clipboard.png", "PNG Files (*.png)"
    )
    if path:
        if img.save(path):
            QMessageBox.information(None, "Saved", f"Image saved to {path}")
        else:
            QMessageBox.warning(None, "Error", "Failed to save image")


# ────────────────────────────────────────────────────────────────────
# System-tray helpers
# ────────────────────────────────────────────────────────────────────
def make_tray_icon() -> Image.Image:
    """Create the system tray icon image."""
    img = Image.new("RGBA", (64, 64), (50, 150, 250, 200))
    d = ImageDraw.Draw(img)
    d.ellipse((16, 16, 48, 48), fill="white")
    d.text((22, 20), "UB", fill=(50, 150, 250))
    return img

def quit_app(icon: Icon, jiggler: MouseJiggler) -> None:
    """Clean up before quitting."""
    icon.visible = False
    jiggler.stop()
    icon.stop()
    QApplication.quit()
    logger.info("Application exited cleanly")

def start_tray(app: QApplication) -> None:
    """Initialize and run the system tray icon."""
    jiggler: MouseJiggler = app.property("jiggler")

    def emit(signal):
        return lambda: signal.emit()

    def get_jiggler_menu_text() -> str:
        """Returns the dynamic text for the jiggler menu item."""
        return "✔ Jiggler: On" if jiggler.is_running() else "◼ Jiggler: Off"

    def toggle_jiggler():
        if jiggler.is_running():
            jiggler.pause()
        else:
            jiggler.start()
        # Update tray title (menu item text is now dynamic)
        tray.title = f"{APP_NAME} - Jiggler: {'On' if jiggler.is_running() else 'Off'}"
        # The menu item itself will call get_jiggler_menu_text to update.

    tray = Icon(
        APP_NAME,
        make_tray_icon(),
        title=f"{APP_NAME} - Jiggler: Off",  # Initial title
        menu=Menu(
            MenuItem(
                get_jiggler_menu_text,  # Use the function here
                toggle_jiggler,
                default=True
            ),
            Menu.SEPARATOR,
            MenuItem("📋 Copy Text", emit(signals.copy)),
            MenuItem("📋 Paste Text", emit(signals.paste)),
            MenuItem("✂ Cut Text", emit(signals.cut)),
            MenuItem("🖼 Copy Image", emit(signals.copy_image)),
            MenuItem("🖼 Paste Image", emit(signals.paste_image)),
            Menu.SEPARATOR,
            MenuItem("⚙ Shortcuts", None, 
                Menu(
                    MenuItem("Copy Text", lambda: signals.custom_shortcut.emit("copy")),
                    MenuItem("Paste Text", lambda: signals.custom_shortcut.emit("paste")),
                    MenuItem("Cut Text", lambda: signals.custom_shortcut.emit("cut")),
                    MenuItem("Copy Image", lambda: signals.custom_shortcut.emit("copy_image")),
                    MenuItem("Paste Image", lambda: signals.custom_shortcut.emit("paste_image")),
                )
            ),
            Menu.SEPARATOR,
            MenuItem("❌ Exit", lambda: quit_app(tray, jiggler)),
        ),
    )

    def run_tray():
        try:
            tray.run()
        except Exception as e:
            logger.error(f"Tray icon failed: {e}")
            QTimer.singleShot(0, QApplication.quit)

    threading.Thread(target=run_tray, daemon=True).start()


# ────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────
def main() -> None:
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)

    # Initialize components
    jiggler = MouseJiggler()
    app.setProperty("jiggler", jiggler)

    # Connect signals
    signals.copy.connect(copy_text)
    signals.paste.connect(paste_text)
    signals.cut.connect(cut_text)
    signals.copy_image.connect(copy_image)
    signals.paste_image.connect(paste_image)

    # Shortcut manager
    handlers = {
        "copy": signals.copy.emit,
        "paste": signals.paste.emit,
        "cut": signals.cut.emit,
        "copy_image": signals.copy_image.emit,
        "paste_image": signals.paste_image.emit,
    }
    shortcut_mgr = ShortcutManager(app, handlers)
    app.setProperty("shortcut_manager", shortcut_mgr)
    signals.custom_shortcut.connect(lambda action: app.property("shortcut_manager").set_shortcut(action))

    # Start tray icon
    QTimer.singleShot(0, lambda: start_tray(app))

    logger.info("Application started")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
