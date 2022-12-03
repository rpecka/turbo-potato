import argparse
import pathlib
import subprocess
import tempfile

TARGET_FILE_SIZE_kb = 8 * 8 * 1000  # 8MB * 8b/B * 1000 kb/Mb
AUDIO_BITRATE_kbPS = 128
MARGIN = 0.98


def compress(input_path, output_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        compress_with_directory(temp_dir, input_path, output_path)


def compress_with_directory(working_directory, input_path, output_path):
    duration_string = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path])
    duration_seconds = float(duration_string)
    bitrate = int(TARGET_FILE_SIZE_kb / duration_seconds * MARGIN) - AUDIO_BITRATE_kbPS
    subprocess.check_call(["ffmpeg", "-y", "-i", input_path, "-c:v", "libx264", "-b:v", f"{bitrate}k", "-pass", "1", "-an", "-f", "null", "garbagefile"], cwd=working_directory)
    subprocess.check_call(["ffmpeg", "-y", "-i", input_path, "-c:v", "libx264", "-b:v", f"{bitrate}k", "-pass", "2", "-c:a", "aac", "-b:a", f"{AUDIO_BITRATE_kbPS}k", output_path], cwd=working_directory)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="the file to read the video from")
    parser.add_argument("--output", help="the path where the resulting file will be written")

    args = parser.parse_args()

    input_path = pathlib.Path(args.input)

    if args.output:
        output_path = pathlib.Path(args.output).with_suffix('.mp4')
    else:
        output_path = pathlib.Path("./output.mp4")

    compress(input_path, output_path)


if __name__ == '__main__':
    main()
