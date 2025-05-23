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

# MouseJiggler class definition
class MouseJiggler:
    """
    Manages the mouse jiggling functionality to prevent system sleep.
    Runs the jiggling in a separate thread.
    """
    def __init__(self, interval=60):
        """
        Initializes the MouseJiggler.

        Args:
            interval (int): The interval in seconds between jiggle actions.
        """
        self.interval = interval
        self.jiggle_event = threading.Event()  # Event to signal whether to jiggle
        self.stop_event = threading.Event()    # Event to signal the jiggle loop to stop
        self.thread = None                     # Holds the jiggle thread
        self._jiggle_on_start = False          # Internal flag to control initial jiggle state

    def _move_mouse(self):
        """Performs a small mouse movement."""
        try:
            x, y = pyautogui.position()
            pyautogui.moveTo(x + 1, y)
            pyautogui.moveTo(x, y)
        except Exception as e:
            # Log error if pyautogui fails (e.g., no display, permissions)
            print(f"Error moving mouse: {e}")

    def _jiggle_loop(self):
        """The main loop for the mouse jiggling thread."""
        if self._jiggle_on_start:  # Set event if jiggling should start immediately
            self.jiggle_event.set()
            self._jiggle_on_start = False  # Reset flag

        while not self.stop_event.is_set():
            if self.jiggle_event.is_set():
                self._move_mouse()
            
            # Sleep in 1-second intervals check stop_event more frequently
            # to make stopping more responsive.
            for _ in range(self.interval):
                if self.stop_event.is_set():
                    break
                time.sleep(1)

    def start(self, jiggle_on_start=True):
        """
        Starts the mouse jiggling thread and enables jiggling.

        If the thread is already running, it just ensures the jiggle event is set.
        Args:
            jiggle_on_start (bool): If True, starts jiggling immediately. 
                                    If False, thread starts but waits for jiggle_event.
        """
        self.jiggle_event.set()  # Ensure jiggling is active
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()  # Clear stop event before starting a new thread
            self._jiggle_on_start = jiggle_on_start
            self.thread = threading.Thread(target=self._jiggle_loop, daemon=True)
            self.thread.start()

    def pause(self):
        """Pauses the mouse jiggling by clearing the jiggle event."""
        self.jiggle_event.clear()

    def stop(self):
        """Stops the mouse jiggling thread gracefully."""
        self.jiggle_event.clear()  # Ensure no more jiggling
        self.stop_event.set()      # Signal the thread to terminate
        if self.thread and self.thread.is_alive():
            # Wait for the thread to finish, with a timeout
            self.thread.join(timeout=self.interval + 2) 
        self.thread = None


# ShortcutManager class definition
class ShortcutManager:
    """
    Manages application-level keyboard shortcuts using QShortcut.
    Note: QShortcut provides shortcuts that are active when the application
    has focus (or one of its windows/dialogs). It does not provide true
    system-wide global hotkeys (i.e., shortcuts that work when another
    application is focused). For system-wide hotkeys, a different library
    (e.g., pynput, keyboard) and platform-specific integration would be needed.
    """
    def __init__(self, app_instance, action_handlers):
        """
        Initializes the ShortcutManager.

        Args:
            app_instance (QApplication): The main application instance, used as parent for QShortcut.
            action_handlers (dict): A dictionary mapping action names (str) to callable handlers.
                                    Example: {"copy": lambda: signals.copy.emit()}
        """
        self.app = app_instance
        self.action_handlers = action_handlers
        
        # Default shortcuts for common actions
        self.default_shortcuts = {
            "copy": "Meta+C" if platform.system() == "Darwin" else "Ctrl+C",  # Cmd+C or Ctrl+C
            "paste": "Meta+V" if platform.system() == "Darwin" else "Ctrl+V",
            "cut": "Meta+X" if platform.system() == "Darwin" else "Ctrl+X"
        }
        self.user_shortcuts = dict(self.default_shortcuts)  # User-configurable shortcuts
        self.shortcut_objects = {}  # Stores active QShortcut objects
        self._initialize_shortcuts()

    def _initialize_shortcuts(self):
        """
        Initializes QShortcut objects for all default or previously user-defined shortcuts.
        This method is called internally during __init__.
        """
        for action_name, sequence_str in self.user_shortcuts.items():
            if action_name in self.action_handlers:
                try:
                    q_sequence = QKeySequence(sequence_str)
                    if q_sequence.isEmpty():
                        # Log if a stored shortcut string is invalid (e.g., corrupted config in future)
                        print(f"Warning: Empty or invalid QKeySequence for action '{action_name}' with sequence '{sequence_str}' during init.")
                        continue 

                    # Create QShortcut with the QApplication instance as parent for application-wide scope
                    shortcut = QShortcut(q_sequence, self.app)
                    shortcut.activated.connect(self.action_handlers[action_name])
                    self.shortcut_objects[action_name] = shortcut
                except Exception as e:
                    print(f"Error creating shortcut for {action_name} ({sequence_str}) during init: {e}")

    def set_shortcut(self, action_name):
        """
        Allows the user to set a custom keyboard shortcut for a given action.
        Displays an input dialog for the user to enter the new shortcut sequence.

        Args:
            action_name (str): The name of the action for which to set the shortcut (e.g., "copy").
        """
        if action_name not in self.action_handlers:
            QMessageBox.warning(None, "Error", f"Action '{action_name}' not recognized for shortcut setting.")
            return

        current_shortcut_str = self.user_shortcuts.get(action_name, "")
        new_sequence_str, ok = QInputDialog.getText(
            None, 
            "Set Custom Shortcut",
            f"Enter shortcut for '{action_name.capitalize()}' (current: '{current_shortcut_str}'):\n"
            f"(e.g., Ctrl+Alt+C, or leave empty to disable)",
            text=current_shortcut_str
        )

        if ok: # User confirmed the dialog
            # Disconnect and remove old QShortcut object if it exists
            if action_name in self.shortcut_objects:
                self.shortcut_objects[action_name].activated.disconnect()
                # Setting an empty QKeySequence effectively disables the QShortcut.
                self.shortcut_objects[action_name].setKey(QKeySequence()) 
                del self.shortcut_objects[action_name]
            
            # Remove previous user preference for this action before trying to set a new one.
            self.user_shortcuts.pop(action_name, None)

            if not new_sequence_str:  # User entered an empty string, meaning "clear/disable shortcut"
                QMessageBox.information(None, "Shortcut Cleared", 
                                        f"Shortcut for '{action_name.capitalize()}' has been cleared.")
            else:
                # Try to create the QKeySequence from the user's input
                q_sequence = QKeySequence(new_sequence_str)

                # Check if the sequence is valid (non-empty QKeySequence from a non-empty string).
                if q_sequence.isEmpty(): 
                    QMessageBox.warning(None, "Invalid Shortcut", 
                                        f"The shortcut sequence '{new_sequence_str}' is invalid and was not set.\n"
                                        f"Examples: 'Ctrl+C', 'Ctrl+Shift+X', 'Alt+F1'.")
                else: # Valid sequence
                    try:
                        shortcut = QShortcut(q_sequence, self.app)
                        shortcut.activated.connect(self.action_handlers[action_name])
                        self.shortcut_objects[action_name] = shortcut
                        self.user_shortcuts[action_name] = new_sequence_str # Store the valid string
                        QMessageBox.information(None, "Shortcut Set", 
                                                f"Shortcut for '{action_name.capitalize()}' set to '{new_sequence_str}'.")
                    except Exception as e:
                        # This might catch rare errors during QShortcut creation
                        QMessageBox.warning(None, "Error Setting Shortcut", 
                                            f"Could not set shortcut '{new_sequence_str}': {e}")


def create_icon():
    """Creates a generic icon for the system tray."""
    img = Image.new("RGB", (64, 64), color=(50, 150, 250)) # Blueish background
    draw = ImageDraw.Draw(img)
    draw.rectangle((16, 16, 48, 48), fill="white")      # White square
    draw.text((22, 20), "UB", fill=(50, 150, 250))      # "UB" text
    return img

class ActionSignals(QObject):
    """
    Defines custom Qt signals for various application actions.
    This allows for decoupled communication between UI components (like tray menu)
    and action handlers or the ShortcutManager.
    """
    copy = pyqtSignal()            # Signal for copy text action
    paste = pyqtSignal()           # Signal for paste text action
    cut = pyqtSignal()             # Signal for cut text action
    copy_image = pyqtSignal()      # Signal for copy image action
    paste_image = pyqtSignal()     # Signal for paste image action
    custom_shortcut = pyqtSignal(str) # Signal to trigger setting a custom shortcut for an action (passes action name)

signals = ActionSignals() # Global instance of signals

# --- GUI Action Functions ---
# These functions perform the core operations and are connected to signals.

def copy_text():
    """Opens a dialog to get text from user and copies it to clipboard."""
    text, ok = QInputDialog.getText(None, "Copy Text", "Enter text to copy to clipboard:")
    if ok and text:
        QApplication.clipboard().setText(text)

def paste_text():
    """Retrieves text from clipboard and displays it in a message box."""
    text = QApplication.clipboard().text()
    QMessageBox.information(None, "Clipboard Text", f"Clipboard text:\n{text}")

def cut_text():
    """Retrieves text from clipboard, clears clipboard, and shows the cut text."""
    text = QApplication.clipboard().text()
    if text:
        QApplication.clipboard().setText("") # Clear clipboard
        QMessageBox.information(None, "Cut Text", f"Text removed from clipboard:\n{text}")
    else:
        QMessageBox.warning(None, "No Text", "No text in clipboard to cut.")

def copy_image():
    """Opens a file dialog to select an image and copies it to clipboard."""
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
    """Retrieves an image from clipboard and opens a dialog to save it."""
    image = QApplication.clipboard().image()
    if not image.isNull():
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save Image from Clipboard", "clipboard_image.png", "PNG Files (*.png)"
        )
        if file_path:
            try:
                image.save(file_path)
                QMessageBox.information(None, "Image Saved", f"Image saved as {file_path}")
            except IOError as e:
                QMessageBox.warning(None, "Save Error", f"Failed to save image due to an I/O error: {e}")
            except PermissionError as e:
                QMessageBox.warning(None, "Save Error", f"Failed to save image due to a permission error: {e}")
            except Exception as e:
                QMessageBox.warning(None, "Save Error", f"An unexpected error occurred while saving the image: {e}")
    else:
        QMessageBox.warning(None, "No Image", "No image in clipboard.")


def quit_app(icon, item, mouse_jiggler_instance):
    """
    Stops background tasks and quits the application.

    Args:
        icon: The pystray.Icon instance.
        item: The pystray.MenuItem instance that triggered this.
        mouse_jiggler_instance (MouseJiggler): Instance of the mouse jiggler to stop its thread.
    """
    if mouse_jiggler_instance:
        mouse_jiggler_instance.stop()
    icon.stop()  # Stop the system tray icon
    QApplication.quit() # Quit the Qt application


def start_tray(app):
    """
    Initializes and starts the system tray icon and its menu.

    Args:
        app (QApplication): The main application instance.
    """
    # Helper function to create menu item actions that emit a specific signal.
    # This avoids repetition and keeps menu item definitions cleaner.
    def trigger_signal_action(signal_to_emit):
        return lambda icon, item: signal_to_emit.emit()

    # Retrieve the MouseJiggler instance stored in the QApplication properties
    mouse_jiggler_instance = app.property("mouse_jiggler_ref")
    
    # Create the system tray icon and menu structure
    icon = Icon(
        APP_NAME,
        icon=create_icon(), # Dynamically generated icon
        menu=Menu(
            MenuItem("Start Mouse Jiggler", lambda i, j: mouse_jiggler_instance.start()),
            MenuItem("Pause Mouse Jiggler", lambda i, j: mouse_jiggler_instance.pause()),
            Menu.SEPARATOR,
            MenuItem("Copy Text", trigger_signal_action(signals.copy)),
            MenuItem("Paste Text", trigger_signal_action(signals.paste)),
            MenuItem("Cut Text", trigger_signal_action(signals.cut)),
            MenuItem("Copy Image", trigger_signal_action(signals.copy_image)),
            MenuItem("Paste Image", trigger_signal_action(signals.paste_image)),
            Menu.SEPARATOR,
            # Menu items for setting custom shortcuts emit the 'custom_shortcut' signal 
            # with the name of the action (e.g., "copy") as an argument.
            MenuItem("Set Custom Copy Shortcut", lambda i, j: signals.custom_shortcut.emit("copy")),
            MenuItem("Set Custom Paste Shortcut", lambda i, j: signals.custom_shortcut.emit("paste")),
            MenuItem("Set Custom Cut Shortcut", lambda i, j: signals.custom_shortcut.emit("cut")),
            MenuItem("Set Custom Copy Image Shortcut", lambda i, j: signals.custom_shortcut.emit("copy_image")),
            MenuItem("Set Custom Paste Image Shortcut", lambda i, j: signals.custom_shortcut.emit("paste_image")),
            Menu.SEPARATOR,
            # Ensure mouse jiggler is stopped when exiting through tray menu
            MenuItem("Exit", lambda icon, item: quit_app(icon, item, mouse_jiggler_instance))
        )
    )
    # Run the system tray icon in a separate thread to avoid blocking the main Qt event loop
    threading.Thread(target=icon.run, daemon=True).start()


def main():
    """
    Main function to set up and run the Utill Buddy application.
    """
    app = QApplication(sys.argv)

    # Define handlers for shortcut actions. These lambdas emit the corresponding
    # signal from the global 'signals' instance when a shortcut is triggered.
    shortcut_action_triggers = {
        "copy": lambda: signals.copy.emit(),
        "paste": lambda: signals.paste.emit(),
        "cut": lambda: signals.cut.emit(),
        "copy_image": lambda: signals.copy_image.emit(),
        "paste_image": lambda: signals.paste_image.emit(),
    }

    # Initialize MouseJiggler
    mouse_jiggler = MouseJiggler(interval=60) # Default jiggle interval 60 seconds
    # Store the instance as a property of the app for access in start_tray
    app.setProperty("mouse_jiggler_ref", mouse_jiggler)

    # Initialize ShortcutManager
    shortcut_manager = ShortcutManager(app_instance=app, action_handlers=shortcut_action_triggers)
    # Store for potential future access, though signals.custom_shortcut is the primary way to interact
    app.setProperty("shortcut_manager_ref", shortcut_manager) 

    # Connect signals from the global 'signals' instance to the actual functions that perform the work.
    # This creates a single point of connection for actions, whether triggered by tray menu or keyboard shortcuts.
    signals.copy.connect(copy_text)
    signals.paste.connect(paste_text)
    signals.cut.connect(cut_text)
    signals.copy_image.connect(copy_image)
    signals.paste_image.connect(paste_image)
    # Connect the signal for setting a custom shortcut to the ShortcutManager's method
    signals.custom_shortcut.connect(shortcut_manager.set_shortcut)

    # MouseJiggler manages its own thread. It's not started automatically here;
    # user can start it via the tray menu.
    # Example: To start jiggling immediately: mouse_jiggler.start()
    # Example: To start thread paused: mouse_jiggler.start(jiggle_on_start=False)

    # Use QTimer.singleShot to defer tray icon setup until Qt event loop is running.
    # This ensures QApplication is fully initialized.
    QTimer.singleShot(0, lambda: start_tray(app))
    
    # Initializing shortcuts is now handled within ShortcutManager's constructor.
    sys.exit(app.exec_()) # Start the Qt event loop

if __name__ == "__main__":
    main()
