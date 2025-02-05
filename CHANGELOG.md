# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[unreleased]: https://github.com/python-ffmpegio/python-namedpipe/compare/v0.1.0...HEAD
