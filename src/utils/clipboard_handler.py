from pynput import keyboard
import pyperclip
import time
import threading
import logging

class ClipboardHandler:
    def __init__(self):
        logging.debug('ClipboardHandler.__init__ called')
        self.keyboard_controller = keyboard.Controller()
        self.callbacks = []
        logging.debug('ClipboardHandler.__init__ finished')
        
    def register_callback(self, callback):
        logging.debug('ClipboardHandler.register_callback called')
        """Register a callback for when text is copied"""
        self.callbacks.append(callback)
        logging.debug('ClipboardHandler.register_callback finished')
        
    def text_copied(self, text):
        logging.debug(f'ClipboardHandler.text_copied called with text: {text}')
        """Call all registered callbacks with the copied text"""
        for callback in self.callbacks:
            callback(text)
        logging.debug('ClipboardHandler.text_copied finished')
        logging.debug(f"Copied text: `{text[:20]}`...")
            
    def get_highlighted_text(self):
        logging.debug('ClipboardHandler.get_highlighted_text called')
        """Get highlighted text using keyboard shortcuts"""
        def _get_text():
            logging.debug('_get_text called')
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
            logging.debug('_get_text finished')
            
        # Run in a separate thread to not block the UI
        thread = threading.Thread(target=_get_text)
        thread.daemon = True
        thread.start()
        logging.debug('ClipboardHandler.get_highlighted_text finished')
        
    def copy_text(self, text):
        logging.debug(f'ClipboardHandler.copy_text called with text: {text}')
        """Copy text to clipboard"""
        pyperclip.copy(text)
        logging.debug('ClipboardHandler.copy_text finished')
        
    def replace_text(self, text):
        logging.debug(f'ClipboardHandler.replace_text called with text: {text}')
        """Replace currently selected text with new text"""
        self.copy_text(text)
        
        # Paste the text
        self.keyboard_controller.press(keyboard.Key.ctrl)
        self.keyboard_controller.press('v')
        self.keyboard_controller.release('v')
        self.keyboard_controller.release(keyboard.Key.ctrl)
        logging.debug('ClipboardHandler.replace_text finished')
