# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.5] - 2025-03-01

### Fixed

- Fixed pipe and stream checks by testing to be not None

## [0.2.4] - 2025-02-21

### Fixed

- Fixed broken pipe error handling in `win32`. It now correctly raises the `BrokenPipeError`.

## [0.2.3] - 2025-02-19

### Fixed

- `__exit__` to re-raise the exception by returning `False` (reverted v0.2.2)

## [0.2.2] - 2025-02-19

### Fixed

- `__exit__` to suppress any exception by returning `True`

## [0.2.1] - 2025-02-11

### Fixed

- [Issue #3] fixed throwing exception when Windows raises ERROR_PIPE_CONNECTED error, which is an OK behavior

## [0.2.0] - 2025-02-04

### Added

- Added `NPopen.readable()` and `NPopen.writable()` methods

## [0.1.1] - 2024-03-27

### Changed

- Dropped support for py3.7
- Removed unnecessary dependency `"typing_extensions;python_version<'3.8'"`

### Fixed

- Reverted the use of the new Union type hint (|) unsupported in py3.8 to old `Union[]` syntax [issue#1;issue#2]

## [0.1.0] - 2022-11-22

Initial release

[unreleased]: https://github.com/python-ffmpegio/python-namedpipe/compare/v0.2.5...HEAD
[0.2.5]: https://github.com/python-ffmpegio/python-namedpipe/compare/v0.2.4...v0.2.4
[0.2.4]: https://github.com/python-ffmpegio/python-namedpipe/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/python-ffmpegio/python-namedpipe/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/python-ffmpegio/python-namedpipe/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/python-ffmpegio/python-namedpipe/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/python-ffmpegio/python-namedpipe/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/python-ffmpegio/python-namedpipe/compare/v0.1.0...v0.1.1
