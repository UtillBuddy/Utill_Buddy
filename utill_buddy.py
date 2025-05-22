import sys
import threading
import time
import pyautogui
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import (
    QApplication, QFileDialog, QMessageBox, QInputDialog, QShortcut
)
from PyQt5.QtGui import QKeySequence, QImage

APP_NAME = "Utill Buddy"
JIGGLE_INTERVAL = 60  # seconds

jiggle_event = threading.Event()
stop_event = threading.Event()

import platform
if platform.system() == "Darwin":
    default_shortcuts = {"copy": "Meta+C", "paste": "Meta+V", "cut": "Meta+X"}
else:
    default_shortcuts = {"copy": "Ctrl+C", "paste": "Ctrl+V", "cut": "Ctrl+X"}
user_shortcuts = dict(default_shortcuts)

def move_mouse():
    x, y = pyautogui.position()
    pyautogui.moveTo(x + 1, y)
    pyautogui.moveTo(x, y)

def jiggle_loop():
    while not stop_event.is_set():
        if jiggle_event.is_set():
            move_mouse()
        time.sleep(JIGGLE_INTERVAL)

def create_icon():
    img = Image.new("RGB", (64, 64), color=(50, 150, 250))
    draw = ImageDraw.Draw(img)
    draw.rectangle((16, 16, 48, 48), fill="white")
    draw.text((22, 20), "UB", fill=(50, 150, 250))
    return img

def start_jiggler(icon, item):
    jiggle_event.set()
    icon.title = f"{APP_NAME} - Jiggler: On"

def pause_jiggler(icon, item):
    jiggle_event.clear()
    icon.title = f"{APP_NAME} - Jiggler: Off"

def quit_app(icon, item):
    stop_event.set()
    icon.stop()
    QApplication.quit()
    sys.exit(0)

def copy_text(icon=None, item=None):
    app = QApplication.instance()
    text, ok = QInputDialog.getText(None, "Copy Text", "Enter text to copy to clipboard:")
    if ok and text:
        app.clipboard().setText(text)

def paste_text(icon=None, item=None):
    app = QApplication.instance()
    text = app.clipboard().text()
    QMessageBox.information(None, "Clipboard Text", f"Clipboard text:\n{text}")

def cut_text(icon=None, item=None):
    app = QApplication.instance()
    text = app.clipboard().text()
    if text:
        app.clipboard().setText("")
        QMessageBox.information(None, "Cut Text", f"Text removed from clipboard:\n{text}")
    else:
        QMessageBox.warning(None, "No Text", "No text in clipboard to cut.")

def copy_image(icon=None, item=None):
    app = QApplication.instance()
    file_path, _ = QFileDialog.getOpenFileName(
        None, "Select Image to Copy", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
    )
    if file_path:
        image = QImage(file_path)
        if not image.isNull():
            app.clipboard().setImage(image)
            QMessageBox.information(None, "Image Copied", "Image copied to clipboard.")
        else:
            QMessageBox.warning(None, "Error", "Failed to load image.")

def paste_image(icon=None, item=None):
    app = QApplication.instance()
    image = app.clipboard().image()
    if not image.isNull():
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save Image from Clipboard", "clipboard_image.png", "PNG Files (*.png)"
        )
        if file_path:
            image.save(file_path)
            QMessageBox.information(None, "Image Saved", f"Image saved as {file_path}")
    else:
        QMessageBox.warning(None, "No Image", "No image in clipboard.")

def set_custom_shortcut(action, app):
    seq, ok = QInputDialog.getText(
        None, "Custom Shortcut", f"Enter shortcut for {action.capitalize()} (e.g., Ctrl+Alt+C):"
    )
    if ok and seq:
        user_shortcuts[action] = seq
        QShortcut(QKeySequence(seq), app).activated.connect(action_map[action])

def init_shortcuts(app):
    for action, seq in user_shortcuts.items():
        shortcut = QShortcut(QKeySequence(seq), app)
        shortcut.activated.connect(action_map[action])

action_map = {
    "copy": copy_text,
    "paste": paste_text,
    "cut": cut_text,
}

def main():
    app = QApplication(sys.argv)
    init_shortcuts(app)
    icon = Icon(
        APP_NAME,
        icon=create_icon(),
        title=f"{APP_NAME} - Jiggler: Off",
        menu=Menu(
            MenuItem("Start Mouse Jiggler", start_jiggler),
            MenuItem("Pause Mouse Jiggler", pause_jiggler),
            Menu.SEPARATOR,
            MenuItem("Copy Text", copy_text),
            MenuItem("Paste Text", paste_text),
            MenuItem("Cut Text", cut_text),
            MenuItem("Copy Image", copy_image),
            MenuItem("Paste Image", paste_image),
            Menu.SEPARATOR,
            MenuItem("Set Custom Copy Shortcut", lambda icon, item: set_custom_shortcut("copy", app)),
            MenuItem("Set Custom Paste Shortcut", lambda icon, item: set_custom_shortcut("paste", app)),
            MenuItem("Set Custom Cut Shortcut", lambda icon, item: set_custom_shortcut("cut", app)),
            Menu.SEPARATOR,
            MenuItem("Exit", quit_app)
        )
    )
    threading.Thread(target=jiggle_loop, daemon=True).start()
    icon.run_detached()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
