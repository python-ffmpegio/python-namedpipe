import numpy as np
import subprocess as sp
from namedpipe import NPopen
from tempfile import TemporaryDirectory
from os import path


def run_ffmpeg(pipe, dstdir):
    outpath = path.join(dstdir, "output.mp4")
    sz = [320, 240, 3]
    return (
        sp.Popen(
            # fmt:off
            [
            "ffmpeg",
            "-y",
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-s", f"{sz[0]}x{sz[1]}",
            "-r", "30",
            "-i", str(pipe),
            outpath,
            ]
            # fmt:on
        ),
        sz,
        outpath,
    )


def test_write():
    print("pipe server")
    with TemporaryDirectory() as dstdir:
        with NPopen("w") as pipe:

            proc, shape, outpath = run_ffmpeg(pipe, dstdir)
            f = pipe.wait()
            for i in range(30):
                F = np.random.randint(0, 255, shape, np.uint8)
                f.write(F)

        proc.wait()

        sp.run(["ffprobe", outpath])


if __name__ == "__main__":
    test_write()
