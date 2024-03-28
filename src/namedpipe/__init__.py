__version__ = "0.1.1"

from os import name as _os_name

if _os_name == "nt":
    from ._win32 import NPopen
else:
    from ._posix import NPopen

NPopen.__doc__ = r"""Create a named pipe. 

On POSIX, the class uses py:func:`os.mkfifo()` to create the named pipe. On 
Windows, the class uses the Windows :py:func:`win32pipe.CreateNamedPipe()` 
function of the ``pywin32`` package. The arguments to NPopen are as follows.

``bufsize`` will be supplied as the corresponding argument to the open() function 
when creating the pipe file objects:

* ``0`` means unbuffered (read and write are one system call and can return short)
* ``1`` means line buffered (only usable in a text mode)
* any other positive value means use a buffer of approximately that size
* negative ``bufsize`` (the default) means the system default of 
  ``io.DEFAULT_BUFFER_SIZE`` will be used.

If ``encoding`` or ``errors`` are specified, or `mode` contains `t`, the file 
objects ``NPopen.stream`` will be opened in text mode with the specified 
``encoding`` and as described below.

``encoding`` gives the name of the encoding that the stream will be decoded or 
encoded with. It defaults to ``locale.getencoding()``. ``encoding="locale"`` can 
be used to specify the current locale’s encoding explicitly. See `Text Encoding 
<https://docs.python.org/3/library/io.html#io-text-encoding>`_ in Python's 
Standard Library documentation for more information.

``errors`` is an optional string that specifies how encoding and decoding errors 
are to be handled. Pass ``'strict'`` to raise a ``ValueError`` exception if 
there is an encoding error (the default of ``None`` has the same effect), or 
pass ``'ignore'`` to ignore errors. (Note that ignoring encoding errors can lead
to data loss.) ``'replace'`` causes a replacement marker (such as ``'?'``) to be 
inserted where there is malformed data. ``'backslashreplace'`` causes malformed 
data to be replaced by a backslashed escape sequence. When writing, 
``'xmlcharrefreplace'`` (replace with the appropriate XML character reference) 
or ``'namereplace'`` (replace with ``\N{...}`` escape sequences) can be used. 
Any other error handling name that has been registered with 
``codecs.register_error()`` is also valid.

``newline`` controls how line endings are handled. It can be ``None``, ``''``, 
``'\n'``, ``'\r'``, and ``'\r\n'``. It works as follows:

* When reading input from the stream, if ``newline`` is ``None``, universal 
  newlines mode is enabled. Lines in the input can end in ``'\n'``, ``'\r'``, or
  ``'\r\n'``, and these are translated into ``'\n'`` before being returned to 
  the caller. If ``newline`` is ``''``, universal newlines mode is enabled, but 
  line endings are returned to the caller untranslated. If newline has any of 
  the other legal values, input lines are only terminated by the given string, 
  and the line ending is returned to the caller untranslated.
* When writing output to the stream, if ``newline`` is ``None``, any ``'\n'`` 
  characters written are translated to the system default line separator, 
  ``os.linesep``. If ``newline`` is ``''`` or ``'\n'``, no translation takes 
  place. If ``newline`` is any of the other legal values, any ``'\n'`` 
  characters written are translated to the given string.

By default, POSIX named pipe is created with a path signature ``$TMPDIR/pipe[a-z0-9_]{8}/[0-9]+``
while Windows named pipe is created with ``\\.\pipe\[0-9]+``. In other words, 
the named pipe has a numeric name. The pipe name can be customized by ``name`` 
argument. Given pipe name will replace the numeric pipe name but still placed in
the same directory. In POSIX, ``name`` may be an absolute path to place the pipe
outside of the ``$TMPDIR/pipe[a-z0-9_]{8}`` directory.

``NPopen`` is also a context manager and therefore supports the ``with`` 
statement. In this example, pipe and its stream are closed after the ``with`` 
statement’s suite is finished—even if an exception occurs:

.. code-block:: python

   with NPopen('w') as pipe:

       proc = sp.Popen(['my_client', pipe.path])

       stream = pipe.wait()

       stream.write('Spam and eggs!')

"""

NPopen.close.__doc__ = """Close named pipe

Flush and close ``NPopen.stream`` and delete the pipe from the file system. This 
method has no effect if the file is already closed. Once the file is closed, any 
operation on the pipe (e.g. reading or writing) will raise a ``ValueError``.

As a convenience, it is allowed to call this method more than once; only the 
first call, however, will have an effect.
"""

NPopen.wait.__doc__ = """Wait for client connection

Blocks until the other end of the pipe is opened by a client.
"""
