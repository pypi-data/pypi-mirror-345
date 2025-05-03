# BuildSnap

**BuildSnap** is a Python CLI tool that helps you easily build and unpack Python packages using `setup.py`. It's simple, fast, and built with [Click](https://click.palletsprojects.com/).

## Features

- Build `.tar.gz` (source) and `.whl` (wheel) distributions
- Make a ready setupped package directory and files
- Lightweight and terminal-friendly

## Commands

```bash
buildsnap --help

buildsnap build
options:
--tar, --whl
--path, -p

Example:
buildsnap build --tar -p /sdcard/mypkg

buildsnap init
options
--name
--username

Example:
buildsnap init --name MyPKG --username User

buildsnap install
options:
--path, -p

Example:
buildsnap install --path /sdcard/MyPKG
```

## Installation

```bash
pip install buildsnap
```