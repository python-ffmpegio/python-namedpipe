import time
import win32pipe, win32file
import numpy as np
import subprocess as sp

print("pipe server")
count = 0
pipe = win32pipe.CreateNamedPipe(
    r"\\.\pipe\Foo",
    win32pipe.PIPE_ACCESS_DUPLEX,
    win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE | win32pipe.PIPE_WAIT,
    1,
    65536,
    65536,
    0,
    None,
)

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
        r"\\.\pipe\Foo",
        "-pix_fmt",
        "yuv420p",
        "output.mp4",
    ]
)


try:
    print("waiting for client")
    win32pipe.ConnectNamedPipe(pipe, None)
    print("got client")

    for i in range(30):
        print(f"writing message {i}")
        F = np.random.randint(0, 255, [320, 480, 3], np.uint8)
        win32file.WriteFile(pipe, F)
    print("finished now")
finally:
    win32file.CloseHandle(pipe)

proc.wait()

sp.run(["ffprobe", "output.mp4"])
