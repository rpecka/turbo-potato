import argparse
import pathlib
import subprocess
import tempfile
import tkinter


TARGET_FILE_SIZE_kb = 8 * 8 * 1000  # 8MB * 8b/B * 1000 kb/Mb
AUDIO_BITRATE_kbPS = 128
MARGIN = 0.98

class Options:
    def __init__(self, output_name, max_fps):
        self.output_name = output_name
        self.max_fps = max_fps


class Attributes:
    def __init__(self, duration_seconds, fps):
        self.duration_seconds = duration_seconds
        self.fps = fps

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
    bitrate = int(TARGET_FILE_SIZE_kb / attributes.duration_seconds * MARGIN) - AUDIO_BITRATE_kbPS
    base_command = ["ffmpeg", "-y", "-i", input_path, "-c:v", "libx264", "-b:v", f"{bitrate}k"]
    if options.max_fps is not None and options.max_fps < attributes.fps:
        base_command.extend(["-filter:v", f"fps=fps={options.max_fps}"])
    subprocess.check_call(base_command + ["-pass", "1", "-an", "-f", "null", "NUL"], cwd=working_directory)
    subprocess.check_call(base_command + ["-pass", "2", "-c:a", "aac", "-b:a", f"{AUDIO_BITRATE_kbPS}k", output_path], cwd=working_directory)

def get_input_attributes(input_path):
    entries_string = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "0", "-show_entries", "format=duration:stream=r_frame_rate",
         "-of", "default=noprint_wrappers=1", input_path]).decode()
    entries_list = entries_string.strip().splitlines()
    entries = {}
    for entry in entries_list:
        keyval = entry.split('=')
        entries[keyval[0]] = keyval[1]
    duration_seconds = float(entries["duration"])
    fps_fraction = entries["r_frame_rate"].split('/')
    fps = float(fps_fraction[0])/float(fps_fraction[1])
    return Attributes(duration_seconds, fps)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="the file to read the video from")
    parser.add_argument("--name", help="the the name of the resulting mp4 file")
    parser.add_argument("--max-fps", type=int, help="reduce the output's frame rate to the given value if it exceeds it")

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

    options = Options(output_name, args.max_fps)

    compress(input_path, options)


if __name__ == '__main__':
    main()
