#!/usr/bin/env python3
"""
Utill Buddy – background utility that lives in the system tray.
Features:
• Mouse-jiggler to keep the system awake.
• Clipboard helpers (copy / paste / cut text, copy / paste image).
• User-configurable application-level shortcuts.
Everything runs silently – no main window, only a tray icon.
"""

import sys
import threading
import time
import platform
import pyautogui
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import (
    QApplication, QWidget, QFileDialog, QMessageBox, QInputDialog, QShortcut
)
from PyQt5.QtGui import QKeySequence, QImage
from PyQt5.QtCore import QTimer, Qt, QObject, pyqtSignal

APP_NAME = "Utill Buddy"


# ────────────────────────────────────────────────────────────────────
# Mouse-jiggler
# ────────────────────────────────────────────────────────────────────
class MouseJiggler:
    """Keeps the pointer moving so the system doesn’t sleep/lock."""

    def __init__(self, interval: int = 60):
        self.interval = interval
        self.jiggle_event = threading.Event()
        self.stop_event = threading.Event()
        self.thread = None
        self._start_jiggling_immediately = False

    # Internal helpers
    def _move_mouse(self) -> None:
        try:
            x, y = pyautogui.position()
            pyautogui.moveTo(x + 1, y)
            pyautogui.moveTo(x, y)
        except Exception as exc:
            print(f"[MouseJiggler] move failed: {exc}")

    def _loop(self) -> None:
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

    # Public API
    def start(self, jiggle_on_start: bool = True) -> None:
        self.jiggle_event.set()
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self._start_jiggling_immediately = jiggle_on_start
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()

    def pause(self) -> None:
        self.jiggle_event.clear()

    def is_running(self) -> bool:
        return self.jiggle_event.is_set()

    def stop(self) -> None:
        self.jiggle_event.clear()
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=self.interval + 2)
        self.thread = None


# ────────────────────────────────────────────────────────────────────
# Shortcut manager
# ────────────────────────────────────────────────────────────────────
class ShortcutManager:
    """
    Application-wide shortcuts (work while ANY Qt widget has focus).
    For true global hot-keys use a library like `keyboard` or `pynput`.
    """

    def __init__(self, app: QApplication, handlers: dict[str, callable]):
        self.app = app
        self.handlers = handlers

        self.default_map = {
            "copy":  "Meta+C" if platform.system() == "Darwin" else "Ctrl+C",
            "paste": "Meta+V" if platform.system() == "Darwin" else "Ctrl+V",
            "cut":   "Meta+X" if platform.system() == "Darwin" else "Ctrl+X",
        }
        self.user_map: dict[str, str] = dict(self.default_map)
        self.shortcuts: dict[str, QShortcut] = {}

        # Invisible parent widget keeps shortcuts alive but unseen
        self.parent_widget = QWidget()
        self.parent_widget.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.parent_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.parent_widget.hide()

        self._create_all()

    # ----------------------------------------------------------------
    def _create_all(self) -> None:
        """Create QShortcuts for the current mapping."""
        for action, seq_str in self.user_map.items():
            self._register_shortcut(action, seq_str)

    def _register_shortcut(self, action: str, sequence_str: str) -> None:
        if action not in self.handlers:
            return
        qseq = QKeySequence(sequence_str)
        if qseq.isEmpty():
            print(f"[ShortcutManager] Invalid sequence '{sequence_str}' for {action}")
            return
        try:
            shortcut = QShortcut(qseq, self.parent_widget)
            shortcut.activated.connect(self.handlers[action])
            self.shortcuts[action] = shortcut
        except Exception as exc:
            print(f"[ShortcutManager] Failed to set shortcut {action}: {exc}")

    # ----------------------------------------------------------------
    def set_shortcut(self, action: str) -> None:
        """Prompt user for a new shortcut."""
        if action not in self.handlers:
            QMessageBox.warning(None, "Unknown action", action)
            return

        current = self.user_map.get(action, "")
        seq_str, ok = QInputDialog.getText(
            None, "Set Shortcut",
            f"Shortcut for '{action}' (example: Ctrl+Shift+Alt+X).\n"
            f"Current = '{current}' (blank to clear):",
            text=current
        )
        if not ok:
            return

        # Remove existing shortcut
        if action in self.shortcuts:
            self.shortcuts[action].activated.disconnect()
            self.shortcuts[action].setKey(QKeySequence())
            del self.shortcuts[action]
        self.user_map.pop(action, None)

        if not seq_str:
            QMessageBox.information(None, "Shortcut cleared", f"'{action}' is now unset.")
            return

        if QKeySequence(seq_str).isEmpty():
            QMessageBox.warning(None, "Invalid", f"'{seq_str}' is not a valid shortcut.")
            return

        self._register_shortcut(action, seq_str)
        self.user_map[action] = seq_str
        QMessageBox.information(None, "Shortcut set", f"{action} → {seq_str}")


# ────────────────────────────────────────────────────────────────────
# Qt signals
# ────────────────────────────────────────────────────────────────────
class Signals(QObject):
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
def copy_text() -> None:
    text, ok = QInputDialog.getText(None, "Copy Text", "Enter text:")
    if ok and text:
        QApplication.clipboard().setText(text)


def paste_text() -> None:
    text = QApplication.clipboard().text()
    QMessageBox.information(None, "Clipboard Text", text or "<empty>")


def cut_text() -> None:
    text = QApplication.clipboard().text()
    if text:
        QApplication.clipboard().setText("")
        QMessageBox.information(None, "Cut Text", text)
    else:
        QMessageBox.warning(None, "Clipboard", "No text to cut.")


def copy_image() -> None:
    path, _ = QFileDialog.getOpenFileName(
        None, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
    )
    if path:
        img = QImage(path)
        if img.isNull():
            QMessageBox.warning(None, "Error", "Invalid image.")
        else:
            QApplication.clipboard().setImage(img)
            QMessageBox.information(None, "Image", "Image copied.")


def paste_image() -> None:
    img = QApplication.clipboard().image()
    if img.isNull():
        QMessageBox.warning(None, "Clipboard", "No image in clipboard.")
        return
    path, _ = QFileDialog.getSaveFileName(None, "Save Image", "clipboard.png", "PNG Files (*.png)")
    if path:
        if img.save(path):
            QMessageBox.information(None, "Saved", f"Image saved to {path}")
        else:
            QMessageBox.warning(None, "Save Failed", "Could not save image.")


# ────────────────────────────────────────────────────────────────────
# System-tray helpers
# ────────────────────────────────────────────────────────────────────
def make_tray_icon() -> Image.Image:
    img = Image.new("RGB", (64, 64), (50, 150, 250))
    d = ImageDraw.Draw(img)
    d.rectangle((16, 16, 48, 48), fill="white")
    d.text((22, 20), "UB", fill=(50, 150, 250))
    return img


def quit_app(icon: Icon, _item, jiggler: MouseJiggler) -> None:
    jiggler.stop()
    icon.stop()
    QApplication.quit()


def start_tray(app: QApplication) -> None:
    jiggler: MouseJiggler = app.property("jiggler")

    def emit(sig):
        return lambda _i, _j: sig.emit()

    def toggle_jiggler(start: bool):
        if start:
            jiggler.start()
        else:
            jiggler.pause()
        # Update tooltip so user sees state change immediately
        tray.title = f"{APP_NAME} – Jiggler: {'On' if jiggler.is_running() else 'Off'}"

    tray = Icon(
        APP_NAME,
        make_tray_icon(),
        title=f"{APP_NAME} – Jiggler: Off",
        menu=Menu(
            MenuItem(
                lambda item: "Pause Mouse Jiggler" if jiggler.is_running() else "Start Mouse Jiggler",
                lambda _icon, _item: toggle_jiggler(not jiggler.is_running()),
                default=True
            ),
            Menu.SEPARATOR,
            MenuItem("Copy Text", emit(signals.copy)),
            MenuItem("Paste Text", emit(signals.paste)),
            MenuItem("Cut Text", emit(signals.cut)),
            MenuItem("Copy Image", emit(signals.copy_image)),
            MenuItem("Paste Image", emit(signals.paste_image)),
            Menu.SEPARATOR,
            MenuItem("Set Copy Shortcut", lambda _i, _j: signals.custom_shortcut.emit("copy")),
            MenuItem("Set Paste Shortcut", lambda _i, _j: signals.custom_shortcut.emit("paste")),
            MenuItem("Set Cut Shortcut", lambda _i, _j: signals.custom_shortcut.emit("cut")),
            MenuItem("Set Copy Image Shortcut", lambda _i, _j: signals.custom_shortcut.emit("copy_image")),
            MenuItem("Set Paste Image Shortcut", lambda _i, _j: signals.custom_shortcut.emit("paste_image")),
            Menu.SEPARATOR,
            MenuItem("Exit", lambda i, item: quit_app(tray, item, jiggler)),
        ),
    )

    threading.Thread(target=tray.run, daemon=True).start()


# ────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────
def main() -> None:
    # Use pythonw / --noconsole exe to avoid a console window.
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # keep running with only tray icon

    # Mouse jiggler instance (not started automatically)
    jiggler = MouseJiggler(interval=60)
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
    signals.custom_shortcut.connect(shortcut_mgr.set_shortcut)

    # Start tray icon (deferred until event loop running)
    QTimer.singleShot(0, lambda: start_tray(app))

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
