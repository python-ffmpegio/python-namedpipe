# `namedpipe` Cross-platform named pipe manager for Python

![PyPI](https://img.shields.io/pypi/v/namedpipe)
![PyPI - Status]( https://img.shields.io/pypi/status/namedpipe)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/namedpipe)
![GitHub License](https://img.shields.io/github/license/python-ffmpegio/python-namedpipe)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/python-ffmpegio/python-namedpipe/test_n_pub.yml?branch=master)

Python natively supports named pipes only in Posix systems via `os.mkfifo`. 
This package extends the support to Windows and defines a `NPopen` class as 
a cross-platform solution to manage named pipes.

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

    pipe.readable() # returns True if yields a readable stream
    pipe.writable() # returns True if yields a writable stream

    # 2. Get the pipe path via pipe.path or str(pipe) to start the client program
    sp.run(['my_client', pipe.path])

    # auto-generated pipe paths (incremental integer pipe #):
    # - Posix: $TMPDIR/pipe[a-z0-9_]{8}/[0-9]+ (random pipe directory name)
    # - Windows: \\.\pipe\[0-9]+

    # 3. Wait for the client to connect and create a stream
    #    - blocks until connection is established
    #    - returns an io-compatible stream
    stream = pipe.wait()

    # 4. Perform read/write operation with stream (or pipe.stream) as a file-like object
    b = stream.read(64)      # read 64 bytes from the client
    b = pipe.stream.read(64) # same call but using the stream property

    in_bytes = bytearray(128)
    nread = stream.readinto(in_bytes) # read 128 bytes of data from client and place them in in_bytes

    b_rest = stream.readall() # read all bytes sent by the client, block till client closes the pipe
    
    stream.write(out_bytes) # send bytes in out_bytes to the client

# 5. the stream is automatically closed and the pipe object is destroyed
#    when comes out of the context
```

## API Reference

TBD
