import argparse
import os.path
import pathlib
import subprocess
import tempfile
import tkinter

import configfile


MB_to_kb = 8 * 1000  # 8b/B * 1000 kb/Mb
AUDIO_BITRATE_kbPS = 128
MARGIN = 0.98


class Resolution:
    def __init__(self, width, height):
        self.width = width
        self.height = height


RESOLUTION_4K = Resolution(3040, 2160)
RESOLUTION_2K = Resolution(2560, 1440)
RESOLUTION_HD = Resolution(1920, 1080)
RESOLUTION_480 = Resolution(854, 480)
RESOLUTION_360 = Resolution(640, 360)
RESOLUTION_240 = Resolution(426, 240)

RESOLUTION_NAMES = {
    "4K": RESOLUTION_4K,
    "UHD": RESOLUTION_4K,
    "2160p": RESOLUTION_4K,

    "2K": RESOLUTION_2K,
    "1440": RESOLUTION_2K,
    "1440p": RESOLUTION_2K,

    "HD": RESOLUTION_HD,
    "1080": RESOLUTION_HD,
    "1080p": RESOLUTION_HD,

    "480": RESOLUTION_480,
    "408p": RESOLUTION_480,

    "360": RESOLUTION_360,
    "360p": RESOLUTION_360,

    "240": RESOLUTION_240,
    "240p": RESOLUTION_240,
}


class Options:
    def __init__(self, output_name, target_size_megabytes, max_fps, max_resolution):
        self.output_name = output_name
        self.target_size_megabytes = target_size_megabytes
        self.max_fps = max_fps
        self.max_resolution = max_resolution


class Attributes:
    def __init__(self, duration_seconds, fps, width, height):
        self.duration_seconds = duration_seconds
        self.fps = fps
        self.width = width
        self.height = height


def validate_config(config):
    if config.default_max_resolution is not None and not config.default_max_resolution in RESOLUTION_NAMES.keys():
        return f"ERROR: the default max resolution must be one of the available settings: {', '.join(RESOLUTION_NAMES.keys())}"
    return None


def compress(input_path, options):
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = pathlib.Path(temp_dir).joinpath(options.output_name).with_suffix(".mp4")
        compress_with_directory(temp_dir, input_path, output_path, options)

        r = tkinter.Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(str(output_path))

        print(f"The video output path has been written to you clipboard ({output_path})")
        input("Press enter when you are done. This will delete the compressed version...")

        r.destroy()


def compress_with_directory(working_directory, input_path, output_path, options):
    attributes = get_input_attributes(input_path)
    bitrate = int((options.target_size_megabytes * MB_to_kb) / attributes.duration_seconds * MARGIN) - AUDIO_BITRATE_kbPS
    base_command = ["ffmpeg", "-y", "-i", input_path, "-c:v", "libx264", "-b:v", f"{bitrate}k"]

    video_filtergraphs = []
    if (fps_filtergraph := make_fps_filtergraph(attributes, options)) is not None:
        video_filtergraphs.append(fps_filtergraph)
    if (resolution_filtergraph := make_resolution_filtergraph(attributes, options)) is not None:
        video_filtergraphs.append(resolution_filtergraph)

    if len(video_filtergraphs) > 0:
        base_command.extend(["-filter_complex", ",".join(video_filtergraphs)])

    subprocess.check_call(base_command + ["-pass", "1", "-an", "-f", "null", "NUL"], cwd=working_directory)
    subprocess.check_call(base_command + ["-pass", "2", "-c:a", "aac", "-b:a", f"{AUDIO_BITRATE_kbPS}k", output_path], cwd=working_directory)


def get_input_attributes(input_path):
    entries_string = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "0", "-show_entries", "format=duration:stream=r_frame_rate,width,height",
         "-of", "default=noprint_wrappers=1", input_path]).decode()
    entries_list = entries_string.strip().splitlines()
    entries = {}
    for entry in entries_list:
        keyval = entry.split('=')
        entries[keyval[0]] = keyval[1]
    duration_seconds = float(entries["duration"])
    fps_fraction = entries["r_frame_rate"].split('/')
    fps = float(fps_fraction[0])/float(fps_fraction[1])
    width = int(entries["width"])
    height = int(entries["height"])
    return Attributes(duration_seconds, fps, width, height)


def make_fps_filtergraph(attributes, options):
    if options.max_fps is None or options.max_fps >= attributes.fps:
        return None
    return f"fps=fps={options.max_fps}"


def make_resolution_filtergraph(attributes, options):
    if options.max_resolution is None:
        return None
    max_dimension = max(options.max_resolution.width, options.max_resolution.height)
    largest_dimension = max(attributes.width, attributes.height)
    if max_dimension >= largest_dimension:
        return None
    if attributes.width > attributes.height:
        return f"scale={max_dimension}:-1"
    else:
        return f"scale=-1:{max_dimension}"


def main():
    config_path = os.path.expanduser(os.path.join("~", ".turbo-potato-config.ini"))
    config = configfile.Config(config_path)

    if (config_error := validate_config(config)) is not None:
        print(config_error)
        exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="the file to read the video from")
    parser.add_argument("--name", help="the the name of the resulting mp4 file")
    parser.add_argument("--target-size", type=float, help="the target output file size in megabytes. i.e. 8, 50, 500", default=config.default_target_size)
    parser.add_argument("--max-fps", type=int, help="reduce the output's frame rate to the given value if it exceeds it", default=config.default_max_fps)
    parser.add_argument("--max-resolution", help="reduce the output's resolution to the given value if it exceeds it", choices=RESOLUTION_NAMES.keys(), default=config.default_max_resolution)

    args = parser.parse_args()

    if args.input:
        input_path = pathlib.Path(args.input)
    else:
        input_path = pathlib.Path(input("Enter the path to the video: ").strip("\""))

    if args.name:
        output_name = args.name
    else:
        output_name = input("(Optional) Enter the name you want the resulting video to have: ")

    if output_name == "":
        output_name = "output"

    options = Options(output_name, args.target_size, args.max_fps, RESOLUTION_NAMES[args.max_resolution])

    compress(input_path, options)


if __name__ == '__main__':
    main()
