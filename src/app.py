import os
import webview
from src.settings.settings_manager import SettingsManager
from src.llm.openai_manager import OpenAIManager
from src.rewrite.rewrite_manager import RewriteManager
from src.utils.global_hotkey import GlobalHotKey
from src.utils.clipboard_handler import ClipboardHandler
from src.utils.resource_path import resource_path

class Application:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.openai_manager = OpenAIManager(self.settings_manager)
        self.clipboard_handler = ClipboardHandler()
        self.rewrite_manager = RewriteManager(self.openai_manager, self.clipboard_handler)
        self.hotkey = GlobalHotKey()
        
        self.window = None
        
    def initialize(self):
        # Create window
        html_path = resource_path(os.path.join('src', 'web', 'templates', 'index.html'))
        self.window = webview.create_window(
            'Open Rewrite', 
            html_path, 
            js_api=self,
            width=600, 
            height=800,
            resizable=True,
            frameless=True,
            easy_drag=True,
            hidden=True
        )
        
        # Setup connections
        self.hotkey.connect(self.on_hotkey_activated)
        self.clipboard_handler.register_callback(self.on_text_copied)
        
    def on_hotkey_activated(self):
        """Handle global hotkey activation"""
        self.clipboard_handler.get_highlighted_text()
        
    def on_text_copied(self, text):
        """Handle copied text"""
        if text.strip():  # Only show if text isn't empty
            self.window.show()
            self.window.evaluate_js(f"showText({repr(text)})")
        
    # JavaScript API methods
    def rewrite_text(self, text, option, category):
        """Rewrite text using selected option"""
        prompt = self.settings_manager.get_prompt(option, category)
        
        def on_response(response):
            self.window.evaluate_js(f"showResult({repr(response)})")
            
        def on_error(error):
            self.window.evaluate_js(f"showError({repr(str(error))})")
            
        self.openai_manager.generate_response(prompt, text, on_response, on_error)
        return True
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.clipboard_handler.copy_text(text)
        return True
        
    def replace_text(self, text):
        """Replace selected text with new text"""
        self.clipboard_handler.replace_text(text)
        self.window.hide()
        return True
        
    def show_settings(self):
        """Show settings window"""
        html_path = resource_path(os.path.join('src', 'web', 'templates', 'settings.html'))
        settings_window = webview.create_window(
            'Settings - Open Rewrite',
            html_path,
            js_api=self,
            width=800,
            height=600,
            resizable=True,
            frameless=True,
            easy_drag=True
        )
        return True
        
    def get_settings(self):
        """Get application settings"""
        return self.settings_manager.get_all()
        
    def save_settings(self, settings):
        """Save application settings"""
        self.settings_manager.set_all(settings)
        self.openai_manager.load_settings()
        return True

    def reset_to_defaults(self):
        """Reset settings to defaults"""
        self.settings_manager.reset_to_defaults()
        self.openai_manager.load_settings()
        return True
        
    def close_window(self):
        """Close the current window"""
        self.window.hide()
        return True