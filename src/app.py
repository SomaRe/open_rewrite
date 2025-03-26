import os
import time
import webview
import logging
import winreg as reg
import sys
from src.managers.settings_manager import SettingsManager
from src.managers.llm.openai_manager import OpenAIManager
from src.managers.rewrite_manager import RewriteManager
from src.utils.global_hotkey import GlobalHotKey
from src.utils.clipboard_handler import ClipboardHandler
from src.utils.resource_path import resource_path


class SettingsAPI:
    def __init__(self, settings_manager, hotkey):
        logging.debug('SettingsAPI.__init__ called')
        self.settings_manager = settings_manager
        self.hotkey = hotkey
        self._window = None
        logging.debug('SettingsAPI.__init__ finished')

    def get_prompt(self, option, category):
        """Get prompt for a specified option and category."""
        logging.debug(f"Getting prompt for {category}.{option}")
        settings = self.settings_manager.get_all()
        if category in settings and option in settings[category]:
            return settings[category][option]['prompt']
        logging.warning(f"Prompt not found for {category}.{option}")
        return None

    def set_window(self, window):
        """Set the window reference"""
        self._window = window

    def get_settings(self):
        logging.debug('SettingsAPI.get_settings called')
        settings = self.settings_manager.get_all()
        logging.debug(f'SettingsAPI.get_settings returning: {settings}')
        return settings

    def save_settings(self, settings):
        logging.debug(f'SettingsAPI.save_settings called with settings: {settings}')
        try:
            if not all(key in settings for key in ['hotkey','api_key', 'base_url', 'model', 'system_message', 'tones', 'formats']):
                raise ValueError("Missing required settings fields")
            
            new_hotkey = settings.get('hotkey', '<alt>+r')
            if new_hotkey != self.hotkey.hotkey_combination:
                logging.debug(f"New hotkey found!")
                self.hotkey.update_hotkey(new_hotkey)

            self.settings_manager.set_all(settings)
            
            # Notify MAIN window to refresh content
            if webview.windows and len(webview.windows) > 0:
                main_window = webview.windows[0]  # Main window is always first
                main_window.evaluate_js("refreshOptions()")
                
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

    def check_startup_status(self):
        """Check if the app is in Windows startup"""
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Run", 
                            0, reg.KEY_READ)
            try:
                value, _ = reg.QueryValueEx(key, "OpenRewrite")
                return 'enabled' if value == sys.executable else 'disabled'
            except FileNotFoundError:
                return 'disabled'
        except Exception as e:
            print(f"Error checking startup status: {e}")
            return 'disabled'

    def toggle_startup(self):
        """Toggle the app in Windows startup"""
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Run", 
                            0, reg.KEY_SET_VALUE)
            
            if self.check_startup_status() == 'enabled':
                # Remove from startup
                reg.DeleteValue(key, "OpenRewrite")
                return {'success': True, 'message': 'Removed from startup'}
            else:
                # Add to startup
                reg.SetValueEx(key, "OpenRewrite", 0, reg.REG_SZ, sys.executable)
                return {'success': True, 'message': 'Added to startup'}
        except Exception as e:
            print(f"Error toggling startup: {e}")
            return {'success': False, 'message': str(e)}

    def get_available_icons(self):
        """Get list of available material icons (white versions) organized by category"""
        import os
        icons = {}
        icon_dir = os.path.join('src', 'ui', 'static', 'material_icons_round')
        for root, dirs, files in os.walk(icon_dir):
            category = os.path.basename(root)
            if category == 'material_icons_round':
                continue
            icons[category] = []
            for file in files:
                if file.endswith('white.png'):
                    # Get relative path from static folder
                    rel_path = os.path.relpath(os.path.join(root, file), 
                                             os.path.join('src', 'ui', 'static'))
                    icons[category].append(rel_path.replace('\\', '/'))
        return {k: sorted(v) for k, v in icons.items()}

class WebViewAPI:
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
                height=600,
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

