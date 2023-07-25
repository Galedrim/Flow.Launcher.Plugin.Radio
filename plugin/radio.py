from flox import Flox
from player import VLCPlayer
from streamlink.session import Streamlink
from urllib import request

import json
import os
import re

ICON_APP = "./Images/app.png"
ICON_UNAVAILABLE = "./Images/app-grayscale.png"
ICON_SETTINGS = "./Images/settings.png"

JSON_SETTINGS = "./Plugin/settings.json"


class Radio(Flox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radio_list = []
        if os.path.exists(JSON_SETTINGS):
            with open(JSON_SETTINGS, "r") as file:
                data = json.load(file)
                self.radio_list = sorted(data, key=lambda x: x["name"])
        else:
            with open(JSON_SETTINGS, "w") as file:
                pass

        self.vlc_player = VLCPlayer()

    def results(self, query):
        args = query.strip().split(" ")
        command = str(args[0]).lower()
        if not command:
            self.process_default_command()
        elif command in "list":
            self.process_list_command(args[1:])
        elif command in "add":
            self.process_add_command(args[1:])
        elif command in "rem":
            self.process_remove_command(args[1:])
        elif command in "reco":
            self.process_reconnect_command()
        else:
            self.process_default_command()

        return self._results

    def process_list_command(self, args):
        for radio in self.radio_list:
            name = radio["name"]
            url = radio["url"]

            if args and not any(arg.lower() in name.lower() for arg in args):
                continue

            stream = self.get_best_stream(url)
            if stream:
                self.add_item(
                    title="Start: {0}".format(name),
                    subtitle=url,
                    icon=ICON_APP,
                    method=self.start_new_stream,
                    parameters=[url]
                )
            else:
                self.add_item(
                    title="Unavailable: {0}".format(name),
                    subtitle=url,
                    icon=ICON_UNAVAILABLE
                )

    def process_add_command(self, args):
        if len(args) == 1:
            name = args[0]
            self.add_item(
                title="Add {0} [URL]".format(name),
                subtitle="Add an URL stream with associated name",
                icon=ICON_SETTINGS
            )
        elif len(args) == 2:
            name = args[0]
            url = args[1]
            if self.is_radio_in_json(name, url) and self.is_youtube_live_channel(url):
                self.add_item(
                    title="Add {0} {1}".format(name, url),
                    subtitle="Add an URL stream with associated name",
                    icon=ICON_SETTINGS,
                    method=self.save_radio_to_json,
                    parameters=[name, url]
                )
            else:
                self.add_item(
                    title="Add {0} [URL]".format(name),
                    subtitle="Add an URL stream with associated name",
                    icon=ICON_SETTINGS
                )
        else:
            self.add_item(
                title="Add [NAME] [URL]",
                subtitle="Add a new URL stream with associated name",
                icon=ICON_SETTINGS
            )

    def process_remove_command(self, args):
        if not args:
            self.add_item(
                title="Rem [NAME] or [URL]",
                subtitle="Remove an URL stream with associated name",
                icon=ICON_SETTINGS
            )
        else:
            for radio in self.radio_list:
                url = radio["url"]
                name = radio["name"]
                arg = str(args[0])
                if arg.lower() in url.lower() or arg.lower() in name.lower():
                    self.add_item(
                        title="Rem: {0} - {1}".format(name, url),
                        subtitle="Remove an URL stream with associated name",
                        icon=ICON_SETTINGS,
                        method=self.delete_radio_from_json,
                        parameters=[url]
                    )

    def process_default_command(self):
        last_stream = self.get_last_played_radio()
        if last_stream and self.is_stream_available(last_stream["url"]):
            self.add_item(
                title="Play/Pause: {0}".format(last_stream["name"]),
                subtitle=last_stream["url"],
                icon=ICON_APP,
                method=self.play_pause_stream,
                parameters=[last_stream["url"]]
            )
        else:
            self.add_item(
                title="Select a radio with the command 'ra list'",
                icon=ICON_APP,
            )

    def process_reconnect_command(self):
        last_radio = self.get_last_played_radio()
        if last_radio and self.is_stream_available(last_radio["url"]):
            name = last_radio["name"]
            url = last_radio["url"]
            self.add_item(
                title="Reconnect last radio played : {0}".format(name),
                subtitle=url,
                icon=ICON_APP,
                method=self.start_new_stream,
                parameters=[url]
            )
        else:
            self.add_item(
                title="Select a radio with the command 'ra list'",
                icon=ICON_APP
            )

    def is_radio_in_json(self, url, name):
        for radio in self.radio_list:
            if (radio["name"] == name or radio["url"] == url):
                return False
        return True

    def is_youtube_live_channel(self, url):
        try:
            with request.urlopen(url) as response:
                if response.getcode() != 200:
                    return False

                page_content = response.read().decode('utf-8')
                is_live_pattern = r'"isLive"\s*:\s*true'
                if re.search(is_live_pattern, page_content):
                    return True
                else:
                    return False

        except Exception:
            return False

    def is_stream_available(self, url):
        stream = self.get_best_stream(url)
        if (stream is None):
            return False
        return True

    def get_best_stream(self, url):
        session = Streamlink()
        session.set_option("stream-timeout", 30)
        available_streams = session.streams(url)
        if "best" in available_streams:
            return available_streams["best"]
        return None

    def start_new_stream(self, url):
        while (self.vlc_player.find_process()):
            self.vlc_player.kill_process()
        self.start_stream(url)

    def play_pause_stream(self, url):
        if self.vlc_player.find_process():
            if self.vlc_player.is_playing():
                self.vlc_player.pause()
            else:
                self.vlc_player.play()
        else:
            self.start_stream(url)

    def start_stream(self, url):
        stream = self.get_best_stream(url)
        self.vlc_player.execute_new_process(stream)
        self.set_last_played_radio(url)

    def save_radio_to_json(self, name, url):
        stream = {'name': name, 'url': url, 'last_played': False}
        with open(JSON_SETTINGS, "w") as file:
            self.radio_list.append(stream)
            file.seek(0)
            json.dump(self.radio_list, file, indent=4)

    def delete_radio_from_json(self, url):
        index = None
        for i, radio in enumerate(self.radio_list):
            if url and radio.get("url") == url:
                index = i
                break

        if index is not None:
            with open(JSON_SETTINGS, "w") as file:
                self.radio_list.pop(index)
                file.seek(0)
                json.dump(self.radio_list, file, indent=4)

    def get_last_played_radio(self):
        last_played_radio = None
        for radio in self.radio_list:
            if radio["last_played"]:
                last_played_radio = radio
                break
        return last_played_radio

    def set_last_played_radio(self, url):
        for radio in self.radio_list:
            if radio["url"] == url:
                radio["last_played"] = True
            else:
                radio["last_played"] = False

        with open(JSON_SETTINGS, "w") as file:
            file.seek(0)
            json.dump(self.radio_list, file, indent=4)

    def query(self, query):
        self.results(query)