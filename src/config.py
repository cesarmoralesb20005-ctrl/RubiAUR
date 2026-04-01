import os
import json

class ConfigManager:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/rubiaur")
        os.makedirs(self.config_dir, exist_ok=True)
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.history_file = os.path.join(self.config_dir, "history.json")

    def load_settings(self, default_settings):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    default_settings.update(json.load(f))
            except Exception:
                pass
        return default_settings

    def save_settings(self, settings):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f)
        except Exception:
            pass

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_history(self, history):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f)
        except Exception:
            pass