from stream import is_youtube_stream, get_best_stream
from flox import Flox
from channels import Channels
from player import DEFAULT_VLC_DIR, VLCPlayer

ICON_APP = "./Images/app.png"
ICON_UNAVAILABLE = "./Images/app-grayscale.png"
ICON_SETTINGS = "./Images/settings.png"

JSON_SETTINGS = "./Plugin/settings.json"

class Radio(Flox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.vlc_player = VLCPlayer(str(DEFAULT_VLC_DIR))
        self.channels_manager = Channels()

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
    

    def process_default_command(self):
        last_channel = self.channels_manager.get_last_played_channel()
        if last_channel:
            name = last_channel["name"]
            url = last_channel["url"]
            if(get_best_stream(url)):
                self.add_item(
                    title="Play/Pause: {0}".format(name),
                    subtitle=url,
                    icon=ICON_APP,
                    method=self.play_pause_stream,
                    parameters=[url]
                )
            else:
                self.add_item(
                    title="Unavailable: {0}".format(name),
                    subtitle=url,
                    icon=ICON_UNAVAILABLE
                )
        else:
            self.add_item(
                title="Select a radio with the command 'ra list'",
                icon=ICON_APP,
            )
    
    def process_list_command(self, args):
        channels = self.channels_manager.channel_list
        for channel in channels:
            name = channel["name"]
            url = channel["url"]

            if args and not any(arg.lower() in name.lower() for arg in args):
                continue

            if get_best_stream(url):
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
            is_channel_existed = self.channels_manager.is_existing_channel(name, url)

            if is_channel_existed and is_youtube_stream(url):
                self.add_item(
                    title="Add {0} {1}".format(name, url),
                    subtitle="Add an URL stream with associated name",
                    icon=ICON_SETTINGS,
                    method=self.save_channel,
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
            channels = self.channels_manager.channel_list
            for chaine in channels:
                url = chaine["url"]
                name = chaine["name"]
                arg = str(args[0])
                if arg.lower() in url.lower() or arg.lower() in name.lower():
                    self.add_item(
                        title="Rem: {0} - {1}".format(name, url),
                        subtitle="Remove an URL stream with associated name",
                        icon=ICON_SETTINGS,
                        method=self.remove_channel,
                        parameters=[url]
                    )

    def process_reconnect_command(self):
        last_channel = self.channels_manager.get_last_played_channel()
        if last_channel and get_best_stream(last_channel["url"]):
            name = last_channel["name"]
            url = last_channel["url"]
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


    def start_new_stream(self, url):
        while (self.vlc_player.find_process()):
            self.vlc_player.kill_process()
        self.start_stream(url)

    def play_pause_stream(self, url):
        if self.vlc_player.find_process():
            self.vlc_player.pause_resume()
        else:
            self.start_stream(url)

    def start_stream(self, url):
        self.vlc_player.execute_new_process(get_best_stream(url))
        self.channels_manager.set_last_played_radio(url)

    def save_channel(self, url, name):
        self.channels_manager.add_channel(url,name)
    
    def remove_channel(self, url):
        self.channels_manager.delete_channel(url)

    def query(self, query):
        self.results(query)