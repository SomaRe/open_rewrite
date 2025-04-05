import os
import time
import webview
import logging
import sys
from src.managers.settings_manager import SettingsManager
from src.managers.llm.openai_manager import OpenAIManager
from src.managers.rewrite_manager import RewriteManager
from src.utils.global_hotkey import GlobalHotKey
from src.utils.clipboard_handler import ClipboardHandler
from src.utils.resource_path import resource_path
from src.apis.webview_api import WebViewAPI

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from . import __version__ as CURRENT_APP_VERSION
    logging.info(f"Current app version: {CURRENT_APP_VERSION}")
except ImportError:
    logging.warning("_version.py not found. Falling back to '0.0.0-dev'.")
    CURRENT_APP_VERSION = "0.0.0-dev"


class Application:
    def __init__(self):
        logging.debug('Application.__init__ called')
        self.settings_manager = SettingsManager()
        self.openai_manager = OpenAIManager()
        self.clipboard_handler = ClipboardHandler()
        self.hotkey = GlobalHotKey(
            self.settings_manager.get('hotkey', '<alt>+r')
        )
        
        # Create the API instance
        self.rewrite_manager = RewriteManager(self.openai_manager, self.settings_manager, self.clipboard_handler)
        self.web_api = WebViewAPI(
            self.settings_manager,
            self.rewrite_manager,
            self.clipboard_handler,
            self.hotkey
        )
        logging.debug('Application.__init__ finished')

    def calculate_window_height(self):
        """Calculate window height based on number of options"""
        # Fixed heights
        header_height = 44  # 2.75rem
        input_height = 44   # 2.75rem
        separator_height = 18  # 0.25rem + margins
        
        # Get number of options
        settings = self.settings_manager.get_all()
        num_tones = len(settings.get('tones', {}))
        num_formats = len(settings.get('formats', {}))
        total_options = num_tones + num_formats
        
        # Each option is 28px (1.75rem)
        options_height = total_options * 28

        # Extra height because of header.
        if sys.platform == "win32": # windows
            extra_height = 56
        else:
            extra_height = 0
        
        # Total height is sum of all components
        total_height = header_height + input_height + separator_height + options_height + extra_height + 25
        
        # Add some padding
        return min(max(total_height, 300), 800)  # Keep between 300-800px

    def initialize(self):
        logging.debug('Application.initialize called')
        # Create window
        html_path = resource_path(os.path.join('src', 'ui', 'app.html'))
        logging.debug(f'Application.initialize: html_path = {html_path}')
        
        # Calculate dynamic height
        window_height = self.calculate_window_height()
        
        # Create window with the API
        self._window = webview.create_window(
            'Open Rewrite',
            html_path,
            js_api=self.web_api,
            width=300,
            height=window_height,
            on_top=True,
            frameless=True,
            background_color="#27272a",
            hidden=True
        )

        # Pass window reference to API
        self.web_api.set_window(self._window)
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
                self._window.evaluate_js(f"handleSelectedText({repr(text)})")
                self._window.show()
                logging.debug('Application.on_text_copied: main window shown and text evaluated')
        logging.debug('Application.on_text_copied finished')

