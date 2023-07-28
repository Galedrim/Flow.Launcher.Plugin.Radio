import os
import json

JSON_SETTINGS = "./Plugin/settings.json"

class Channels:
    def __init__(self):
        self.channel_list = self.load()

    def load(self):
        if os.path.exists(JSON_SETTINGS):
            with open(JSON_SETTINGS, "r") as file:
                return sorted(json.load(file), key=lambda x: x["name"])
        else:
            with open(JSON_SETTINGS, "w"):
                pass
            return []

    def add_channel(self, name, url):
        channel = {'name': name, 'url': url, 'last_played': False}
        self.channel_list.append(channel)

        try:
            with open(JSON_SETTINGS, "w") as file:
                json.dump(self.channel_list, file, indent=4)
            return True

        except Exception:
            return False

    def delete_channel(self, url):    
        try:
            updated_channels = [channel for channel in self.channel_list 
                if not (url and channel.get("url") == url)]
            with open(JSON_SETTINGS, "w") as file:
                json.dump(updated_channels, file, indent=4)
            
            self.channel_list = updated_channels
            return True

        except Exception:
            return False

    def is_existing_channel(self, url, name):
        return not any(channel["name"] == name or 
                    channel["url"] == url for channel in self.channel_list)

    def get_last_played_channel(self):
        for channel in self.channel_list:
            if channel["last_played"]:
                return channel
        return None

    def set_last_played_radio(self, url):
        for channel in self.channel_list:
            channel["last_played"] = True if channel["url"] == url else False

        try:
            with open(JSON_SETTINGS, "w") as file:
                json.dump(self.channel_list, file, indent=4)
            return True

        except Exception:
            return False