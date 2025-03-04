from pynput import keyboard

class GlobalHotKey:
    def __init__(self):
        self.callbacks = []
        self.listener = keyboard.GlobalHotKeys({
            '<alt>+r': self.on_activate
        })
        self.listener.start()
        
    def connect(self, callback):
        """Connect a callback to the hotkey activation"""
        self.callbacks.append(callback)
        
    def on_activate(self):
        """Called when the hotkey is activated"""
        for callback in self.callbacks:
            callback()
            
    def __del__(self):
        """Clean up the listener when the object is destroyed"""
        self.listener.stop()