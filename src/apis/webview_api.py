import os
import time
import logging
import webview
from src.apis.settings_api import SettingsAPI
from src.managers.llm.openai_manager import OpenAIManager
from src.utils.resource_path import resource_path

class WebViewAPI:
    """API for handling webview interactions and text rewriting operations"""
    
    def __init__(self, settings_manager, rewrite_manager, clipboard_handler, hotkey):
        logging.debug('WebViewAPI.__init__ called')
        self.rewrite_manager = rewrite_manager
        self.clipboard_handler = clipboard_handler
        self.openai_manager = OpenAIManager()
        self.settings_api = SettingsAPI(settings_manager, hotkey)
        self._window = None
        logging.debug('WebViewAPI.__init__ finished')

    def set_window(self, window):
        """Set the window reference"""
        self._window = window

    def create_settings_window(self):
        logging.debug('WebViewAPI.create_settings_window called')
        """Creates and shows the settings window."""
        html_path = resource_path(os.path.join('src', 'ui', 'settings.html'))
        existing_settings_windows = [w for w in webview.windows if w.title == "Settings"]

        if self._window:
            self._window.hide()
        
        if not existing_settings_windows:
            settings_window = webview.create_window(
                "Settings",
                html_path,
                width=1000,
                height=700,
                js_api=self.settings_api,
                background_color="#27272a"
            )
            self.settings_api.set_window(settings_window)
            settings_window.show()
            logging.debug('WebViewAPI.create_settings_window: settings window created and shown')
        else:
            existing_settings_windows[0].show()
            logging.debug('WebViewAPI.create_settings_window: existing settings window shown')
        logging.debug('WebViewAPI.create_settings_window finished')

    def get_settings(self):
        logging.debug('WebViewAPI.get_settings called')
        """Get application settings"""
        settings = self.settings_api.get_settings()
        logging.debug(f'WebViewAPI.get_settings returning: {settings}')
        return settings

    def rewrite_text(self, text, option, category):
        logging.debug(f'WebViewAPI.rewrite_text called with text: {text[:20]+"..."}, option: {option}, category: {category}')
        """Rewrite text using selected option"""
        prompt = self.settings_api.get_prompt(option, category)
        logging.debug(f'WebViewAPI.rewrite_text: prompt retrieved: {prompt}')
        
        def on_response(response):
            logging.debug(f'WebViewAPI.rewrite_text.on_response called with response: {response}')
            self._window.evaluate_js(f"showResult({repr(response)})")
            logging.debug('WebViewAPI.rewrite_text.on_response finished')
            
        def on_error(error):
            logging.error(f'WebViewAPI.rewrite_text.on_error called with error: {error}')
            self._window.evaluate_js(f"showError({repr(str(error))})")
            logging.debug('WebViewAPI.rewrite_text.on_error finished')
            
        self.rewrite_manager.rewrite_text(text, prompt, on_response, on_error)
        logging.debug('WebViewAPI.rewrite_text finished')
        return True

    def handle_custom_request(self, text, custom_prompt):
        logging.debug(f'WebViewAPI.handle_custom_request called with text: {text[:20]+"..."}, prompt: {custom_prompt}')
        """Handle custom user requests through dedicated endpoint"""
        
        def on_response(response):
            logging.debug(f'WebViewAPI.handle_custom_request.on_response called with response: {response}')
            self._window.evaluate_js(f"showResult({repr(response)})")
            logging.debug('WebViewAPI.handle_custom_request.on_response finished')
            
        def on_error(error):
            logging.error(f'WebViewAPI.handle_custom_request.on_error called with error: {error}')
            self._window.evaluate_js(f"showError({repr(str(error))})")
            logging.debug('WebViewAPI.handle_custom_request.on_error finished')
            
        self.rewrite_manager.handle_custom_request(text, custom_prompt, on_response, on_error)
        logging.debug('WebViewAPI.handle_custom_request finished')
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
        self._window.hide()
        time.sleep(0.1)
        self.clipboard_handler.replace_text(text)
        logging.debug('WebViewAPI.replace_text finished')
        return True

    def exit_app(self):
        logging.debug('WebViewAPI.exit_app called')
        """Exit the application"""
        if self._window:
            self._window.destroy()
        logging.debug('WebViewAPI.exit_app finished')
        return True

    def close_window(self):
        logging.debug('WebViewAPI.close_window called')
        """Hide the window"""
        if self._window:
            self._window.hide()
        logging.debug('WebViewAPI.close_window finished')
        return True

    def open_settings_window(self):
        logging.debug('WebViewAPI.open_settings_window called')
        """Opens the settings window."""
        self.create_settings_window()
        logging.debug('WebViewAPI.open_settings_window finished')