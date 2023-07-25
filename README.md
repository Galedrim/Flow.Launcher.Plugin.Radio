# Flow.Launcher.Plugin.Radio

A Flow Launcher plugin to search and play Youtube Radio on a VLC instance in the background

:warning: **VLC must be installed in**: ```C:\Program Files\VideoLAN\VLC\vlc.exe``` :warning:

![image](https://github.com/Galedrim/Flow.Launcher.Plugin.Radio/assets/84284891/cd4a8bf7-9638-464f-9905-bc02f2522494)

## Requirements

You'll need Python 3.8 or later installed on your system to use Python plugins within Flow-Launcher. You also may need to select your Python installation directory in the Flow Launcher settings. As of v1.8, Flow Launcher should take care of the installation of Python for you if it is not on your system.

## Installing
The Plugin has been officially added to the supported list of plugins. 
Run the command  ``` pm install radio``` to install it.

You can also manually add it.

## Manual
Add the plugins folder to %APPDATA%\Roaming\FlowLauncher\Plugins\ and run the Flow command ```restart Flow Launcher```.

## Python Package Requirements
This plugin automatically packs the required packages during release so for regular usage in Flow, no additional actions are needed.

If you would like to install the packages manually:

This plugin depends on the Python flow-launcher package.

Without this package installed in your Python environment, the plugin won't work!

The easiest way to install it is to open a CLI like Powershell, navigate into the plugins folder, and run the following command:

``` pip install -r requirements.txt -t ./lib ```

## Usage

| Keyword                            | Description                                                                      |
| ---------------------------------- | -----------------------------                                                    |
| `` ra ``                           | Show currently playing Youtube stream  (or last played if not currently playing) |
| `` ra list ``                      | Search Youtube Stream registered                                                 |
| `` ra add {name} {url} ``          | Register a Youtube Stream with a specific name                                   |
| `` ra rem {name or url} ``         | Unregister a Youtube Stream by his name or URL                                   |
| `` ra reco ``                      | Force a reconnection to the VLC Player                                           |
