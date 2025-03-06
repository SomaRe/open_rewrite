import os
import webview
import logging
from src.settings.settings_manager import SettingsManager
from src.llm.openai_manager import OpenAIManager
from src.rewrite.rewrite_manager import RewriteManager
from src.utils.global_hotkey import GlobalHotKey
from src.utils.clipboard_handler import ClipboardHandler
from src.utils.resource_path import resource_path


class SettingsAPI:
    def __init__(self, settings_manager):
        logging.debug('SettingsAPI.__init__ called')
        self.settings_manager = settings_manager
        logging.debug('SettingsAPI.__init__ finished')

    def get_settings(self):
        logging.debug('SettingsAPI.get_settings called')
        settings = self.settings_manager.get_all()
        logging.debug(f'SettingsAPI.get_settings returning: {settings}')
        return settings

    def save_settings(self, settings):
        logging.debug(f'SettingsAPI.save_settings called with settings: {settings}')
        try:
            if not all(key in settings for key in ['api_key', 'base_url', 'model', 'system_message', 'tones', 'formats']):
                raise ValueError("Missing required settings fields")
            
            self.settings_manager.set_all(settings)
            logging.debug('SettingsAPI.save_settings: settings saved successfully')
            return True
        except Exception as e:
            logging.error(f"Error saving settings: {str(e)}")
            return False

    def reset_to_defaults(self):
        logging.debug('SettingsAPI.reset_to_defaults called')
        self.settings_manager.reset_to_defaults()
        logging.debug('SettingsAPI.reset_to_defaults finished')
        return True

    def close_window(self):
        logging.debug('SettingsAPI.close_window called')
        webview.windows[1].hide()
        logging.debug('SettingsAPI.close_window finished')
        return True

class WebViewAPI:
    def __init__(self, settings_manager, rewrite_manager, clipboard_handler):
        logging.debug('WebViewAPI.__init__ called')
        self.settings_manager = settings_manager
        self.rewrite_manager = rewrite_manager
        self.clipboard_handler = clipboard_handler
        self.openai_manager = OpenAIManager()
        self.settings_api = SettingsAPI(self.settings_manager)
        logging.debug('WebViewAPI.__init__ finished')

    def create_settings_window(self):
        logging.debug('WebViewAPI.create_settings_window called')
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
            logging.debug('WebViewAPI.create_settings_window: settings window created and shown')
        else:
            existing_settings_windows[0].show()
            logging.debug('WebViewAPI.create_settings_window: existing settings window shown')
        logging.debug('WebViewAPI.create_settings_window finished')

    def get_settings(self):
        logging.debug('WebViewAPI.get_settings called')
        """Get application settings"""
        settings = self.settings_manager.get_all()
        logging.debug(f'WebViewAPI.get_settings returning: {settings}')
        return settings

    def rewrite_text(self, text, option, category):
        logging.debug(f'WebViewAPI.rewrite_text called with text: {text}, option: {option}, category: {category}')
        """Rewrite text using selected option"""
        prompt = self.settings_manager.get_prompt(option, category)
        logging.debug(f'WebViewAPI.rewrite_text: prompt retrieved: {prompt}')
        
        def on_response(response):
            logging.debug(f'WebViewAPI.rewrite_text.on_response called with response: {response}')
            webview.windows[0].evaluate_js(f"showResult({repr(response)})")
            logging.debug('WebViewAPI.rewrite_text.on_response finished')
            
        def on_error(error):
            logging.error(f'WebViewAPI.rewrite_text.on_error called with error: {error}')
            webview.windows[0].evaluate_js(f"showError({repr(str(error))})")
            logging.debug('WebViewAPI.rewrite_text.on_error finished')
            
        self.rewrite_manager.rewrite_text(text, prompt, on_response, on_error)
        logging.debug('WebViewAPI.rewrite_text finished')
        return True

    def copy_to_clipboard(self, text):
        logging.debug(f'WebViewAPI.copy_to_clipboard called with text: {text}')
        """Copy text to clipboard"""
        self.clipboard_handler.copy_text(text)
        logging.debug('WebViewAPI.copy_to_clipboard finished')
        return True

    def replace_text(self, text):
        logging.debug(f'WebViewAPI.replace_text called with text: {text}')
        """Replace selected text with new text"""
        self.clipboard_handler.replace_text(text)
        webview.windows[0].hide()
        logging.debug('WebViewAPI.replace_text finished')
        return True

    def save_settings(self, settings):
        logging.debug(f'WebViewAPI.save_settings called with settings: {settings}')
        """Save application settings"""
        try:
            # Validate required fields
            if not all(key in settings for key in ['api_key', 'base_url', 'model', 'system_message', 'tones', 'formats']):
                raise ValueError("Missing required settings fields")
            
            # Save all settings
            self.settings_manager.set_all(settings)
            logging.debug('WebViewAPI.save_settings: settings saved successfully')
            return True
        except Exception as e:
            logging.error(f"Error saving settings: {str(e)}")
            return False

    def reset_to_defaults(self):
        logging.debug('WebViewAPI.reset_to_defaults called')
        """Reset settings to defaults"""
        self.settings_manager.reset_to_defaults()
        logging.debug('WebViewAPI.reset_to_defaults finished')
        return True

    def close_window(self):
        logging.debug('WebViewAPI.close_window called')
        """Close the current window"""
        webview.windows[0].hide()
        logging.debug('WebViewAPI.close_window finished')
        return True

    def open_settings_window(self):
        logging.debug('WebViewAPI.open_settings_window called')
        """Opens the settings window."""
        self.create_settings_window()
        logging.debug('WebViewAPI.open_settings_window finished')

class Application:
    def __init__(self):
        logging.debug('Application.__init__ called')
        self.settings_manager = SettingsManager()
        self.openai_manager = OpenAIManager()
        self.clipboard_handler = ClipboardHandler()
        self.hotkey = GlobalHotKey()
        
        # Create the API instance
        self.rewrite_manager = RewriteManager(self.openai_manager, self.settings_manager, self.clipboard_handler)
        self.web_api = WebViewAPI(
            self.settings_manager,
            self.rewrite_manager,
            self.clipboard_handler
        )
        logging.debug('Application.__init__ finished')

    def initialize(self):
        logging.debug('Application.initialize called')
        # Create window
        html_path = resource_path(os.path.join('src', 'ui', 'index.html'))
        logging.debug(f'Application.initialize: html_path = {html_path}')
        
        # Create window with the API
        webview.create_window(
            'Open Rewrite',
            html_path,
            js_api=self.web_api,
            width=300,
            height=400,
            frameless=True,
            easy_drag=True,
        )
        logging.debug('Application.initialize: main window created')

        # Setup connections
        self.hotkey.connect(self.on_hotkey_activated)
        self.clipboard_handler.register_callback(self.on_text_copied)
        logging.debug('Application.initialize: hotkey and clipboard handler connected')
        logging.debug('Application.initialize finished')

    def on_hotkey_activated(self):
        logging.debug('Application.on_hotkey_activated called')
        """Handle global hotkey activation"""
        self.clipboard_handler.get_highlighted_text()
        logging.debug('Application.on_hotkey_activated finished')
        
    def on_text_copied(self, text):
        logging.debug(f'Application.on_text_copied called with text: {text}')
        """Handle copied text"""
        if text.strip():
            if webview.windows:
                webview.windows[0].show()
                webview.windows[0].evaluate_js(f"showText({repr(text)})")
                logging.debug('Application.on_text_copied: main window shown and text evaluated')
        logging.debug('Application.on_text_copied finished')

