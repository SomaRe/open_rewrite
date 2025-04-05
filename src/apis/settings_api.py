import os
import time
import logging
import winreg as reg
import sys
import requests
import subprocess
import tempfile
import webview
from src.utils.resource_path import resource_path
from src import __version__ as CURRENT_APP_VERSION

class SettingsAPI:
    """API for handling application settings, updates, and system integrations"""
    
    def __init__(self, settings_manager, hotkey):
        logging.debug('SettingsAPI.__init__ called')
        self.settings_manager = settings_manager
        self.hotkey = hotkey
        self._window = None
        logging.debug('SettingsAPI.__init__ finished')

    def get_current_version(self):
        """Returns the hardcoded current application version."""
        logging.info(f"Reporting current app version: {CURRENT_APP_VERSION}")
        return CURRENT_APP_VERSION

    def check_for_update(self):
        """Checks GitHub for the latest release and compares versions."""
        logging.info("Checking for updates...")
        repo = "SomaRe/open_rewrite"
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        asset_name = "open-rewrite-windows-x64.exe"

        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            latest_release = response.json()
            logging.debug(f"Latest release data: {latest_release}")
            latest_version = latest_release.get("tag_name", "0.0.0").lstrip('v') # Remove leading 'v' if present
            assets = latest_release.get("assets", [])

            logging.debug(f"Latest release tag: {latest_version}, Current version: {CURRENT_APP_VERSION}")

            # Simple version comparison (can be improved with packaging.version)
            if latest_version > CURRENT_APP_VERSION:
                logging.info(f"Update found: {latest_version}")
                download_url = None
                for asset in assets:
                    if asset.get("name") == asset_name:
                        download_url = asset.get("browser_download_url")
                        break

                if download_url:
                    logging.info(f"Asset found: {asset_name} at {download_url}")
                    return {
                        "update_available": True,
                        "latest_version": latest_version,
                        "download_url": download_url,
                        "release_notes": latest_release.get("body", "No release notes available.")
                    }
                else:
                    logging.warning(f"Update found ({latest_version}), but asset '{asset_name}' not found in latest release.")
                    return {"update_available": False, "message": f"Version {latest_version} found, but required asset missing."}
            else:
                logging.info("Application is up to date.")
                return {"update_available": False, "message": "You are running the latest version."}

        except requests.exceptions.RequestException as e:
            logging.error(f"Error checking for updates: {e}")
            return {"update_available": False, "error": f"Network error: {e}"}
        except Exception as e:
            logging.error(f"Unexpected error checking for updates: {e}")
            return {"update_available": False, "error": f"An unexpected error occurred: {e}"}

    def download_and_install_update(self, download_url):
        """Downloads the update and triggers the external updater script."""
        logging.info(f"Starting update download from: {download_url}")
        try:
            # Create a temporary file for the download
            temp_dir = tempfile.gettempdir()
            downloaded_exe_path = os.path.join(temp_dir, "open_rewrite_update.exe")

            # Download the file
            response = requests.get(download_url, stream=True, timeout=60) # Longer timeout for download
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(downloaded_exe_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)

            logging.info(f"Update downloaded successfully to: {downloaded_exe_path}")

            # Find the updater script (assuming it's packaged next to the main exe)
            app_dir = os.path.dirname(sys.executable)
            updater_script_path = os.path.join(app_dir, "updater.py")

            if not os.path.exists(updater_script_path):
                 # Fallback for development: check relative path
                 dev_updater_path = resource_path(os.path.join('src', 'updater.py'))
                 if os.path.exists(dev_updater_path):
                     updater_script_path = dev_updater_path
                 else:
                    logging.error("updater.py not found!")
                    return {"success": False, "error": "Updater script not found."}

            # Prepare arguments for the updater script
            current_exe_path = sys.executable

            # Launch the updater script in a new process
            # Use pythonw.exe to run without a console window
            python_executable = sys.executable.replace("python.exe", "pythonw.exe") if "python.exe" in sys.executable else sys.executable

            logging.info(f"Launching updater: {python_executable} {updater_script_path} \"{current_exe_path}\" \"{downloaded_exe_path}\"")
            subprocess.Popen([python_executable, updater_script_path, current_exe_path, downloaded_exe_path])

            # Exit the current application
            logging.info("Exiting application to allow update.")
            # Need to give the Popen call a moment to start
            time.sleep(1)
            # Force exit if webview doesn't close immediately
            os._exit(0) # Force exit if necessary

            # This part might not be reached if os._exit works
            return {"success": True, "message": "Update process initiated."}

        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading update: {e}")
            return {"success": False, "error": f"Download failed: {e}"}
        except Exception as e:
            logging.error(f"Error during update process: {e}")
            return {"success": False, "error": f"An unexpected error occurred: {e}"}

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