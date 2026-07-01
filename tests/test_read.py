import multiprocessing as mp
import subprocess as sp

import namedpipe as npipe


def worker_npopen_rt(pipe_path, msg):

    with open(pipe_path, "wt") as f:
        f.write(msg)


def test_multiprocessing_read_default():

    # Use 'spawn' context to remain safe across OS platforms (Windows/macOS/Linux)
    ctx = mp.get_context("spawn")

    # Create a named pipe Initialize the process
    msg = "hello reader!!"
    with npipe.NPopen("rt") as pipe:
        p = ctx.Process(target=worker_npopen_rt, args=(pipe.path, msg))
        p.start()
        stream = pipe.wait()
        rmsg = stream.read(len(msg) * 2)
        p.join()

    assert rmsg == msg


def run_ffmpeg(pipe):
    sz = [320, 240]
    return (
        sp.Popen(
            # fmt:off
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"testsrc=s={sz[0]}x{sz[1]}:d=1",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                f"{pipe}",
            ]
            # fmt:on
        ),
        sz[0] * sz[1] * 3,
    )


def test_read_all():
    with npipe.NPopen("r") as pipe:
        assert pipe.readable()
        assert not pipe.writable()
        proc, nbytes = run_ffmpeg(pipe)
        f = pipe.wait()
        while f.read(nbytes):
            pass
    proc.wait()


def test_read_some():
    with npipe.NPopen("r") as pipe:
        proc, nbytes = run_ffmpeg(pipe)
        f = pipe.wait()
        for i in range(30):
            f.read(nbytes)
        proc.kill()


def test_read_too_much():
    with npipe.NPopen("r") as pipe:
        proc, nbytes = run_ffmpeg(pipe)
        f = pipe.wait()
        f.read(nbytes * 100)
        proc.kill()


# if __name__ == "__main__":
#     test_read_all()
