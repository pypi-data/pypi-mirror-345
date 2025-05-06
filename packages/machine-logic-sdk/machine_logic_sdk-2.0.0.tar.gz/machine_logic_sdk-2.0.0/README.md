Provides a programmatic interface in Python to talk to Vention hardware, as well as a generic state machine for coordinating your programs.

## Table of Contents

1. [Requirements](#Requirements)
1. [Development](#Development)
1. [Documentation](#Documentation)
1. [Resources](#Resources)

## Requirements
Python 3.9.2
Higher versions of Python work (until 3.11), but 3.9.2 is shipped on the MachineMotion.

### Installing Python

You can install python 3.9 on Ubuntu via `sudo apt install python3.9`  
Check your python version via `python3 --version`  
If you already had a python version installed, you'll need to map `python3` to the 3.9 version that you installed.

```sh
cd /usr/bin
sudo link python3
sudo ln -s /usr/bin/python3.9 python3
```

Then you'll need these in order to set up a venv

```sh
sudo apt-get install python3-apt python3-virtualenv python3.9-venv
```

## Development

Always work inside a python `venv` so that your dependencies do not get interfered with:

```sh
python3 -m venv venv
source venv/bin/activate
```

You will need to upgrade pip before continuing

```sh
pip install --upgrade pip
```

Then install package:

```sh
pip install machine-logic-sdk
```

## Documentation
- [Documentation](https://vention.io/resources/guides/machinelogic-python-programming-514)

## Resources
- [Miros](https://aleph2c.github.io/miros/html/#) is the framework upon which our architecture is based
