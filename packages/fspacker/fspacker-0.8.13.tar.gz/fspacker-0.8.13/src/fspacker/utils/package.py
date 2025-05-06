import fnmatch
import logging
import pathlib
import re
import subprocess
import typing
import zipfile
from urllib.parse import urlparse

from packaging import requirements

from fspacker.settings import get_settings
from fspacker.simplifiers import get_simplify_options
from fspacker.trackers import perf_tracker


def _is_version_satisfied(cached_file: pathlib.Path, req: requirements.Requirement) -> bool:
    """检查缓存文件版本是否满足需求"""

    if not req.specifier:
        return True  # 无版本约束

    version = _extract_package_version(cached_file.name)
    return version in req.specifier


def get_cached_package(req: requirements.Requirement) -> typing.Optional[pathlib.Path]:
    """获取满足版本约束的缓存文件"""

    package_name = req.name.lower().replace("-", "_")  # 包名大小写不敏感
    pattern = f"{package_name}-*" if not req.specifier else f"{package_name}-[0-9]*"

    for cached_file in get_settings().dirs.libs.glob(pattern):
        if cached_file.suffix in (".whl", ".gz", ".zip"):
            if _is_version_satisfied(cached_file, req):
                return cached_file
    return None


def download_to_libs_dir(req: requirements.Requirement) -> pathlib.Path:
    """下载满足版本的包到缓存"""

    pip_url = get_settings().urls.fastest_pip_url
    net_loc = urlparse(pip_url).netloc
    libs_dir = get_settings().dirs.libs
    libs_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        get_settings().python_exe,
        "-m",
        "pip",
        "download",
        "--no-deps",
        "--dest",
        str(libs_dir),
        str(req),  # 使用解析后的Requirement对象保持原始约束
        "--trusted-host",
        net_loc,
        "-i",
        pip_url,
        "--no-deps",
    ]

    subprocess.call(cmd, shell=False)
    lib_filepath = get_cached_package(req) or pathlib.Path()
    logging.info(f"下载后库文件: [[green bold]{lib_filepath.name}[/]]")
    return lib_filepath


@perf_tracker
def unpack_whleel(
    wheel_file: pathlib.Path,
    dest_dir: pathlib.Path,
    excludes: typing.Optional[typing.Set[str]] = None,
    patterns: typing.Optional[typing.Set[str]] = None,
) -> None:
    excludes = set() if excludes is None else excludes
    patterns = set() if patterns is None else patterns

    excludes = set(excludes) | {"*dist-info/*"}
    with zipfile.ZipFile(wheel_file, "r") as zf:
        for file in zf.namelist():
            if any(fnmatch.fnmatch(file, exclude) for exclude in excludes):
                continue

            if len(patterns):
                if any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                    zf.extract(file, dest_dir)
                    continue
                else:
                    continue

            zf.extract(file, dest_dir)


@perf_tracker
def install_package(
    req: requirements.Requirement,
    lib_file: pathlib.Path,
    dest_dir: pathlib.Path,
    simplify: bool = False,
) -> None:
    """从缓存安装到site-packages"""
    options = get_simplify_options(req.name)

    if simplify and options:
        excludes, patterns = options.excludes, options.patterns
        logging.info(f"找到简化目标库: {req.name}, {options.excludes=}, {options.patterns=}")
    else:
        excludes, patterns = None, None

    if lib_file.suffix == ".whl":
        unpack_whleel(lib_file, dest_dir, excludes, patterns)
    else:
        cmds = [get_settings().python_exe, "-m", "pip", "install", str(lib_file.absolute()), "-t", str(dest_dir)]
        logging.info(f"调用命令: [green bold]{cmds}")
        subprocess.call(cmds, shell=False)


def _extract_package_version(filename: str) -> str:
    """从文件名提取版本号, 支持任意长度版本号如 20.0 或 1.20.3.4

    适配格式：
       package-1.2.3.tar.gz
       package-20.0-py3-none-any.whl
       Package_Name-1.20.3.4.whl
    """
    # 匹配两种命名格式：
    # 1. 常规格式：package-1.2.3
    # 2. 复杂wheel格式：Package-1.2.3.4-xxx.whl
    version_pattern = r"""
        (?:^|-)                   # 开头或连接符
        (\d+\.\d+(?:\.\d+)*)      # 版本号核心（至少两段数字）
        (?=-|\.|_|$)              # 后接分隔符或结束
    """
    match = re.search(version_pattern, filename, re.VERBOSE)
    return match.group(1) if match else "0.0.0"  # 默认返回最低版本
