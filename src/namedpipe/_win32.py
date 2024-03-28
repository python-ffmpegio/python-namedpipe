import win32pipe, win32file, win32api, winerror, win32con, pywintypes
from os import path
import io
from typing import TypeVar, NewType, Literal, IO, Optional, Union

WritableBuffer = TypeVar("WritableBuffer")
PyHANDLE = NewType("PyHANDLE", int)

id = 0


def _name_pipe():
    global id

    notok = True
    while notok:
        name = rf"\\.\pipe\{id}"
        id += 1
        notok = path.exists(name)

    return name


def _win_error(code=None):
    if not code:
        code = win32api.GetLastError()
    return OSError(
        f"[OS Error {code}] {win32api.FormatMessage(win32con.FORMAT_MESSAGE_FROM_SYSTEM,0,code,0,None)}"
    )


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
        if bufsize is None:
            bufsize = -1  # Restore default
        if not isinstance(bufsize, int):
            raise TypeError("bufsize must be an integer")

        self.stream: Union[IO, None] = None  # I/O stream of the pipe
        self._path = _name_pipe() if name is None else rf"\\.\pipe\{name}"
        self._rd = any(c in mode for c in "r+")
        self._wr = any(c in mode for c in "wax+")

        if encoding or errors or newline:
            if "b" in mode:
                raise ValueError(
                    "Cannot disambiguate when mode includes 't' and "
                    "and encoding or errors or newline is supplied."
                )
            txt_mode = True
        else:
            txt_mode = "t" in mode

        self._txt = (
            {
                "encoding": encoding,
                "errors": errors,
                "newline": newline,
                "line_buffering": bufsize == 1,
                "write_through": self._wr,
            }
            if txt_mode
            else None
        )

        self._bufsize = -1 if txt_mode and bufsize == 1 else bufsize

        if self._rd and self._wr:
            access = win32pipe.PIPE_ACCESS_DUPLEX
        elif self._rd:
            access = win32pipe.PIPE_ACCESS_INBOUND
        elif self._wr:
            access = win32pipe.PIPE_ACCESS_OUTBOUND
        else:
            raise ValueError("Invalid mode")
        # TODO: assess options: FILE_FLAG_WRITE_THROUGH, FILE_FLAG_OVERLAPPED, FILE_FLAG_FIRST_PIPE_INSTANCE

        pipe_mode = (
            win32pipe.PIPE_TYPE_BYTE
            | win32pipe.PIPE_READMODE_BYTE
            | win32pipe.PIPE_WAIT
        )
        # TODO: assess options: PIPE_WAIT, PIPE_NOWAIT, PIPE_ACCEPT_REMOTE_CLIENTS, PIPE_REJECT_REMOTE_CLIENTS

        max_instances = win32pipe.PIPE_UNLIMITED_INSTANCES  # 1
        buffer_size = 0
        timeout = 0

        # "open" named pipe
        self._pipe = win32pipe.CreateNamedPipe(
            self._path,
            access,
            pipe_mode,
            max_instances,
            buffer_size,
            buffer_size,
            timeout,
            None,
        )
        if self._pipe == win32file.INVALID_HANDLE_VALUE:
            raise _win_error()

    @property
    def path(self):
        """str: path of the pipe in the file system"""
        return self._path

    def __str__(self):
        # return the path
        return self._path

    def close(self):
        # close named pipe
        if self.stream:
            self.stream.close()
            self.stream = None
        if self._pipe:
            if win32file.CloseHandle(self._pipe):
                raise _win_error()
            self._pipe = None

    def wait(self):

        if not self._pipe:
            raise RuntimeError("pipe has already been closed.")

        # wait for the pipe to open (the other end to be opened) and return fileobj to read/write
        if win32pipe.ConnectNamedPipe(self._pipe, None):
            raise _win_error()

        # create new io stream object
        stream = Win32RawIO(self._pipe, self._rd, self._wr)

        if self._bufsize:
            Wrapper = (
                io.BufferedRandom
                if self._rd and self._wr
                else io.BufferedReader if self._rd else io.BufferedWriter
            )
            stream = Wrapper(
                stream, self._bufsize if self._bufsize > 0 else io.DEFAULT_BUFFER_SIZE
            )

        if self._txt is not None:
            stream = io.TextIOWrapper(stream, **self._txt)

        self.stream = stream
        return stream

    def __bool__(self):
        return self.stream is not None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class Win32RawIO(io.RawIOBase):
    """Raw I/O stream layer over open Windows pipe handle.

    `handle` is an open ``pywintypes.PyHANDLE`` object (from ``pywin32`` package) to
    be wrapped by this class.

    Specify the read and write modes by boolean flags: ``rd`` and ``wr``.
    """

    def __init__(self, handle: PyHANDLE, rd: bool, wr: bool) -> None:
        super().__init__()
        self.handle = handle  # PyHANDLE: Underlying Windows handle.
        self._readable: bool = rd
        self._writable: bool = wr

    def readable(self) -> bool:
        """True if file was opened in a read mode."""
        return self._readable

    def seekable(self) -> bool:
        """Always returns False (pipes are not seekable)."""
        return False

    def writable(self) -> bool:
        """True if file was opened in a write mode."""
        return self._writable

    def close(self) -> None:
        """Close the pipe.

        A closed pipe cannot be used for further I/O operations. ``close()`` may
        be called more than once without error."""
        if self.closed:
            return
        if self.handle:
            win32file.CloseHandle(self.handle)
            self.handle = None

        super().close()

    def readinto(self, b: WritableBuffer) -> Union[int, None]:
        """Read bytes into a pre-allocated, writable bytes-like object ``b`` and
        return the number of bytes read. For example, ``b`` might be a ``bytearray``."""

        assert self.handle is not None  # show type checkers we already checked
        assert self._readable

        size = len(b)
        nread = 0
        while nread < size:
            try:
                hr, res = win32file.ReadFile(self.handle, size - nread)
                if hr in (winerror.ERROR_MORE_DATA, winerror.ERROR_IO_PENDING):
                    raise _win_error(hr)
            except pywintypes.error:
                if win32api.GetLastError() == winerror.ERROR_BROKEN_PIPE:
                    break
                raise
            if not len(res):
                break
            nnext = nread + len(res)
            b[nread:nnext] = res
            nread = nnext
        return nread

    def write(self, b):
        """Write buffer ``b`` to file, return number of bytes written.

        Only makes one system call, so not all of the data may be written.
        The number of bytes actually written is returned."""

        assert self.handle is not None  # show type checkers we already checked
        assert self._writable
        hr, n_written = win32file.WriteFile(self.handle, b)
        if hr:
            raise _win_error(hr)
        return n_written
