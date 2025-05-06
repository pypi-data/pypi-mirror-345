# hatch_build.py
import logging
import os
import platform
import shutil
import subprocess
from functools import cached_property
from pathlib import Path
from time import perf_counter
from typing import List

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

logging.basicConfig(level=logging.INFO, format="[*] %(message)s")

CWD: Path = Path.cwd()


class CustomBuildHook(BuildHookInterface):
    # 构建对象
    APP_NAME: str = "fsloader"

    # c源码路径
    SOURCE_DIR: Path = CWD / "fsloader"
    # 输出路径
    OUTPUT_DIR: Path = CWD / "src" / "fspacker" / "assets"

    @cached_property
    def is_windows(self) -> bool:
        return platform.system()

    @cached_property
    def exe_name(self) -> Path:
        return f"{self.APP_NAME}.exe" if self.is_windows else self.APP_NAME

    @cached_property
    def app_dist_path(self) -> Path:
        if self.is_windows:
            return self.SOURCE_DIR / "target" / "x86_64-win7-windows-msvc" / "release" / self.exe_name
        else:
            return self.SOURCE_DIR / "target" / "release" / self.exe_name

    @cached_property
    def app_full_path(self) -> Path:
        return self.OUTPUT_DIR / self.exe_name

    @cached_property
    def build_commands(self) -> List[List[str]]:
        if self.is_windows:
            return [
                ["rustup", "override", "set", "nightly-x86_64-pc-windows-msvc"],
                ["rustup", "component", "add", "rust-src", "--toolchain", "nightly-x86_64-pc-windows-msvc"],
                ["cargo", "build", "--release", "-Z", "build-std", "--target", "x86_64-win7-windows-msvc"],
            ]
        else:
            return [
                ["cargo", "build", "--release", "-Z", "build-std", "--target", "x86_64-pc-linux-gnu"],
            ]

    def initialize(self, version, build_data):
        t0 = perf_counter()

        if not self.OUTPUT_DIR.exists():
            self.OUTPUT_DIR.mkdir(parents=True)

        logging.info(f"启动构建, 名称: {self.APP_NAME}, 源码路径: {self.SOURCE_DIR}, 输出路径: {self.OUTPUT_DIR}")

        try:
            os.chdir(self.SOURCE_DIR)
            for command in self.build_commands:
                logging.info(f"运行编译命令: {command}")
                subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            raise SystemExit(f"编译失败, 错误信息: {e}") from e

        if self.app_dist_path.exists():
            logging.info(f"拷贝文件: {self.app_dist_path} -> {self.app_full_path}")
            shutil.copyfile(self.app_dist_path, self.app_full_path)
        else:
            logging.error(f"未找到可执行文件, {self.app_dist_path}")

        logging.info(f"完成编译, 用时: {perf_counter() - t0:4f}s")
