# turbo-potato

Compress videos to a specific file size on Windows so that they can be uploaded using the Discord free tier.

## Usage

`turbo-potato` is a python script that is executed by running the following command in your terminal:

```
turbo-potato.exe
```

You will then be prompted for the path to the file you would like to compress:

```
Enter the path to the video: "C:\path\to\video.mp4"
```

And then you will be asked for the name you would like the resulting mp4 video to have:

```
(Optional) Enter the name you want the resulting video to have: awesome_clip.mp4
```

If you don't care what the name is, you can just press enter and a name will be provided for you.

The input video will then be processed and placed in a temporary directory. The path to the result will be copied into
your clipboard:

```
The video output path has been written to you clipboard (C:\Users\rpecka\AppData\Local\Temp\tmpcmf2g8b5\awesome_clip.mp4)
Press enter when you are done. This will delete the compressed version...
```

To prevent excess disk usage, the script will wait for you to press enter before exiting. When it exits, the compressed
version of your video will be deleted.

If you want to upload the clip to Discord, before pressing enter to close the script, you can double-click the plus sign
in the message bar and paste the path to the clip into the File Explorer window.

## Installation

### Install `ffmpeg` and add it to your `%PATH%`

You can check if this is already done by typing `where ffmpeg` into the Command Prompt. If it shows a path then you
can continue to the next step.

If you don't have it then you can download it by going to the [FFmpeg downloads page](https://ffmpeg.org/download.html)
and downloading it from the `Get packages & executable files` section.

### Install the project from pypi

```
pip install turbo-potato
```

## How it Works

The script uses the Two-Pass rate control mode of the `ffmpeg` H.264 encoder. You can read about it
[here](https://trac.ffmpeg.org/wiki/Encode/H.264#twopass).

It pins the output file size by dividing the target size in kilobits by the clip length in seconds to determine the
bitrate in kilobits/second. It also subtracts the desired audio bitrate from this value so that the clip has space
for the audio.
