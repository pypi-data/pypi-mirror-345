![PyPeLoader Logo](https://mauricelambert.github.io/info/python/security/PyPeLoader_small.png "PyPeLoader logo")

# PyPeLoader

## Description

This package implements a basic PE loader in python (can load simple
executable like calc.exe, net1.exe, little malwares...)

## Requirements

This package require:
 - python3
 - python3 Standard Library

## Installation

### Pip

```bash
python3 -m pip install PyPeLoader
```

### Git

```bash
git clone "https://github.com/mauricelambert/PyPeLoader.git"
cd "PyPeLoader"
python3 -m pip install .
```

### Wget

```bash
wget https://github.com/mauricelambert/PyPeLoader/archive/refs/heads/main.zip
unzip main.zip
cd PyPeLoader-main
python3 -m pip install .
```

### cURL

```bash
curl -O https://github.com/mauricelambert/PyPeLoader/archive/refs/heads/main.zip
unzip main.zip
cd PyPeLoader-main
python3 -m pip install .
```

## Usages

### Command line

```bash
PyPeLoader              # Using CLI package executable
python3 -m PyPeLoader   # Using python module
python3 PyPeLoader.pyz  # Using python executable
PyPeLoader.exe          # Using python Windows executable

PyPeLoader.exe "C:\Windows\System32\net1.exe" "C:\Windows\System32\calc.exe"
```

### Python script

```python
from PyPeLoader import load

load(r'C:\Windows\System32\net1.exe') # for 32 bits python version use: C:\Windows\SysWOW64\net1.exe
load(r'C:\Windows\System32\calc.exe') # for 32 bits python version use: C:\Windows\SysWOW64\calc.exe
```

## Links

 - [Pypi](https://pypi.org/project/PyPeLoader)
 - [Github](https://github.com/mauricelambert/PyPeLoader)
 - [Documentation](https://mauricelambert.github.io/info/python/security/PyPeLoader.html)
 - [Python executable](https://mauricelambert.github.io/info/python/security/PyPeLoader.pyz)
 - [Python Windows executable](https://mauricelambert.github.io/info/python/security/PyPeLoader.exe)

## License

Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).
