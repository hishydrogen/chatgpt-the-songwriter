"""Export the generated, complete sleeve to exact 3000 px PNG/JPEG files.

source.png is the preserved 1254 px image-generation result. This only changes
delivery dimensions and format; typography and composition are already in it.
"""
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent


def main():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "source.png"),
                    "-vf", "scale=3000:3000:flags=lanczos,format=rgb24",
                    "-frames:v", "1", str(HERE / "cover.png")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "cover.png"),
                    "-q:v", "2", "-frames:v", "1", str(HERE / "cover.jpg")], check=True)
    print("3000 × 3000 PNG and JPEG written from the preserved generated sleeve.")


if __name__ == "__main__":
    main()
