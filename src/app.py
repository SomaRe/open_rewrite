import os
import webview
from src.settings.settings_manager import SettingsManager
from src.llm.openai_manager import OpenAIManager
from src.rewrite.rewrite_manager import RewriteManager
from src.utils.global_hotkey import GlobalHotKey
from src.utils.clipboard_handler import ClipboardHandler
from src.utils.resource_path import resource_path

class SettingsAPI:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager

    def get_settings(self):
        return self.settings_manager.get_all()

    def save_settings(self, settings):
        try:
            if not all(key in settings for key in ['api_key', 'base_url', 'model', 'system_message', 'tones', 'formats']):
                raise ValueError("Missing required settings fields")
            
            self.settings_manager.set_all(settings)
            return True
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            return False

    def reset_to_defaults(self):
        self.settings_manager.reset_to_defaults()
        return True

    def close_window(self):
        webview.windows[1].hide()
        return True

class WebViewAPI:
    def __init__(self, settings_manager, rewrite_manager, clipboard_handler):
        self.settings_manager = settings_manager
        self.rewrite_manager = rewrite_manager
        self.clipboard_handler = clipboard_handler
        self.openai_manager = OpenAIManager(self.settings_manager)
        self.settings_api = SettingsAPI(settings_manager)

    def create_settings_window(self):
        """Creates and shows the settings window."""
        html_path = resource_path(os.path.join('src', 'ui', 'settings.html'))
        existing_settings_windows = [w for w in webview.windows if w.title == "Settings"]
        
        if not existing_settings_windows:
            settings_window = webview.create_window(
                "Settings",
                html_path,
                width=800,
                height=600,
                on_top=True,
                js_api=self.settings_api
            )
            settings_window.show()
        else:
            existing_settings_windows[0].show()

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
            
        self.rewrite_manager.rewrite_text(text, prompt, on_response, on_error)
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
        try:
            # Validate required fields
            if not all(key in settings for key in ['api_key', 'base_url', 'model', 'system_message', 'tones', 'formats']):
                raise ValueError("Missing required settings fields")
            
            # Save all settings
            self.settings_manager.set_all(settings)
            self.openai_manager.load_settings()
            return True
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            return False

    def reset_to_defaults(self):
        """Reset settings to defaults"""
        self.settings_manager.reset_to_defaults()
        self.openai_manager.load_settings()
        return True

    def close_window(self):
        """Close the current window"""
        webview.windows[0].hide()
        return True

    def open_settings_window(self):
        """Opens the settings window."""
        self.create_settings_window()

class Application:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.openai_manager = OpenAIManager(self.settings_manager)
        self.clipboard_handler = ClipboardHandler()
        self.hotkey = GlobalHotKey()
        
        # Create the API instance
        self.rewrite_manager = RewriteManager(self.openai_manager, self.clipboard_handler)
        self.web_api = WebViewAPI(
            self.settings_manager,
            self.rewrite_manager,
            self.clipboard_handler
        )

    def initialize(self):
        # Create window
        html_path = resource_path(os.path.join('src', 'ui', 'index.html'))
        
        # Create window with the API
        webview.create_window(
            'Open Rewrite',
            html_path,
            js_api=self.web_api,
            width=375,
            height=500,
            frameless=True,
            easy_drag=True,
        )

        # Setup connections
        self.hotkey.connect(self.on_hotkey_activated)
        self.clipboard_handler.register_callback(self.on_text_copied)

    def on_hotkey_activated(self):
        """Handle global hotkey activation"""
        self.clipboard_handler.get_highlighted_text()
        
    def on_text_copied(self, text):
        """Handle copied text"""
        if text.strip():
            if webview.windows:
                webview.windows[0].show()
                webview.windows[0].evaluate_js(f"showText({repr(text)})")

