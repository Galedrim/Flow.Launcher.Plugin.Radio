import socket
import subprocess

class VLCPlayer():
    def __init__(self):
        self.APP_NAME = 'vlc.exe'
        self.DEFAULT_APP_PATH = 'C:\\Program Files\\VideoLAN\\VLC\\'+self.APP_NAME
        self.HOST = '127.0.0.1'
        self.PORT = 44500

        self.MAX_VOL = 512
        self.MIN_VOL = 0
        self.VOL_STEP = 32


    def find_process(self):
        cmd = subprocess.run(
            ['tasklist', '/FI', f'ImageName eq {self.APP_NAME}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW)
        return (cmd.returncode == 0 and self.APP_NAME in cmd.stdout)
    
    def execute_new_process(self, stream):
        # Start a new detached process with the specified screen name and VLC command
        cmd = subprocess.Popen([
            self.DEFAULT_APP_PATH,"-I", "rc", "--rc-host", f"{self.HOST}:{self.PORT}", "--no-video", "--rc-quiet", stream.url
        ])

    def kill_process(self):
        cmd = subprocess.run(['taskkill', '/IM', self.APP_NAME, '/F'], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return (cmd.returncode == 0)

    def send_command(self, msg: str, full=False):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # Connect to server and send data
                sock.settimeout(0.7)
                sock.connect((self.HOST, self.PORT))
                response = ""
                received = ""
                sock.sendall(bytes(msg + '\n', "utf-8"))
                try:
                    while (True):
                        received = (sock.recv(1024)).decode()
                        response = response + received
                        if full:
                            b = response.count("\r\n")
                            if response.count("\r\n") > 1:
                                sock.close()
                                break
                        else:
                            if response.count("\r\n") > 0:
                                sock.close()
                                break
                except:
                    response = response + received
                    pass
                sock.close()
                return response
        except:
            return None

    def is_playing(self):
        return self.send_command('is_playing')

    def play(self):
        self.send_command('play')

    def pause(self):
        self.send_command('pause')

    def set_volume(self, level):
        self.send_command("volume " + str(level))

    def volume_up(self):
        print("volume_up")
        self.send_command("volup " + str(self.VOL_STEP))
    
    def volume_down(self):
        self.send_command("voldown " + str(self.VOL_STEP))