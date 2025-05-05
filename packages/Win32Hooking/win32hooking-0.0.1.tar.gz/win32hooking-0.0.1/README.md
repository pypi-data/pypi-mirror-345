![Win32Hooking Logo](https://mauricelambert.github.io/info/python/security/Win32Hooking_small.png "Win32Hooking logo")

# Win32Hooking

## Description

This module hooks IAT and EAT to monitor all external functions calls,
very useful for \[malware\] reverse and debugging.

> This module should run in a virtual machine without any EDR because it hook all exported and imported functions. Hooks may be detected and EDR can kill the process and removes files. Another problem is some EDR injected API, hooking the EDR API can be a problem to run an executable and some API could not be resolved (for example SentinelOne `ntd1l.dll` and `kern3l32.dll`, used to detect very basic shellcode, cannot be resolved as standard library).

## Requirements

This package require:

 - python3
 - python3 Standard Library

## Installation

### Pip

```bash
python3 -m pip install Win32Hooking
```

### Git

```bash
git clone "https://github.com/mauricelambert/Win32Hooking.git"
cd "Win32Hooking"
python3 -m pip install .
```

### Wget

```bash
wget https://github.com/mauricelambert/Win32Hooking/archive/refs/heads/main.zip
unzip main.zip
cd Win32Hooking-main
python3 -m pip install .
```

### cURL

```bash
curl -O https://github.com/mauricelambert/Win32Hooking/archive/refs/heads/main.zip
unzip main.zip
cd Win32Hooking-main
python3 -m pip install .
```

## Usages

### Command line

```bash
Win32Hooking              # Using CLI package executable
python3 -m Win32Hooking   # Using python module
python3 Win32Hooking.pyz  # Using python executable
Win32Hooking.exe          # Using python Windows executable

Win32Hooking "C:\Windows\System32\calc.exe"
```

### Python script

```python
from Win32Hooking import load

load(r"C:\Windows\System32\calc.exe")
```

## Links

 - [Pypi](https://pypi.org/project/Win32Hooking)
 - [Github](https://github.com/mauricelambert/Win32Hooking)
 - [Documentation](https://mauricelambert.github.io/info/python/security/Win32Hooking.html)
 - [Python executable](https://mauricelambert.github.io/info/python/security/Win32Hooking.pyz)
 - [Python Windows executable](https://mauricelambert.github.io/info/python/security/Win32Hooking.exe)

## License

Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).
