from pynput import keyboard
import logging

class GlobalHotKey:
    def __init__(self, initial_hotkey='<ctrl>+r'):
        logging.debug('GlobalHotKey.__init__ called')
        self.callbacks = []
        self.hotkey_combination = initial_hotkey
        self.listener = None
        self.start_listener()
        logging.debug('GlobalHotKey.__init__ finished')

    def start_listener(self):
        if self.listener:
            self.listener.stop()
        self.listener = keyboard.GlobalHotKeys({
            self.hotkey_combination: self.on_activate
        })
        self.listener.start()

    def update_hotkey(self, new_combination):
        logging.debug(f'Updating hotkey to {new_combination}')
        self.hotkey_combination = new_combination
        self.start_listener()
        
    def connect(self, callback):
        logging.debug('GlobalHotKey.connect called')
        """Connect a callback to the hotkey activation"""
        self.callbacks.append(callback)
        logging.debug('GlobalHotKey.connect finished')
        
    def on_activate(self):
        logging.debug('GlobalHotKey.on_activate called')
        """Called when the hotkey is activated"""
        for callback in self.callbacks:
            callback()
        logging.debug('GlobalHotKey.on_activate finished')
            
    def __del__(self):
        logging.debug('GlobalHotKey.__del__ called')
        """Clean up the listener when the object is destroyed"""
        self.listener.stop()
        logging.debug('GlobalHotKey.__del__ finished')
