import json
import os

from src.utils.resource_path import resource_path

class SettingsManager:
    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()  # Load settings upon initialization

    def load_settings(self):
        """Load settings from the JSON file."""
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                # Update icon paths to use resource_path
                for category in ['tones', 'formats']:
                    if category in settings:
                        for option in settings[category]:
                            icon_path = settings[category][option].get('icon', '')
                            settings[category][option]['icon'] = os.path.join('src', 'resources', 'material_icons_round', icon_path)
                return settings
        except FileNotFoundError:
            # Provide default settings if the file doesn't exist
            default_settings = self.get_default_settings()
            self.save_settings(default_settings)  # Save the defaults to the new file
            return default_settings
        except json.JSONDecodeError:
            print(f"Error decoding settings file, falling back to defaults.")
            return self.get_default_settings()  # Or take other appropriate action

    def get(self, key, default=None):
        """Get a setting by key."""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a setting."""
        self.settings[key] = value
        self.save_settings()

    def get_all(self):
        """Get all settings."""
        return self.settings

    def set_all(self, settings_dict):
        """Set all settings at once."""
        self.settings = settings_dict
        self.save_settings()

    def save_settings(self, settings=None):
        """Save settings to the JSON file."""
        if settings is not None:
            self.settings = settings
            
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def reset_to_defaults(self):
        """Reset settings to default values."""
        default_settings = self.get_default_settings()
        self.settings = default_settings
        self.save_settings()

    def get_prompt(self, option, category):
        """Get prompt for a specified option and category."""
        if category in self.settings and option in self.settings[category]:
            return self.settings[category][option]['prompt']
        return None  # Or raise an exception or return a default

    def get_default_settings(self):
        """Return the default settings for the app."""
        return {
            'api_key': '',
            'base_url': 'https://api.openai.com/v1/',
            'model': 'gpt-4o-mini',
            'system_message': "You are a helpful tool called Open Rewrite, your main purpose is to rewrite the text as instructions given by the user, do not add any extra information or add any new information, just rewrite",
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
