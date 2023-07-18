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

        # DEBUG
        #self.delete_radio("https://www.youtube.com/watch?v=MVPTGNGiI-4")

        if len(args) == 1:
            if(args[0] == ""):
                last_stream = self.get_last_played_stream()
                if(last_stream is not None):
                    self.add_item(
                        title="Play/Pause : {0}".format(last_stream["name"]),
                        subtitle=last_stream["url"],
                        icon=ICON_APP,
                        method = self.play_pause_stream,
                        parameters = [last_stream["url"]],
                        score = 1
                    )
            elif(str(args[0]).lower() in "list"):
                for stream in self.stream_list:
                    stream = self.get_stream(stream["url"])
                    if(stream is not None):
                        self.add_item(
                            title="Start: {0}".format(stream["name"]),
                            subtitle=stream["url"],
                            icon=ICON_APP,
                            method = self.start_new_stream,
                            parameters = [stream["url"]]
                        )
                    else:
                        self.add_item(
                            title="Unavailable: {0}".format(stream["name"]),
                            subtitle=stream["url"],
                            icon=ICON_APP_GRAYSCALE
                        )
            elif(str(args[0]).lower() in "add"):
                self.add_item(
                    title=("Add [NAME] [URL]"),
                    subtitle="Add a new URL stream with associated name",
                    icon=ICON_SETTINGS,
                )
            elif(str(args[0]).lower() in "remove"):
                for stream in self.stream_list:
                    self.add_item(
                        title="Remove: {0} - {1} ".format(stream["name"], stream["url"]),
                        subtitle="Remove an URL stream with associated name", 
                        icon=ICON_SETTINGS,
                    )

            elif(str(args[0]).lower() in "play" or str(args[0]).lower() in "pause"):
                last_stream = self.get_last_played_stream()
                if(last_stream is not None):
                    self.add_item(
                        title="Play/Pause : {0}".format(last_stream["name"]),
                        subtitle=last_stream["url"],
                        icon=ICON_APP,
                        method = self.play_pause_stream,
                        parameters = [last_stream["url"]],
                        score = 1
                    )

        elif len(args) == 2:
            if(str(args[0]).lower() == "list"):
                for stream in self.stream_list:
                    if str(args[1]).lower() in stream["name"].lower():
                        stream = self.get_stream(stream["url"])
                        if(stream is not None):
                            self.add_item(
                                title="Start: {0}".format(stream["name"]),
                                subtitle=stream["url"],
                                icon=ICON_APP,
                                method = self.start_new_stream,
                                parameters = [stream["url"]]
                            )
                        else:
                            self.add_item(
                                title="Unavailable: {0}".format(stream["name"]),
                                subtitle=stream["url"],
                                icon=ICON_APP_GRAYSCALE
                            )

            elif(str(args[0]).lower() == "add"):
                self.add_item(
                    title="Add {0} [URL]".format(args[1]),
                    subtitle="Add an URL stream with associated name", 
                    icon=ICON_SETTINGS
                )
                
            elif(str(args[0]).lower() == "remove"):
                for stream in self.stream_list:
                    if(str(args[1]).lower() in stream["name"].lower() or str(args[1]).lower() in stream["url"].lower()):
                        self.add_item(
                            title="Remove: {0} - {1} ".format(stream["name"], stream["url"]),
                            subtitle="Remove an URL stream with associated name", 
                            icon=ICON_SETTINGS,
                            method = self.delete_stream,
                            parameters = [stream["url"]]
                        )

        elif len(args) == 3:
            if(str(args[0]).lower() == "add" and self.check_stream_name(args[1]) and self.check_radio_stream(args[2])):
                    self.add_item(
                        title="Add {0} - {1}".format(args[1], args[2]),
                        subtitle="Add an URL stream with associated name", 
                        icon=ICON_SETTINGS,
                        method = self.save_stream,
                        parameters = [args[1], args[2]]
                    )
        return self._results
    
    def check_stream_name(self, name):
        for stream in self.stream_list:
            if(stream["name"] == name):
                return False
        return True
    
    def check_radio_stream(self, url):  
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
        print(available_streams)
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
        if(self.vlc_player.find_process()):
            if(self.vlc_player.is_playing):
                self.vlc_player.pause()
            else:
                self.vlc_player.play()
        else:
            stream = self.get_stream(url) 
            self.vlc_player.execute_new_process(stream)
            self.set_last_played_stream(url)

    def save_stream(self, name, url):  
        radio = {'name': name, 'url': url, 'last_played': False}
        with open(JSON_SETTINGS, "w") as file:
            self.stream_list.append(radio)
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