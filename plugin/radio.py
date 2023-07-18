from flox import Flox, ICON_SETTINGS
from player import VLCPlayer

import streamlink
import json
import os

ICON_APP = "./Images/app.png"
ICON_APP_GRAYSCALE = "./Images/app-grayscale.png"
JSON_SETTINGS = "./Plugin/settings.json"

class Radio(Flox):

    def __init__(self, lib=None, **kwargs):
        super().__init__(lib=lib, **kwargs)
        
        self.stream_list = []
        if os.path.exists(JSON_SETTINGS):
            with open(JSON_SETTINGS, "r") as file:
                data = json.load(file)
                self.stream_list = sorted(data, key=lambda x: x["name"])
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
        elif command in "remove":
            self.process_remove_command(args[1:])
        elif command in "volume":
            self.process_volume_command(args[1:])
        else:
            self.process_default_command()

        # DEBUG
        # self.get_stream("https://www.youtube.com/watch?v=5yx6BWlEVcY")
        # self.process_volume_command("+")

        return self._results


    def process_list_command(self, args):
        for stream in self.stream_list:
            name = stream["name"]
            url = stream["url"]

            if args and not any(arg.lower() in name.lower() for arg in args):
                        continue

            stream_data = self.get_stream(url)
            if stream_data:
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
                    icon=ICON_APP_GRAYSCALE
                )

    def process_add_command(self, args):
        if len(args) == 1:
            self.add_item(
                title="Add {0} [URL]".format(args[1]),
                subtitle="Add an URL stream with associated name", 
                icon=ICON_SETTINGS
            )
        elif len(args) == 2 and self.check_stream_name(args[0]) and self.check_stream_url(args[1]):
            self.add_item(
                title="Add {0} - {1}".format(args[0], args[1]),
                subtitle="Add an URL stream with associated name",
                icon=ICON_SETTINGS,
                method=self.save_stream,
                parameters=args
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
                title="Remove [NAME] or [URL]",
                subtitle="Remove an URL stream with associated name",
                icon=ICON_SETTINGS
            )
        else:
            for stream in self.stream_list:
                if str(args[0]).lower() in stream["name"].lower() or str(args[0]).lower() in stream["url"].lower():
                    self.add_item(
                        title="Remove: {0} - {1}".format(stream["name"], stream["url"]),
                        subtitle="Remove an URL stream with associated name",
                        icon=ICON_SETTINGS,
                        method=self.delete_stream,
                        parameters=[stream["url"]]
                    )

    def process_volume_command(self, args):
        if(len(args) == 1):
            result = True
            if(args[0].isdigit() and self.vlc_player.MIN_VOL < int(args[0]) < self.vlc_player.MAX_VOL):
                subtitle = "Set the volume stream to {0}".format(args[0])
            elif(args[0] == "+"):
                subtitle = "Turn up the volume"
            elif(args[0] == "-"):
                subtitle = "Turn down the volume"
            else:
                result = False

            if(result):
                self.add_item(
                    title="Volume {0} ".format(args[0]),
                    subtitle=subtitle,
                    icon=ICON_SETTINGS,
                    method=self.set_volume_stream,
                    parameters=[args[0]]
                )
        else:
            self.add_item(
                title="Volume [1-512] or [+/-]",
                subtitle="Set the volume stream with absolute or relative value",
                icon=ICON_SETTINGS
            )

    def process_default_command(self):
            last_stream = self.get_last_played_stream()
            if last_stream:
                self.add_item(
                    title="Play/Pause: {0}".format(last_stream["name"]),
                    subtitle=last_stream["url"],
                    icon=ICON_APP,
                    method=self.play_pause_stream,
                    parameters=[last_stream["url"]],
                    score=1
                )


    def check_stream_name(self, name):
        for stream in self.stream_list:
            if(stream["name"] == name):
                return False
        return True
    
    def check_stream_url(self, url):  
        for stream in self.stream_list:
            if(stream["url"] == url):
                return False

        stream = self.get_stream(url)
        if(stream is None):
            return False

        return True

    def get_stream(self, url):
        stream = None
        available_streams = streamlink.streams(url)
        if "best" in available_streams:
            stream = available_streams["best"]
        return stream


    def start_new_stream(self, url):
        while(self.vlc_player.find_process()):
            self.vlc_player.kill_process()

        stream = self.get_stream(url)
        self.vlc_player.execute_new_process(stream)
        self.set_last_played_stream(url)

    def play_pause_stream(self, url):
        if self.vlc_player.find_process():
            self.vlc_player.pause() if self.vlc_player.is_playing else self.vlc_player.play()
        else:
            stream = self.get_stream(url) 
            self.vlc_player.execute_new_process(stream)
            self.set_last_played_stream(url)

    def set_volume_stream(self, level):
        if (level[0].isdigit() and self.vlc_player.MIN_VOL < int(level[0]) < self.vlc_player.MAX_VOL):
            self.vlc_player.set_volume(level)
        elif(level == "+"):
            self.vlc_player.volume_up
        elif(level == "-"):
            self.vlc_player.volume_down

    def save_stream(self, name, url):  
        stream = {'name': name, 'url': url, 'last_played': False}
        with open(JSON_SETTINGS, "w") as file:
            self.stream_list.append(stream)
            file.seek(0)
            json.dump(self.stream_list, file, indent = 4)

    def delete_stream(self, url):
        index = None
        for i, stream in enumerate(self.stream_list):
            if url and stream.get("url") == url:
                index = i
                break

        if index is not None:
            with open(JSON_SETTINGS, "w") as file:
                self.stream_list.pop(index)
                file.seek(0)
                json.dump(self.stream_list, file, indent = 4)


    def get_last_played_stream(self):
        last_played_stream = None
        for stream in self.stream_list:
            if stream["last_played"]:
                last_played_stream = stream
                break
        return last_played_stream
    
    def set_last_played_stream(self, url):
        for stream in self.stream_list:
            if stream["url"] == url:
                stream["last_played"] = True
            else:
                stream["last_played"] = False

        with open(JSON_SETTINGS, "w") as file:
            file.seek(0)
            json.dump(self.stream_list, file, indent = 4)


    def query(self, query):
        self.results(query)