import argparse
import pathlib
import subprocess
import tempfile
import tkinter


TARGET_FILE_SIZE_kb = 8 * 8 * 1000  # 8MB * 8b/B * 1000 kb/Mb
AUDIO_BITRATE_kbPS = 128
MARGIN = 0.98


def compress(input_path, output_name):
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = pathlib.Path(temp_dir).joinpath(output_name).with_suffix(".mp4")
        compress_with_directory(temp_dir, input_path, output_path)

        r = tkinter.Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(str(output_path))

        print(f"The video output path has been written to you clipboard ({output_path})")
        input("Press enter when you are done. This will delete the compressed version...")

        r.destroy()


def compress_with_directory(working_directory, input_path, output_path):
    duration_string = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path])
    duration_seconds = float(duration_string)
    bitrate = int(TARGET_FILE_SIZE_kb / duration_seconds * MARGIN) - AUDIO_BITRATE_kbPS
    base_command = ["ffmpeg", "-y", "-i", input_path, "-c:v", "libx264", "-b:v", f"{bitrate}k"]
    subprocess.check_call(base_command + ["-pass", "1", "-an", "-f", "null", "NUL"], cwd=working_directory)
    subprocess.check_call(base_command + ["-pass", "2", "-c:a", "aac", "-b:a", f"{AUDIO_BITRATE_kbPS}k", output_path], cwd=working_directory)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="the file to read the video from")
    parser.add_argument("--name", help="the the name of the resulting mp4 file")

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

    compress(input_path, output_name)


if __name__ == '__main__':
    main()
