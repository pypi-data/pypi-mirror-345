# FSPacker

Fast & Simple Packer toolset for python.

## Key Features

- [x] 10-100x faster than existing deploy libs such as Py2exe, PyInstaller, Nuitka...
- [x] Supports multi-project deployment
- [x] Supports offline packing
- [ ] Supports archiving with zip or 7z
- [ ] Supports deployment with InnoSetup
- [ ] Supports compilation with nuitka
- [ ] Supports encryption with PyArmor

## Support Platforms

- [x] Windows 7 ~ 11
- [ ] linux
- [ ] macOS

## Support Libraries

- [x] tkinter(Windows only)
- [x] pyside2
- [x] matplotlib
- [x] pandas
- [x] pytorch

## Quick Start

Usage:

```bash
pip install fspacker
cd [directory/of/app.py]
fsp
```

> **!!!NOTICE!!!**
> 'app.py' must contain 'main' function as entry.

Example:

Python project structure:

```bash
ex01_helloworld/
|
|___ core
|   |____ __init__.py
|   |____ core_a.py
|   |____ core_b.py
|   |____ core_c.py
|
|___ mathtools/
|   |____ __init__.py
|   |____ algorithms.py
|
|___ modules/
|   |____ __init__.py
|   |____ mod_a.py
|   |____ mod_b.py
|
|___ ex01_helloworld.py
|___ global_a.py
|___ global_b.py
|___ pyproject.toml

```

```python
# ex01_helloworld.py
import global_a  # import
import global_b
from modules.mod_a import function_mod_a  # import from
from modules.mod_b import function_mod_b  # import from


def main():
    print("hello, world")

    function_mod_a()
    function_mod_b()
    global_a.function_global_a()
    global_b.function_global_b()


if __name__ == "__main__":
    main()
```

Run command:

```bash
cd .../ex01_helloworld
fsp b
```
