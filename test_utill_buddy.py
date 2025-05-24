import unittest
import time
import threading
from unittest.mock import patch, Mock

from utill_buddy import MouseJiggler, DEFAULT_JIGGLE_INTERVAL

# Mock pyautogui methods used by MouseJiggler before it's even imported by tests
# This is to prevent actual mouse movements during tests.
# We create a mock object that can be used by @patch
mock_pyautogui = Mock()
mock_pyautogui.size.return_value = (1920, 1080) # Default screen size
mock_pyautogui.position.return_value = (0, 0) # Default mouse position
mock_pyautogui.moveTo.return_value = None

# Apply patch to the actual pyautogui if it's imported by utill_buddy
# This is a bit tricky as utill_buddy is imported by this test file.
# The ideal way is to ensure pyautogui is patched before MouseJiggler class uses it.
# For simplicity in this context, we might rely on @patch in test methods for specific tests,
# but a module-level patch is safer.
# However, direct module-level @patch like this for 'utill_buddy.pyautogui' can be tricky
# if utill_buddy.py itself is not structured to easily allow this for its own import of pyautogui.

# For tests that specifically check mouse movement, @patch('utill_buddy.pyautogui') at the method level is standard.

class TestMouseJiggler(unittest.TestCase):

    def setUp(self):
        """Initialize a MouseJiggler instance with a short interval for faster testing."""
        self.test_interval = 0.05  # Using a very small interval for tests
        # Patch pyautogui for the duration of each test method if not done globally
        self.pyautogui_patcher = patch('utill_buddy.pyautogui', new=mock_pyautogui)
        self.mock_pyautogui_instance = self.pyautogui_patcher.start()
        
        self.jiggler = MouseJiggler(interval=self.test_interval)
        # Ensure pyautogui methods used in __init__ are also properly mocked if any
        # MouseJiggler's __init__ calls pyautogui.size()
        self.mock_pyautogui_instance.size.return_value = (1920, 1080)
        self.mock_pyautogui_instance.position.return_value = (100,100)


    def tearDown(self):
        """Ensure the jiggler is stopped after each test."""
        if self.jiggler:
            self.jiggler.stop()
        # Stop the patcher
        self.pyautogui_patcher.stop()
        mock_pyautogui.reset_mock() # Reset call counts etc. for the global mock

    def test_jiggler_initialization(self):
        """Test that the jiggler initializes correctly."""
        self.assertFalse(self.jiggler.is_running(), "Jiggler should not be running initially.")
        self.assertEqual(self.jiggler.interval, self.test_interval)
        self.assertIsNone(self.jiggler.thread, "Jiggler thread should be None initially.")

    def test_jiggler_starts_and_stops(self):
        """Test starting and stopping the jiggler."""
        self.jiggler.start(jiggle_on_start=False) # Start paused initially for this test
        self.assertTrue(self.jiggler.jiggle_event.is_set(), "Jiggle event should be set on start.")
        # Jiggle_on_start=False means it starts but waits for interval, so is_running() might be tricky
        # Let's adjust the test logic slightly for clarity or start it fully.
        
        self.jiggler.stop() # Stop immediately for a clean state
        self.jiggler.start(jiggle_on_start=True) # Start and make it active
        self.assertTrue(self.jiggler.is_running(), "Jiggler should be running after start.")
        self.assertIsNotNone(self.jiggler.thread, "Jiggler thread should not be None after start.")
        self.assertTrue(self.jiggler.thread.is_alive(), "Jiggler thread should be alive after start.")

        self.jiggler.stop()
        self.assertFalse(self.jiggler.is_running(), "Jiggler should not be running after stop.")
        # The thread might take a moment to fully join and become None
        # Depending on implementation, thread might not be None immediately if join timeout is long
        # self.jiggler.thread.join() # Explicitly wait if needed, but stop() should handle it
        if self.jiggler.thread is not None: # Check if thread object still exists
             self.assertFalse(self.jiggler.thread.is_alive(), "Jiggler thread should not be alive after stop and join.")
        # A more robust check might be to wait for thread to be None or not alive
        # For this implementation, stop() sets self.thread to None after join.
        self.assertIsNone(self.jiggler.thread, "Jiggler thread should be None after stop.")


    def test_jiggler_pauses_and_resumes(self):
        """Test pausing and resuming the jiggler."""
        self.jiggler.start(jiggle_on_start=True)
        self.assertTrue(self.jiggler.is_running(), "Jiggler should be running after start.")

        self.jiggler.pause()
        self.assertFalse(self.jiggler.is_running(), "Jiggler should not be running after pause.")
        # Check if thread is still alive but just not jiggling
        self.assertIsNotNone(self.jiggler.thread, "Jiggler thread should still exist when paused.")
        self.assertTrue(self.jiggler.thread.is_alive(), "Jiggler thread should still be alive when paused.")

        self.jiggler.start() # This should resume it (or restart if it was fully stopped)
        self.assertTrue(self.jiggler.is_running(), "Jiggler should be running after resuming.")

    # Patch pyautogui for this specific test method
    # The mock_pyautogui instance created in setUp will be used
    def test_jiggler_moves_mouse_called(self):
        """Test that the jiggler calls pyautogui.moveTo."""
        # Ensure the mock is clean before this test
        self.mock_pyautogui_instance.moveTo.reset_mock()
        self.mock_pyautogui_instance.position.return_value = (100, 100) # Simulate mouse position

        self.jiggler.start(jiggle_on_start=True)
        self.assertTrue(self.jiggler.is_running(), "Jiggler should be running.")
        
        # Wait for a period to allow the jiggle loop to run a few times
        # Interval is short, so 2-3 cycles should be enough
        time.sleep(self.test_interval * 3) 

        self.mock_pyautogui_instance.moveTo.assert_called()
        # Check if called multiple times (at least twice for one jiggle operation)
        self.assertGreaterEqual(self.mock_pyautogui_instance.moveTo.call_count, 1, "moveTo should be called at least once.")
        
        # Verify that the coordinates are within expected small random offset if needed
        # For now, just checking if it's called is sufficient as per requirements

        self.jiggler.stop()

    def test_jiggler_loop_runs_and_stops(self):
        """Test the internal loop mechanism and stopping it."""
        # This test is more about the thread lifecycle and event handling
        self.jiggler.start(jiggle_on_start=True)
        self.assertTrue(self.jiggler.thread.is_alive())
        self.assertTrue(self.jiggler.jiggle_event.is_set())
        self.assertFalse(self.jiggler.stop_event.is_set())

        # Let it run for a tiny bit
        time.sleep(self.test_interval / 2)

        self.jiggler.stop()
        self.assertFalse(self.jiggler.jiggle_event.is_set())
        self.assertTrue(self.jiggler.stop_event.is_set())
        
        # Wait for thread to actually terminate. stop() calls join().
        # If thread is still not None, it means join might not have completed or logic is different.
        # Given current MouseJiggler.stop(), self.thread should be None.
        self.assertIsNone(self.jiggler.thread, "Thread should be None after stop().")


if __name__ == '__main__':
    unittest.main()


from PyQt5.QtWidgets import QApplication, QClipboard, QMessageBox, QInputDialog, QFileDialog
# QImage is imported in utill_buddy, so we will patch 'utill_buddy.QImage'
# from PyQt5.QtGui import QImage # Not directly used in test, but for type hinting if needed
from PyQt5.QtCore import pyqtSignal

from utill_buddy import (
    copy_text, paste_text, cut_text, copy_image, paste_image,
    Signals, _with_retry # _with_retry might be indirectly tested
)

# Keep the existing mock_pyautogui and TestMouseJiggler class as is.
# Add the new TestClipboardHelpers class below.

class TestClipboardHelpers(unittest.TestCase):
    app_instance = None # To hold QApplication instance

    @classmethod
    def setUpClass(cls):
        """Ensure a QApplication instance exists for clipboard operations."""
        if QApplication.instance() is None:
            cls.app_instance = QApplication([])
        else:
            cls.app_instance = QApplication.instance()

    @classmethod
    def tearDownClass(cls):
        """Clean up the QApplication instance if it was created by this class."""
        # This is tricky; typically, QApplication is meant to live for the app's lifetime.
        # For tests, if we created it, we might want to quit it.
        # However, other test classes might also need it.
        # For now, let's not QApplication.quit() here to avoid side effects on other tests.
        # If cls.app_instance was created by this class:
        # if hasattr(cls, '_created_qapp_instance') and cls._created_qapp_instance:
        #     QApplication.quit()
        pass


    def setUp(self):
        """Set up mocks for Qt classes and methods."""
        self.app = QApplication.instance() # Get the application instance

        # 1. Mock QApplication.clipboard()
        self.clipboard_patcher = patch('PyQt5.QtWidgets.QApplication.clipboard')
        self.mock_clipboard_method = self.clipboard_patcher.start()
        self.mock_clipboard_instance = Mock(spec=QClipboard) # This is what QApplication.clipboard() will return
        self.mock_clipboard_method.return_value = self.mock_clipboard_instance

        # 2. Mock QMessageBox methods
        self.msgbox_info_patcher = patch('PyQt5.QtWidgets.QMessageBox.information')
        self.mock_msgbox_info = self.msgbox_info_patcher.start()

        self.msgbox_warn_patcher = patch('PyQt5.QtWidgets.QMessageBox.warning')
        self.mock_msgbox_warn = self.msgbox_warn_patcher.start()

        # 3. Mock QInputDialog.getText
        self.input_dialog_patcher = patch('PyQt5.QtWidgets.QInputDialog.getText')
        self.mock_input_dialog_getText = self.input_dialog_patcher.start()

        # 4. Mock QFileDialog methods
        self.file_dialog_open_patcher = patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
        self.mock_file_dialog_getOpenFileName = self.file_dialog_open_patcher.start()

        self.file_dialog_save_patcher = patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
        self.mock_file_dialog_getSaveFileName = self.file_dialog_save_patcher.start()

        # 5. Mock QImage (constructor and instance methods)
        # Patch QImage where it's looked up by utill_buddy.py
        self.qimage_patcher = patch('utill_buddy.QImage')
        self.mock_qimage_constructor = self.qimage_patcher.start()
        
        # This mock_qimage_instance will be returned when `QImage()` is called in the code under test
        self.mock_qimage_instance = Mock() 
        self.mock_qimage_constructor.return_value = self.mock_qimage_instance


    def tearDown(self):
        """Stop all patchers."""
        self.clipboard_patcher.stop()
        self.msgbox_info_patcher.stop()
        self.msgbox_warn_patcher.stop()
        self.input_dialog_patcher.stop()
        self.file_dialog_open_patcher.stop()
        self.file_dialog_save_patcher.stop()
        self.qimage_patcher.stop()

    # --- Test Methods ---

    def test_copy_text_success(self):
        self.mock_input_dialog_getText.return_value = ("sample text", True)
        # self.mock_clipboard_instance.setText will be called by _with_retry
        # For _with_retry to succeed, the lambda func() passed to it should not raise error.
        # So, ensure setText itself (the mock) doesn't raise an error. Mocks don't by default.
        
        copy_text()

        self.mock_clipboard_instance.setText.assert_called_once_with("sample text")
        self.mock_msgbox_info.assert_called_once_with(None, "Copied", "Text copied to clipboard")

    def test_copy_text_cancel(self):
        self.mock_input_dialog_getText.return_value = ("sample text", False) # User cancelled
        
        copy_text()

        self.mock_clipboard_instance.setText.assert_not_called()
        self.mock_msgbox_info.assert_not_called() # No success message
        self.mock_msgbox_warn.assert_not_called() # No error message either for simple cancel

    def test_copy_text_no_text_input(self):
        self.mock_input_dialog_getText.return_value = ("", True) # User entered no text but pressed OK
        
        copy_text() # Should not copy empty string or show success

        self.mock_clipboard_instance.setText.assert_not_called() # Or called with "" then error? Let's check func logic.
                                                              # Current logic: if ok and text: ... setText
                                                              # So, if text is "", setText is not called.
        self.mock_msgbox_info.assert_not_called()


    def test_paste_text_with_text(self):
        self.mock_clipboard_instance.text.return_value = "pasted text"
        
        paste_text()
        
        self.mock_clipboard_instance.text.assert_called_once()
        self.mock_msgbox_info.assert_called_once_with(None, "Clipboard Text", "pasted text")

    def test_paste_text_no_text(self):
        self.mock_clipboard_instance.text.return_value = ""
        
        paste_text()
        
        self.mock_clipboard_instance.text.assert_called_once()
        self.mock_msgbox_warn.assert_called_once_with(None, "Clipboard", "No text in clipboard")

    def test_cut_text_success(self):
        self.mock_clipboard_instance.text.return_value = "text to cut"
        # self.mock_clipboard_instance.clear should not raise error for _with_retry
        
        cut_text()
        
        self.mock_clipboard_instance.text.assert_called_once() # To get the text
        self.mock_clipboard_instance.clear.assert_called_once() # To clear it
        self.mock_msgbox_info.assert_called_once_with(None, "Cut Text", "Cut: text to cut")

    def test_cut_text_no_text_to_cut(self):
        self.mock_clipboard_instance.text.return_value = "" # Clipboard is empty
        
        cut_text()
        
        self.mock_clipboard_instance.text.assert_called_once()
        self.mock_clipboard_instance.clear.assert_not_called()
        self.mock_msgbox_warn.assert_called_once_with(None, "Clipboard", "No text to cut")
        self.mock_msgbox_info.assert_not_called()


    def test_cut_text_clear_fails(self):
        self.mock_clipboard_instance.text.return_value = "text to cut"
        # Make the mocked clear method raise an error to test _with_retry failure
        self.mock_clipboard_instance.clear.side_effect = RuntimeError("Simulated clear error")
        
        cut_text()
        
        self.mock_clipboard_instance.text.assert_called_once()
        # clear() would be called MAX_RETRIES times by _with_retry
        self.assertEqual(self.mock_clipboard_instance.clear.call_count, 3) # DEFAULT_MAX_RETRIES = 3 in utill_buddy
        self.mock_msgbox_warn.assert_called_once_with(None, "Error", "Failed to cut text. Clipboard could not be cleared.")
        self.mock_msgbox_info.assert_not_called()

    def test_copy_image_success(self):
        self.mock_file_dialog_getOpenFileName.return_value = ("fake/path.png", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        self.mock_qimage_instance.isNull.return_value = False # QImage("fake/path.png") is valid
        # self.mock_clipboard_instance.setImage should not raise error for _with_retry
        
        copy_image()
        
        self.mock_file_dialog_getOpenFileName.assert_called_once()
        self.mock_qimage_constructor.assert_called_once_with("fake/path.png")
        self.mock_qimage_instance.isNull.assert_called_once()
        self.mock_clipboard_instance.setImage.assert_called_once_with(self.mock_qimage_instance)
        self.mock_msgbox_info.assert_called_once_with(None, "Copied", "Image copied to clipboard")

    def test_copy_image_no_path(self):
        self.mock_file_dialog_getOpenFileName.return_value = ("", None) # User cancelled dialog
        
        copy_image()
        
        self.mock_file_dialog_getOpenFileName.assert_called_once()
        self.mock_qimage_constructor.assert_not_called()
        self.mock_clipboard_instance.setImage.assert_not_called()
        self.mock_msgbox_info.assert_not_called()
        self.mock_msgbox_warn.assert_not_called()


    def test_copy_image_invalid_file(self):
        self.mock_file_dialog_getOpenFileName.return_value = ("fake/invalid.png", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        self.mock_qimage_instance.isNull.return_value = True # QImage("fake/invalid.png") is invalid
        
        copy_image()
        
        self.mock_qimage_constructor.assert_called_once_with("fake/invalid.png")
        self.mock_qimage_instance.isNull.assert_called_once()
        self.mock_clipboard_instance.setImage.assert_not_called()
        self.mock_msgbox_warn.assert_called_once_with(None, "Error", "Invalid image file")

    def test_copy_image_clipboard_setimage_fails(self):
        self.mock_file_dialog_getOpenFileName.return_value = ("fake/path.png", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        self.mock_qimage_instance.isNull.return_value = False
        self.mock_clipboard_instance.setImage.side_effect = RuntimeError("Simulated setImage error")

        copy_image()

        self.assertEqual(self.mock_clipboard_instance.setImage.call_count, 3) # MAX_RETRIES
        self.mock_msgbox_warn.assert_called_once_with(None, "Error", "Failed to copy image")


    def test_paste_image_success(self):
        # Mock the image returned by clipboard.image()
        mock_clipboard_image = Mock()
        mock_clipboard_image.isNull.return_value = False
        mock_clipboard_image.save.return_value = True # Simulate successful save
        self.mock_clipboard_instance.image.return_value = mock_clipboard_image
        
        self.mock_file_dialog_getSaveFileName.return_value = ("save/path.png", "PNG Files (*.png)")
        
        paste_image()
        
        self.mock_clipboard_instance.image.assert_called_once()
        mock_clipboard_image.isNull.assert_called_once()
        self.mock_file_dialog_getSaveFileName.assert_called_once()
        mock_clipboard_image.save.assert_called_once_with("save/path.png")
        self.mock_msgbox_info.assert_called_once_with(None, "Saved", "Image saved to save/path.png")

    def test_paste_image_clipboard_empty(self):
        mock_clipboard_image = Mock()
        mock_clipboard_image.isNull.return_value = True # Clipboard image is null
        self.mock_clipboard_instance.image.return_value = mock_clipboard_image
        
        paste_image()
        
        self.mock_clipboard_instance.image.assert_called_once()
        mock_clipboard_image.isNull.assert_called_once()
        self.mock_file_dialog_getSaveFileName.assert_not_called()
        self.mock_msgbox_warn.assert_called_once_with(None, "Clipboard", "No image in clipboard")

    def test_paste_image_save_dialog_cancel(self):
        mock_clipboard_image = Mock()
        mock_clipboard_image.isNull.return_value = False
        self.mock_clipboard_instance.image.return_value = mock_clipboard_image
        
        self.mock_file_dialog_getSaveFileName.return_value = ("", None) # User cancelled save dialog
        
        paste_image()
        
        self.mock_file_dialog_getSaveFileName.assert_called_once()
        mock_clipboard_image.save.assert_not_called()
        self.mock_msgbox_info.assert_not_called() # No success message
        self.mock_msgbox_warn.assert_not_called() # No error message either for cancel

    def test_paste_image_save_fails(self):
        mock_clipboard_image = Mock()
        mock_clipboard_image.isNull.return_value = False
        mock_clipboard_image.save.return_value = False # Simulate QImage.save() returning False
        self.mock_clipboard_instance.image.return_value = mock_clipboard_image
        
        self.mock_file_dialog_getSaveFileName.return_value = ("save/path.png", "PNG Files (*.png)")
        
        paste_image()
        
        mock_clipboard_image.save.assert_called_once_with("save/path.png")
        self.mock_msgbox_warn.assert_called_once_with(None, "Error", "Failed to save image")


from utill_buddy import ShortcutManager
from PyQt5.QtWidgets import QShortcut # QKeySequence is used by QShortcut
from PyQt5.QtGui import QKeySequence # For constructing QKeySequence objects in tests if needed
import logging # For asserting log messages

# TestShortcutManager
class TestShortcutManager(unittest.TestCase):
    app_instance = None

    @classmethod
    def setUpClass(cls):
        if QApplication.instance() is None:
            cls.app_instance = QApplication([])
        else:
            cls.app_instance = QApplication.instance()

    def setUp(self):
        self.app = QApplication.instance()
        self.mock_handlers = {
            "copy": Mock(name="copy_handler"),
            "paste": Mock(name="paste_handler"),
            "cut": Mock(name="cut_handler"),
            "copy_image": Mock(name="copy_image_handler"),
            "paste_image": Mock(name="paste_image_handler"),
        }

        # Patch QShortcut where it's used by ShortcutManager
        self.qshortcut_patcher = patch('utill_buddy.QShortcut', autospec=True)
        self.mock_qshortcut_class = self.qshortcut_patcher.start()

        # Store created QShortcut mock instances, keyed by action for easy access in tests
        self.created_shortcuts_mocks = {} 
        
        def mock_qshortcut_side_effect(key_sequence, parent_widget, handler_func):
            # Create a new mock for each QShortcut instance
            mock_instance = Mock(spec=QShortcut) # Mock for the QShortcut instance
            mock_instance.key_sequence = key_sequence # Store for verification
            mock_instance.handler_func = handler_func # Store for verification
            
            # Find action name by handler_func (this is a bit indirect)
            action_name = None
            for name, hnd in self.mock_handlers.items():
                if hnd == handler_func:
                    action_name = name
                    break
            if action_name:
                 # If a shortcut for this action already exists, store it to check setEnabled(False) later
                if action_name in self.manager.shortcuts and self.manager.shortcuts[action_name]:
                     # This assumes self.manager.shortcuts stores the *actual mock instances*
                     # which it will if QShortcut constructor returns our mock_instance
                    pass # Already handled by manager logic if it replaces existing
                self.created_shortcuts_mocks[action_name] = mock_instance
            
            # Ensure the mock_instance.activated.connect is a mock itself
            mock_instance.activated = Mock()
            mock_instance.activated.connect = Mock()
            mock_instance.setEnabled = Mock()
            return mock_instance

        self.mock_qshortcut_class.side_effect = mock_qshortcut_side_effect
        
        # Patch QInputDialog and QMessageBox (similar to TestClipboardHelpers)
        self.input_dialog_patcher = patch('PyQt5.QtWidgets.QInputDialog.getText')
        self.mock_input_dialog_getText = self.input_dialog_patcher.start()
        self.msgbox_info_patcher = patch('PyQt5.QtWidgets.QMessageBox.information')
        self.mock_msgbox_info = self.msgbox_info_patcher.start()
        self.msgbox_warn_patcher = patch('PyQt5.QtWidgets.QMessageBox.warning')
        self.mock_msgbox_warn = self.msgbox_warn_patcher.start()

        self.manager = ShortcutManager(self.app, self.mock_handlers)
        # After manager init, self.created_shortcuts_mocks should be populated via side_effect

    def tearDown(self):
        self.qshortcut_patcher.stop()
        self.input_dialog_patcher.stop()
        self.msgbox_info_patcher.stop()
        self.msgbox_warn_patcher.stop()
        self.created_shortcuts_mocks.clear()


    def test_initial_shortcuts_created(self):
        # ShortcutManager's __init__ calls _create_all, which calls _register_shortcut
        # self.mock_qshortcut_class should have been called for each default mapping
        
        default_map_size = len(self.manager.default_map)
        self.assertEqual(self.mock_qshortcut_class.call_count, default_map_size)

        for action, seq_str in self.manager.default_map.items():
            self.assertIn(action, self.created_shortcuts_mocks, f"Mock shortcut for {action} not created")
            mock_shortcut_instance = self.created_shortcuts_mocks[action]
            
            # Check key sequence (QKeySequence objects might need careful comparison)
            # self.assertEqual(mock_shortcut_instance.key_sequence.toString(), QKeySequence(seq_str).toString())
            # The mock_qshortcut_side_effect stores the QKeySequence object passed to it.
            # ShortcutManager creates QKeySequence(seq_str).
            self.assertIsInstance(mock_shortcut_instance.key_sequence, QKeySequence)
            self.assertEqual(mock_shortcut_instance.key_sequence.toString(), seq_str)

            # Check connection
            mock_shortcut_instance.activated.connect.assert_called_once_with(self.mock_handlers[action])
            self.assertEqual(mock_shortcut_instance.handler_func, self.mock_handlers[action])


    def test_set_shortcut_new_valid(self):
        action_to_set = "copy"
        new_sequence_str = "Ctrl+Shift+Y"
        self.mock_input_dialog_getText.return_value = (new_sequence_str, True)

        # Get the mock for the original "copy" shortcut, if it exists
        original_mock_shortcut = self.created_shortcuts_mocks.get(action_to_set)
        if not original_mock_shortcut: # Should exist from setup
             self.fail(f"Original shortcut for {action_to_set} was not created during setup.")

        self.manager.set_shortcut(action_to_set)

        self.mock_input_dialog_getText.assert_called_once()
        
        # Assert old shortcut was disabled
        original_mock_shortcut.setEnabled.assert_called_with(False)

        # Assert new shortcut was created and connected
        # The side_effect of mock_qshortcut_class should have stored the new mock
        self.assertIn(action_to_set, self.created_shortcuts_mocks)
        new_mock_shortcut = self.created_shortcuts_mocks[action_to_set]
        self.assertIsNot(new_mock_shortcut, original_mock_shortcut, "A new shortcut mock should have been created.")
        
        # Check call to QShortcut constructor (implicitly via number of calls and side_effect)
        # Total calls = initial defaults + 1 for this new one
        expected_calls = len(self.manager.default_map) + 1
        self.assertEqual(self.mock_qshortcut_class.call_count, expected_calls)
        
        # Check the properties of the new shortcut mock from its creation
        self.assertEqual(new_mock_shortcut.key_sequence.toString(), new_sequence_str)
        new_mock_shortcut.activated.connect.assert_called_once_with(self.mock_handlers[action_to_set])

        self.assertEqual(self.manager.user_map[action_to_set], new_sequence_str)
        self.mock_msgbox_info.assert_called_once()


    def test_set_shortcut_clear(self):
        action_to_clear = "paste"
        self.mock_input_dialog_getText.return_value = ("", True) # Empty string = clear

        original_mock_shortcut = self.created_shortcuts_mocks.get(action_to_clear)
        self.assertIsNotNone(original_mock_shortcut, "Original shortcut for paste should exist.")

        self.manager.set_shortcut(action_to_clear)

        original_mock_shortcut.setEnabled.assert_called_with(False)
        self.assertNotIn(action_to_clear, self.manager.user_map)
        self.mock_msgbox_info.assert_called_once_with(None, "Shortcut cleared", f"'{action_to_clear}' shortcut removed")
        # Ensure no new shortcut was created for this action
        self.assertNotIn(action_to_clear, self.manager.shortcuts)


    def test_set_shortcut_invalid_sequence(self):
        action_to_set = "copy"
        original_sequence = self.manager.user_map[action_to_set]
        self.mock_input_dialog_getText.return_value = ("Invalid!", True) # Invalid sequence

        original_mock_shortcut = self.created_shortcuts_mocks.get(action_to_set)
        self.assertIsNotNone(original_mock_shortcut)

        self.manager.set_shortcut(action_to_set)
        
        self.mock_msgbox_warn.assert_called_once_with(None, "Invalid", "'Invalid!' is not a valid shortcut")
        # Ensure original shortcut is still there and enabled (or not disabled)
        original_mock_shortcut.setEnabled.assert_not_called_with(False) # Should not be disabled
        self.assertEqual(self.manager.user_map[action_to_set], original_sequence)
        # Ensure no new shortcut was attempted to be created beyond initial ones
        self.assertEqual(self.mock_qshortcut_class.call_count, len(self.manager.default_map))


    def test_set_shortcut_unknown_action(self):
        self.manager.set_shortcut("unknown_action")
        self.mock_msgbox_warn.assert_called_once_with(None, "Unknown action", "Action 'unknown_action' not found")
        self.mock_input_dialog_getText.assert_not_called()


    def test_set_shortcut_dialog_cancel(self):
        action_to_set = "copy"
        original_sequence = self.manager.user_map[action_to_set]
        self.mock_input_dialog_getText.return_value = ("Ctrl+Shift+Y", False) # User cancelled

        self.manager.set_shortcut(action_to_set)

        self.mock_input_dialog_getText.assert_called_once()
        self.mock_msgbox_info.assert_not_called()
        self.mock_msgbox_warn.assert_not_called()
        self.assertEqual(self.manager.user_map[action_to_set], original_sequence)
        # No change to shortcuts, so call count remains initial
        self.assertEqual(self.mock_qshortcut_class.call_count, len(self.manager.default_map))


    def test_register_shortcut_invalid_handler(self):
        # This test is tricky because _register_shortcut is internal.
        # We can test its behavior by trying to set a shortcut for an action not in self.handlers
        # but present in user_map. The ShortcutManager's _create_all calls _register_shortcut.
        # Or, we can call _register_shortcut directly if needed, but it's better to test via public API if possible.
        
        # Let's directly call _register_shortcut for focused test
        action_name = "bad_action" # Not in self.mock_handlers
        sequence_str = "Ctrl+L"
        
        initial_qshortcut_call_count = self.mock_qshortcut_class.call_count

        # Use assertLogs to check for the warning
        with self.assertLogs('utill_buddy', level='WARNING') as cm:
            self.manager._register_shortcut(action_name, sequence_str)
        
        self.assertIn(f"No handler for action: {action_name}", cm.output[0])
        
        # Ensure no new QShortcut was created for "bad_action"
        self.assertEqual(self.mock_qshortcut_class.call_count, initial_qshortcut_call_count)
        self.assertNotIn(action_name, self.manager.shortcuts)

    def test_register_shortcut_invalid_qkeysequence(self):
        action_name = "copy" # Valid action
        invalid_sequence_str = "This Is Not A Valid Sequence At All" 
        
        initial_qshortcut_call_count = self.mock_qshortcut_class.call_count
        
        # Temporarily remove from manager.shortcuts to allow _register_shortcut to proceed further
        # This simulates trying to register a new shortcut with an invalid sequence string
        if action_name in self.manager.shortcuts:
            del self.manager.shortcuts[action_name]

        with self.assertLogs('utill_buddy', level='ERROR') as cm:
            self.manager._register_shortcut(action_name, invalid_sequence_str)
        
        self.assertIn(f"Invalid sequence '{invalid_sequence_str}' for {action_name}", cm.output[0])
        
        # Ensure no new QShortcut was created
        self.assertEqual(self.mock_qshortcut_class.call_count, initial_qshortcut_call_count)
        self.assertNotIn(action_name, self.manager.shortcuts)
