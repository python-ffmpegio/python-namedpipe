# `namedpipe` Cross-platform named pipe manager for Python

![PyPI](https://img.shields.io/pypi/v/namedpipe)
![PyPI - Status]( https://img.shields.io/pypi/status/namedpipe)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/namedpipe)
![GitHub License](https://img.shields.io/github/license/python-ffmpegio/python-namedpipe)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/python-ffmpegio/python-namedpipe/Run%20Tests)

Python only natively supports named pipes in Posix systems via `os.mkfifo`. This package extends the support to Windows and defines a `NPopen` class as a cross-platform solution to manage named pipes.

## Installation

```bash
pip install namedpipe
```

## Usage

```python
import subproces as sp
from namedpipe import NPopen

# 1. Use the context-managing `NPopen` class to open an (auto-)named pipe
#    - specify the mode argument with the standard notation (see built-in open())
with NPopen('r+') as pipe: # bidirectional (duplex) binary pipe
    # - for an inbound pipe, specify the read access mode 'rb' or 'rt' 
    # - for an outbound pipe, specify the write access mode 'wb or 'wt'

    # 2. Get the pipe path via pipe.path or str(pipe) to start the client program
    sp.run(['my_client', pipe.path])

    # auto-generated pipe paths (incremental integer pipe #):
    # - Posix: $TMPDIR/pipe[a-z0-9_]{8}/[0-9]+ (random pipe directory name)
    # - Windows: \\.\pipe\[0-9]+

    # 3. Wait for the client to connect and create a stream
    #    - accepts other open() arguments: buffering, encoding, error, newline
    #    - blocks until connection is established
    #    - returns an io-compatible stream
    stream = pipe.wait()

    # 4. Perform read/write operation with stream (or pipe.stream) as a file-like object
    b = stream.read(64)
    b = pipe.stream.read(64) # alternate

    in_bytes = bytearray(128)
    nread = stream.readinto(in_bytes)

    b_rest = stream.readall()
    
    stream.write(out_bytes)

# 5. automatically closes the stream and destroys the pipe object 
#    when out of the contenxt
```

## API Reference

TBD
