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
            "-f", "lavfi",
            "-i", "testsrc=s=320x240",
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            r"\\.\pipe\Foo",
    ]
)


try:
    print("waiting for client")
    win32pipe.ConnectNamedPipe(pipe, None)
    print("got client")

    nbytes = 320*240*3
    print(f'frame size: {nbytes} bytes')

    for i in range(30):
        print(f"reading frame {i}")
        hr,buf = win32file.ReadFile(pipe, nbytes)
        if hr:
            print('read error')
        else:
            print(f'read {len(buf)} bytes')
    print("finished now")
finally:
    win32file.CloseHandle(pipe)

proc.wait()

sp.run(["ffprobe", "output.mp4"])
