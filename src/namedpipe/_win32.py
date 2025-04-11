import ctypes
from ctypes import wintypes
from os import path
import io
from typing import TypeVar, NewType, Literal, IO, Optional, Union

WritableBuffer = TypeVar("WritableBuffer")
PyHANDLE = NewType("PyHANDLE", int)

# Define global constants
PIPE_ACCESS_DUPLEX = 0x00000003
PIPE_ACCESS_INBOUND = 0x00000001
PIPE_ACCESS_OUTBOUND = 0x00000002
PIPE_TYPE_BYTE = 0x00000000
PIPE_READMODE_BYTE = 0x00000000
PIPE_WAIT = 0x00000000
PIPE_UNLIMITED_INSTANCES = 0xFFFFFFFF
ERROR_PIPE_CONNECTED = 535
ERROR_BROKEN_PIPE = 109
ERROR_MORE_DATA = 234
ERROR_IO_PENDING = 997
FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000
INVALID_HANDLE_VALUE = -1

id = 0

def _wt(value: int) -> wintypes.DWORD:
    return wintypes.DWORD(value)

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
        code = ctypes.get_last_error()
    return ctypes.WinError(code)

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

        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
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
            access = _wt(PIPE_ACCESS_DUPLEX)
        elif self._rd:
            access = _wt(PIPE_ACCESS_INBOUND)
        elif self._wr:
            access = _wt(PIPE_ACCESS_OUTBOUND)
        else:
            raise ValueError("Invalid mode")
        # TODO: assess options: FILE_FLAG_WRITE_THROUGH, FILE_FLAG_OVERLAPPED, FILE_FLAG_FIRST_PIPE_INSTANCE
        pipe_mode = _wt(PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT)

        # TODO: assess options: PIPE_WAIT, PIPE_NOWAIT, PIPE_ACCEPT_REMOTE_CLIENTS, PIPE_REJECT_REMOTE_CLIENTS

        max_instances = _wt(1) # PIPE_UNLIMITED_INSTANCES returns 'invalid params'. Pipes are point-to-point anyway
        buffer_size = _wt(0)
        timeout = _wt(0)

        # "open" named pipe
        h = self.kernel32.CreateNamedPipeW(
            self._path,
            access,
            pipe_mode,
            max_instances,
            buffer_size,
            buffer_size,
            timeout,
            None,
        )
        if h == INVALID_HANDLE_VALUE:
            raise _win_error()
        self._pipe = h

    @property
    def path(self):
        """str: path of the pipe in the file system"""
        return self._path

    def __str__(self):
        return self._path

    def close(self):
        """Close the named pipe.
        A closed pipe cannot be used for further I/O operations. `close()` may
        be called more than once without error.
        """
        if self.stream is not None:
            self.stream.close()
            self.stream = None
        if self._pipe is not None:
            self.kernel32.CloseHandle(self._pipe)
            self._pipe = None

    def wait(self):
        """Wait for the pipe to open (the other end to be opened) and return file object to read/write."""
        if not self._pipe:
            raise RuntimeError("pipe has already been closed.")
        if not self.kernel32.ConnectNamedPipe(self._pipe, None):
            code = ctypes.get_last_error()
            if code != ERROR_PIPE_CONNECTED: # (ok, just indicating that the client has already connected)(Issue#3)
                raise _win_error(code)

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
        return False

    def readable(self) -> bool:
        """True if pipe's stream is readable"""
        return self._rd

    def writable(self) -> bool:
        """True if pipe's stream is writable"""
        return self._wr


class Win32RawIO(io.RawIOBase):
    """Raw I/O stream layer over open Windows pipe handle.

    `handle` is an open Windows ``HANDLE`` object (from ``ctype`` package) to
    be wrapped by this class.

    Specify the read and write modes by boolean flags: ``rd`` and ``wr``.
    """

    def __init__(self, handle: PyHANDLE, rd: bool, wr: bool) -> None:
        super().__init__()
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        self.handle = handle  # Underlying Windows handle.
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
        if self.handle is not None:
            self.kernel32.CloseHandle(self.handle)
            self.handle = None

        super().close()

    def readinto(self, b: WritableBuffer) -> Union[int, None]:
        """Read bytes into a pre-allocated, writable bytes-like object ``b`` and
        return the number of bytes read. For example, ``b`` might be a ``bytearray``."""

        assert self.handle is not None  # show type checkers we already checked
        assert self._readable

        size = len(b)
        nread =  _wt(0)
        buf = (ctypes.c_char * size).from_buffer(b)

        success = self.kernel32.ReadFile(self.handle, buf, size, ctypes.byref(nread), None)
        if not success:
            code = ctypes.get_last_error()
            # ERROR_MORE_DATA - not big deal, will read next time
            # ERROR_IO_PENDING - should not happen, unless use OVERLAPPING, which we don't so far
            # ERROR_BROKEN_PIPE - pipe was closed from other end. While it is an error, test seemingly expects to receive 0 instead of exception
            if code not in (ERROR_MORE_DATA, ERROR_IO_PENDING, ERROR_BROKEN_PIPE):
                raise _win_error(code)

        return nread.value

    def write(self, b):
        """Write buffer ``b`` to file, return number of bytes written.

        Only makes one system call, so not all of the data may be written.
        The number of bytes actually written is returned."""

        assert self.handle is not None  # show type checkers we already checked
        assert self._writable
        size = len(b)
        nwritten = _wt(0)
        buf = (ctypes.c_char * size).from_buffer_copy(b)
        if not self.kernel32.WriteFile(self.handle, buf, _wt(size), ctypes.byref(nwritten), None):
            raise _win_error()

        return nwritten.value
