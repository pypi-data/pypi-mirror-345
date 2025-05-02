import logging
import shutil

from fspacker.packers._base import BasePacker
from fspacker.settings import get_settings


class PostPacker(BasePacker):
    NAME = "项目后处理打包"

    def pack(self):
        if get_settings().mode.archive:
            logging.info(f"压缩文件: [[green]{self.info.dist_dir}[/]]")
            shutil.make_archive(
                self.info.dist_dir.name,
                "zip",
                self.info.dist_dir.parent,
                self.info.dist_dir.name,
            )
