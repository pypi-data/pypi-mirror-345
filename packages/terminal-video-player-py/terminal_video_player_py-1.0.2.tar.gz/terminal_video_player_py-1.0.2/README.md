# Terminal Video Player (tvp)

This Command Line Interface Tool can be used to play videos in the terminal.

## Installation

`pip install terminal-video-player-py`

## Usage

### Video Playback

`tvp [-h] [-a] [-c] [-chars CHARACTERS] [-rt] video_path downscale`

To play a video, you can simply call `tvp <video_path> <downscale> [optional arguments]`.

Example:
``` bash
tvp <path> 8 -a -rt
```
This will play the video in real time and downscaled 8 times. It will also playback the video's audio.

## Arguments

| Argument  | Description |
| ------------- | ------------- |
| **-h, --help**  | Show help information about the CLI  |
| **-a, --audio**  | Play video audio  |
| **-c, --colored**  | Set the output to be colored(may not work on some terminals)  |
| **-chars string, --characters string**  | Custom characters(low density to high)  |
| **-rt, --realtime**  | Play the video in real time  |

## Uninstall

`pip uninstall terminal-video-player-py`
