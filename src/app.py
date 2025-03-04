import os
import webview
from src.settings.settings_manager import SettingsManager
from src.llm.openai_manager import OpenAIManager
from src.rewrite.rewrite_manager import RewriteManager
from src.utils.global_hotkey import GlobalHotKey
from src.utils.clipboard_handler import ClipboardHandler
from src.utils.resource_path import resource_path

class WebViewAPI:
    def __init__(self, settings_manager, openai_manager, clipboard_handler):
        self.settings_manager = settings_manager
        self.openai_manager = openai_manager
        self.clipboard_handler = clipboard_handler

    def get_settings(self):
        """Get application settings"""
        settings = self.settings_manager.get_all()
        return settings

    def rewrite_text(self, text, option, category):
        """Rewrite text using selected option"""
        prompt = self.settings_manager.get_prompt(option, category)
        
        def on_response(response):
            webview.windows[0].evaluate_js(f"showResult({repr(response)})")
            
        def on_error(error):
            webview.windows[0].evaluate_js(f"showError({repr(str(error))})")
            
        self.openai_manager.generate_response(prompt, text, on_response, on_error)
        return True

    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.clipboard_handler.copy_text(text)
        return True

    def replace_text(self, text):
        """Replace selected text with new text"""
        self.clipboard_handler.replace_text(text)
        webview.windows[0].hide()
        return True

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
        webview.windows[0].hide()
        return True

class Application:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.openai_manager = OpenAIManager(self.settings_manager)
        self.clipboard_handler = ClipboardHandler()
        self.hotkey = GlobalHotKey()
        
        # Create the API instance
        self.web_api = WebViewAPI(
            self.settings_manager,
            self.openai_manager,
            self.clipboard_handler
        )
        self.settings_window = None

    def initialize(self):
        # Create window
        html_path = resource_path(os.path.join('src', 'ui', 'index.html'))
        
        # Create window with the API
        webview.create_window(
            'Open Rewrite',
            html_path,
            js_api=self.web_api,  # Use the API instance
            width=600,
            height=800,
            frameless=True,
            easy_drag=True,
        )

        # Setup connections
        self.hotkey.connect(self.on_hotkey_activated)
        self.clipboard_handler.register_callback(self.on_text_copied)
        webview.expose(self.web_api)
        self.web_api.app = self

    def on_hotkey_activated(self):
        """Handle global hotkey activation"""
        self.clipboard_handler.get_highlighted_text()
        
    def on_text_copied(self, text):
        """Handle copied text"""
        if text.strip():  # Only show if text isn't empty
            if webview.windows:
                webview.windows[0].show()
                webview.windows[0].evaluate_js(f"showText({repr(text)})")

    def create_settings_window(self):
        """Creates and shows the settings window."""
        if self.settings_window is None:  # Only create one settings window
            self.settings_window = webview.create_window(
                "Settings",
                "static/settings.html",  # Or wherever your settings HTML is
                width=800,  # Adjust as needed
                height=600, # Adjust as needed
                resizable=False,
                on_top=True
            )
            self.settings_window.events.closed += self.on_settings_window_closed
        else:
            self.settings_window.show() # If it exists, just show it

    def on_settings_window_closed(self):
        """Handles the settings window closing event."""
        self.settings_window = None # Reset the window reference
