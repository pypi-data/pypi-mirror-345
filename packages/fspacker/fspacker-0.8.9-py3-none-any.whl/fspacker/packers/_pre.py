import logging
import shutil

from fspacker.packers._base import BasePacker
from fspacker.settings import get_settings


class PrePacker(BasePacker):
    NAME = "项目初始化打包"

    def pack(self):
        if get_settings().mode.rebuild:
            logging.info(f"清理旧文件: [[green]{self.info.dist_dir}[/]]")
            shutil.rmtree(self.info.dist_dir, ignore_errors=True)

        for directory in (self.info.dist_dir,):
            logging.info(f"创建文件夹: [[purple]{directory.name}[/]]")
            directory.mkdir(parents=True, exist_ok=True)
