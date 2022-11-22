import os
import numpy as np
import subprocess as sp

print("pipe server")
count = 0
pipe = os.mkfifo("Foo")

proc = sp.Popen(
    [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        "480x320",
        "-r",
        "30",
        "-i",
        "Foo",
        "-pix_fmt",
        "yuv420p",
        "output.mp4",
    ]
)

with open("Foo", "wb") as f:

    for i in range(30):
        print(f"writing message {i}")
        F = np.random.randint(0, 255, [320, 480, 3], np.uint8)
        f.write(F)
        print("finished now")

proc.wait()

os.unlink('Foo')

sp.run(["ffprobe", "output.mp4"])
