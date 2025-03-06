import json
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SettingsManager:
    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file
        logging.info(f"Initializing SettingsManager with settings file: {settings_file}")
        self.settings = self.load_settings()

    def load_settings(self):
        """Load settings from the JSON file."""
        logging.info(f"Loading settings from {self.settings_file}")
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                logging.debug("Successfully loaded settings from file")
                # Update icon paths to use resource_path
                for category in ['tones', 'formats']:
                    if category in settings:
                        for option in settings[category]:
                            icon_path = settings[category][option].get('icon', '')
                            settings[category][option]['icon'] = icon_path
                return settings
        except FileNotFoundError:
            logging.warning(f"Settings file not found at {self.settings_file}, creating with defaults")
            default_settings = self.get_default_settings()
            self.save_settings(default_settings)
            return default_settings
        except json.JSONDecodeError:
            logging.error(f"Error decoding settings file, falling back to defaults.")
            return self.get_default_settings()

    def get(self, key, default=None):
        """Get a setting by key."""
        value = self.settings.get(key, default)
        logging.debug(f"Getting setting {key}: {value}")
        return value

    def set(self, key, value):
        """Set a setting."""
        logging.info(f"Setting {key} to {value}")
        self.settings[key] = value
        self.save_settings()

    def get_all(self):
        """Get all settings."""
        logging.debug("Retrieving all settings")
        return self.settings

    def set_all(self, settings_dict):
        """Set all settings at once."""
        logging.info("Updating all settings")
        self.settings = settings_dict
        self.save_settings()

    def save_settings(self, settings=None):
        """Save settings to the JSON file."""
        logging.info(f"Saving settings to {self.settings_file}")
        if settings is not None:
            self.settings = settings
            
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            logging.debug("Settings saved successfully")
        except Exception as e:
            logging.error(f"Error saving settings: {str(e)}")

    def reset_to_defaults(self):
        """Reset settings to default values."""
        logging.info("Resetting settings to defaults")
        default_settings = self.get_default_settings()
        self.settings = default_settings
        self.save_settings()

    def get_prompt(self, option, category):
        """Get prompt for a specified option and category."""
        logging.debug(f"Getting prompt for {category}.{option}")
        if category in self.settings and option in self.settings[category]:
            return self.settings[category][option]['prompt']
        logging.warning(f"Prompt not found for {category}.{option}")
        return None

    def get_default_settings(self):
        """Return the default settings for the app."""
        logging.debug("Getting default settings")
        return {
            # ... [rest of the default settings remain unchanged]
        }
