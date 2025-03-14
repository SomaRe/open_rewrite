import json
import os
import logging

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

    def reload(self):
        """Reload settings from the file."""
        logging.info(f"Reloading settings from {self.settings_file}")
        self.settings = self.load_settings()

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
            self.reload()
            logging.debug("Settings saved successfully")
        except Exception as e:
            logging.error(f"Error saving settings: {str(e)}")

    def reset_to_defaults(self):
        """Reset settings to default values."""
        logging.info("Resetting settings to defaults")
        default_settings = self.get_default_settings()
        self.settings = default_settings
        self.save_settings()


    def get_default_settings(self):
        """Return the default settings for the app."""
        logging.debug("Getting default settings")
        return {
            'hotkey': '<alt>+r',
            'api_key': '',
            'base_url': 'https://api.openai.com/v1/',
            'model': 'gpt-4o-mini',
            'system_message': "You are a helpful tool called Open Rewrite, your main purpose is to rewrite the text as instructions given by the user, do not add any extra information or add any new information, just rewrite",
            'custom_system_message': (
                "You are a helpful tool called Open Rewrite. Follow the user's custom instructions exactly as provided."
            ),
            'tones': {
                "Friendly": {
                    "prompt": "Rewrite the text in a friendly tone. Ensure it sounds approachable and warm. Do not assume anything or add any new information. don't use funky words.",
                    "icon": os.path.join('static', 'material_icons_round', 'social','round_emoji_emotions_black_48dp_white.png')
                },
                "Professional": {
                    "prompt": "Rewrite the text in a professional tone. Make it sound formal and polished. Use simple English words. Do not assume anything or add any new information.",
                    "icon": os.path.join('static', 'material_icons_round', 'places','round_business_center_black_48dp_white.png')
                },
                "Polite": {
                    "prompt": "Rewrite the text in a polite tone. Ensure it is courteous and respectful but also use casual language.Use simple English words. Do not assume anything or add any new information.",
                    "icon": os.path.join('static', 'material_icons_round', 'maps','round_local_florist_black_48dp_white.png')
                },
                "Casual": {
                    "prompt": "Rewrite the text in a casual tone. Make it sound relaxed and informal. Do not use funky words,use basic english words. Do not assume anything or add new information.",
                    "icon": os.path.join('static', 'material_icons_round', 'maps','round_local_cafe_black_48dp_white.png')
                },
                "Concise": {
                    "prompt": "Rewrite the text in a concise way. Use only the main points. use simple English words. Do not assume anything or add any new information.",
                    "icon": os.path.join('static', 'material_icons_round', 'editor','round_vertical_align_center_black_48dp_white.png')
                }
            },
            'formats': {
                "Summary": {
                    "prompt": "Summarize the text. Capture the main points succinctly without adding new information or assuming anything.",
                    "icon": os.path.join('static', 'material_icons_round', 'content','round_sort_black_48dp_white.png')
                },
                "Keypoints": {
                    "prompt": "Rewrite the text highlighting the key points. Use bullet points to make it clear and concise. Do not add new information or assume anything.",
                    "icon": os.path.join('static', 'material_icons_round', 'editor','round_format_list_bulleted_black_48dp_white.png')
                },
                "List": {
                    "prompt": "Rewrite the text as a list. Break down the information into a clear, itemized list. Do not assume anything or add new information.",
                    "icon": os.path.join('static', 'material_icons_round', 'editor','round_format_list_numbered_black_48dp_white.png')
                },
                "Markdown": {
                    "prompt": "Rewrite the text using Markdown formatting. Organize the information with appropriate headers, lists, and other Markdown elements. Do not assume anything or add new information.",
                    "icon": os.path.join('static', 'material_icons_round', 'editor','round_table_chart_black_48dp_white.png')
                }
            }
        }
