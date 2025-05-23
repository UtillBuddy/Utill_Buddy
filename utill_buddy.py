import sys
import threading
import time
import platform
import pyautogui
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import (
    QApplication, QFileDialog, QMessageBox, QInputDialog, QShortcut
)
from PyQt5.QtGui import QKeySequence, QImage
from PyQt5.QtCore import QTimer, Qt, QObject, pyqtSignal

APP_NAME = "Utill Buddy"
JIGGLE_INTERVAL = 60  # seconds

jiggle_event = threading.Event()
stop_event = threading.Event()

default_shortcuts = {
    "copy": "Meta+C" if platform.system() == "Darwin" else "Ctrl+C",
    "paste": "Meta+V" if platform.system() == "Darwin" else "Ctrl+V",
    "cut": "Meta+X" if platform.system() == "Darwin" else "Ctrl+X"
}
user_shortcuts = dict(default_shortcuts)
shortcut_objects = {}

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

class ActionSignals(QObject):
    copy = pyqtSignal()
    paste = pyqtSignal()
    cut = pyqtSignal()
    copy_image = pyqtSignal()
    paste_image = pyqtSignal()
    custom_shortcut = pyqtSignal(str)

signals = ActionSignals()

# GUI Action functions
def copy_text():
    text, ok = QInputDialog.getText(None, "Copy Text", "Enter text to copy to clipboard:")
    if ok and text:
        QApplication.clipboard().setText(text)

def paste_text():
    text = QApplication.clipboard().text()
    QMessageBox.information(None, "Clipboard Text", f"Clipboard text:\n{text}")

def cut_text():
    text = QApplication.clipboard().text()
    if text:
        QApplication.clipboard().setText("")
        QMessageBox.information(None, "Cut Text", f"Text removed from clipboard:\n{text}")
    else:
        QMessageBox.warning(None, "No Text", "No text in clipboard to cut.")

def copy_image():
    file_path, _ = QFileDialog.getOpenFileName(
        None, "Select Image to Copy", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
    )
    if file_path:
        image = QImage(file_path)
        if not image.isNull():
            QApplication.clipboard().setImage(image)
            QMessageBox.information(None, "Image Copied", "Image copied to clipboard.")
        else:
            QMessageBox.warning(None, "Error", "Failed to load image.")

def paste_image():
    image = QApplication.clipboard().image()
    if not image.isNull():
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save Image from Clipboard", "clipboard_image.png", "PNG Files (*.png)"
        )
        if file_path:
            image.save(file_path)
            QMessageBox.information(None, "Image Saved", f"Image saved as {file_path}")
    else:
        QMessageBox.warning(None, "No Image", "No image in clipboard.")

def set_custom_shortcut(action):
    seq, ok = QInputDialog.getText(
        None, "Custom Shortcut", f"Enter shortcut for {action.capitalize()} (e.g., Ctrl+Alt+C):"
    )
    if ok and seq:
        if action in shortcut_objects:
            shortcut_objects[action].disconnect()
        shortcut = QShortcut(QKeySequence(seq), QApplication.instance().activeWindow())
        shortcut.activated.connect(action_map[action])
        shortcut_objects[action] = shortcut
        user_shortcuts[action] = seq

def quit_app(icon, _):
    stop_event.set()
    icon.stop()
    QApplication.quit()

action_map = {
    "copy": copy_text,
    "paste": paste_text,
    "cut": cut_text
}

def init_shortcuts(app):
    for action, seq in user_shortcuts.items():
        shortcut = QShortcut(QKeySequence(seq), app.activeWindow())
        shortcut.activated.connect(action_map[action])
        shortcut_objects[action] = shortcut

def start_tray(app):
    def trigger(signal):
        return lambda icon, item: signal.emit()

    def trigger_custom(action):
        return lambda icon, item: signals.custom_shortcut.emit(action)

    icon = Icon(
        APP_NAME,
        icon=create_icon(),
        menu=Menu(
            MenuItem("Start Mouse Jiggler", lambda i, j: jiggle_event.set()),
            MenuItem("Pause Mouse Jiggler", lambda i, j: jiggle_event.clear()),
            Menu.SEPARATOR,
            MenuItem("Copy Text", trigger(signals.copy)),
            MenuItem("Paste Text", trigger(signals.paste)),
            MenuItem("Cut Text", trigger(signals.cut)),
            MenuItem("Copy Image", trigger(signals.copy_image)),
            MenuItem("Paste Image", trigger(signals.paste_image)),
            Menu.SEPARATOR,
            MenuItem("Set Custom Copy Shortcut", trigger_custom("copy")),
            MenuItem("Set Custom Paste Shortcut", trigger_custom("paste")),
            MenuItem("Set Custom Cut Shortcut", trigger_custom("cut")),
            Menu.SEPARATOR,
            MenuItem("Exit", quit_app)
        )
    )
    threading.Thread(target=icon.run, daemon=True).start()

def main():
    app = QApplication(sys.argv)

    # Connect signals to slots
    signals.copy.connect(copy_text)
    signals.paste.connect(paste_text)
    signals.cut.connect(cut_text)
    signals.copy_image.connect(copy_image)
    signals.paste_image.connect(paste_image)
    signals.custom_shortcut.connect(set_custom_shortcut)

    QTimer.singleShot(0, lambda: start_tray(app))
    threading.Thread(target=jiggle_loop, daemon=True).start()

    init_shortcuts(app)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
