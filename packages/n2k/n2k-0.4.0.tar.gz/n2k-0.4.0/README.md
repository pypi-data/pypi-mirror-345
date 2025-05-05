# NMEA2000
NMEA2000 library for Raspberry Pi. Fork of https://github.com/ttlappalainen/NMEA2000

This library is still in an alpha state and is currently missing support for the following:

- several messages (as noted by the `todo` comments in [n2k/messages.py](n2k/messages.py)
- testing for the included messages
- support for transport protocol messages
- support for group functions
- proper logging
- good documentation. For now only the expected values for the messages are documented

The interface for creating messages will likely change in the future.

## Installing the library
If you want to use this library for a project, simply install it via pip:

```bash
pip install n2k
```


## Contributing

### Setup dev environment
First make sure you have python installed.

Then run
```bash
./prepare.sh
source .venv/bin/activate
```
to setup your virtual environment, install dependencies and setup pre-commit hooks.

If you choose to use VS Code as your editor, there are some extension recommendations that will automatically show up, as well as some pre-configured workspace settings.

### Build Documentation
```bash
cd docs && make clean && make html
```

### Build and publish package
```bash
python -m build && twine upload dist/*
```
