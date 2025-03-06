from pynput import keyboard
import logging

class GlobalHotKey:
    def __init__(self):
        logging.debug('GlobalHotKey.__init__ called')
        self.callbacks = []
        self.listener = keyboard.GlobalHotKeys({
            '<alt>+r': self.on_activate
        })
        self.listener.start()
        logging.debug('GlobalHotKey.__init__ finished')
        
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
