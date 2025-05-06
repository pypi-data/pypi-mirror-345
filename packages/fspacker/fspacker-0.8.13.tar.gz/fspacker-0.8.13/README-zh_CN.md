# FSPacker

Python `极简`打包工具集.

## 关键特性

- [x] 比Py2exe、PyInstaller、Nuitka等现有库打包速度快10-100倍
- [x] 支持多项目部署
- [x] 支持离线打包
- [ ] 支持使用zip或7z进行压缩归档
- [ ] 支持InnoSetup安装包制作
- [ ] 支持nuitka编译
- [ ] 支持PyArmor加密

## 支持平台

- [x] Windows 7 ~ 11
- [ ] Linux
- [ ] macOS

## 支持库

- [x] tkinter(仅Windows)
- [x] pyside2
- [x] matplotlib
- [x] pandas
- [x] pytorch

## 快速入门

使用方式:

```bash
pip install fspacker
cd [app.py所在目录]
fsp b
```

> **!!!注意!!!**
> 'app.py'必须包含作为程序入口的'main'函数

示例:

Python项目结构:

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

运行命令:

```bash
cd .../ex01_helloworld_console
fsp b
```
