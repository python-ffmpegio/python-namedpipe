import subprocess as sp
from namedpipe import NPopen


def run_ffmpeg(pipe):
    sz = [320, 240]
    return (
        sp.Popen(
            # fmt:off
            [
            "ffmpeg",
            "-y",
            "-f", "lavfi",
            "-i", f"testsrc=s={sz[0]}x{sz[1]}:d=5",
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            f'{pipe}',
            ]
            # fmt:on
        ),
        sz[0] * sz[1] * 3,
    )


def test_read_all():
    with NPopen("r") as pipe:
        proc, nbytes = run_ffmpeg(pipe)
        f = pipe.wait()
        while f.read(nbytes):
            pass
    proc.wait()


def test_read_some():
    with NPopen("r") as pipe:
        proc, nbytes = run_ffmpeg(pipe)
        f = pipe.wait()
        for i in range(30):
            f.read(nbytes)
        proc.kill()

if __name__=='__main__':
    test_read_all()