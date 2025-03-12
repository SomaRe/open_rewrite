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
        logging.debug('SettingsAPI.__init__ finished')

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
            
            new_hotkey = settings.get('hotkey', '<ctrl>+r')
            if new_hotkey != self.hotkey.hotkey_combination:
                logging.debug(f"New hotkey found!")
                self.hotkey.update_hotkey(new_hotkey)

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
        self.settings_manager = settings_manager
        self.rewrite_manager = rewrite_manager
        self.clipboard_handler = clipboard_handler
        self.hotkey = hotkey
        self.openai_manager = OpenAIManager()
        self.settings_api = SettingsAPI(self.settings_manager, self.hotkey)
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

        if webview.windows:
            webview.windows[0].hide()
        
        if not existing_settings_windows:
            settings_window = webview.create_window(
                "Settings",
                html_path,
                width=1000,
                height=600,
                js_api=self.settings_api,
                background_color="#27272a"
                # frameless=True,
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
        if category == 'custom':
            # For custom requests, use the option as the prompt directly
            prompt = f"Rewrite the text as follows: {option}"
        else:
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
        webview.windows[0].hide()
        time.sleep(0.1)
        self.clipboard_handler.replace_text(text)
        logging.debug('WebViewAPI.replace_text finished')
        return True

    def save_settings(self, settings):
        logging.debug(f'WebViewAPI.save_settings called with settings: {settings}')
        """Save application settings"""
        try:
            # Validate required fields
            if not all(key in settings for key in ['hotkey', 'api_key', 'base_url', 'model', 'system_message', 'tones', 'formats']):
                raise ValueError("Missing required settings fields")
            
            # Update hotkey if changed
            new_hotkey = settings.get('hotkey', '<ctrl>+r')
            if new_hotkey != self.hotkey.hotkey_combination:
                self.hotkey.update_hotkey(new_hotkey)
            
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

    def exit_app(self):
        logging.debug('WebViewAPI.exit_app called')
        """Exit the application"""
        if self._window:
            self._window.destroy()
        logging.debug('WebViewAPI.exit_app finished')
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
            self.settings_manager.get('hotkey', '<ctrl>+r')
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

    def initialize(self):
        logging.debug('Application.initialize called')
        # Create window
        html_path = resource_path(os.path.join('src', 'ui', 'app.html'))
        logging.debug(f'Application.initialize: html_path = {html_path}')
        
        # Create window with the API
        window = webview.create_window(
            'Open Rewrite',
            html_path,
            js_api=self.web_api,
            width=300,
            height=400,
            on_top=True,
            frameless=True,
            background_color="#27272a"
        )

        # Pass window reference to API
        self.web_api.set_window(window)
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
                webview.windows[0].evaluate_js(f"showText({repr(text)})")
                webview.windows[0].show()
                logging.debug('Application.on_text_copied: main window shown and text evaluated')
        logging.debug('Application.on_text_copied finished')

