from pynput import keyboard
import pyperclip
import time
import threading

class ClipboardHandler:
    def __init__(self):
        self.keyboard_controller = keyboard.Controller()
        self.callbacks = []
        
    def register_callback(self, callback):
        """Register a callback for when text is copied"""
        self.callbacks.append(callback)
        
    def text_copied(self, text):
        """Call all registered callbacks with the copied text"""
        for callback in self.callbacks:
            callback(text)
            
    def get_highlighted_text(self):
        """Get highlighted text using keyboard shortcuts"""
        def _get_text():
            old_clipboard = pyperclip.paste()
            
            # Release alt key if it's pressed
            self.keyboard_controller.release(keyboard.Key.alt)
            
            # Copy the highlighted text
            self.keyboard_controller.press(keyboard.Key.ctrl)
            self.keyboard_controller.press('c')
            self.keyboard_controller.release('c')
            self.keyboard_controller.release(keyboard.Key.ctrl)
            
            # Wait for clipboard to update
            time.sleep(0.1)
            
            new_clipboard = pyperclip.paste()
            
            # Notify about the copied text
            self.text_copied(new_clipboard)
            
        # Run in a separate thread to not block the UI
        thread = threading.Thread(target=_get_text)
        thread.daemon = True
        thread.start()
        
    def copy_text(self, text):
        """Copy text to clipboard"""
        pyperclip.copy(text)
        
    def replace_text(self, text):
        """Replace currently selected text with new text"""
        self.copy_text(text)
        
        # Paste the text
        self.keyboard_controller.press(keyboard.Key.ctrl)
        self.keyboard_controller.press('v')
        self.keyboard_controller.release('v')
        self.keyboard_controller.release(keyboard.Key.ctrl)