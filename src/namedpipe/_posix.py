import os, tempfile
from os import path
from typing import IO, Optional, Union
try:
    from typing import Literal  # type: ignore
except ImportError:
    from typing_extensions import Literal


class _FifoMan:

    __instance = None
    __inited = False

    def __new__(cls) -> "_FifoMan":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        if type(self).__inited:
            return
        type(self).__inited = True

        self.tempdir = None
        self.id = 0
        self.active = 0  # if zero, no tempdir

    def make(self, name):
        in_dir = not (name and path.isabs(name))
        if in_dir:
            if not self.tempdir:
                self.tempdir = tempfile.mkdtemp(prefix="pipe", suffix="")
            name = path.join(self.tempdir, str(self.id))
        try:
            os.mkfifo(name)
        except:
            if in_dir and not self.active:
                os.rmdir(self.tempdir)
            raise

        if in_dir:
            # if success, update the counter
            self.id += 1
            self.active += 1

        return name

    def unlink(self, name):
        os.unlink(name)
        if self.tempdir and name.startswith(self.tempdir):
            self.active -= 1
            if not self.active:
                os.rmdir(self.tempdir)
                self.tempdir = None


class NPopen:
    def __init__(
        self,
        mode: Optional[str] = "r",
        bufsize: Optional[int] = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[Literal["", "\n", "\r", "\r\n"]] = None,
        name: Optional[str] = None,
    ):
        # "open" named pipe
        self._path = _FifoMan().make(name)
        self.stream: Union[IO, None] = None  # I/O stream of the pipe

        if 't' not in mode and 'b' not in mode:
            mode += 'b' # default to binary mode

        self._open_args = {
            "mode": mode,
            "buffering": bufsize,
            "encoding": encoding,
            "errors": errors,
            "newline": newline,
        }

    @property
    def path(self):
        return self._path

    def __str__(self):
        # return the path
        return self._path

    def close(self):
        # close named pipe
        if self.stream:
            self.stream.close()
            self.stream = None
        if path.exists(self._path):
            _FifoMan().unlink(self._path)

    def wait(self):

        if self._path is None:
            raise RuntimeError("pipe has already been closed.")

        # wait for the pipe to open (the other end to be opened) and return fileobj to read/write
        self.stream = open(self._path, **self._open_args)
        return self.stream

    def __bool__(self):
        return self.stream is not None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
