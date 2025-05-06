import logging
import time
import typing

__all__ = ["PackerFactory"]

from fspacker.parsers.project import Project
from fspacker.settings import get_settings


class PackerFactory:
    """打包工具"""

    def __init__(self, info: Project):
        from fspacker.packers._base import BasePacker
        from fspacker.packers._builtins import BuiltinsPacker
        from fspacker.packers._entry import EntryPacker
        from fspacker.packers._library import LibraryPacker
        from fspacker.packers._post import PostPacker
        from fspacker.packers._pre import PrePacker
        from fspacker.packers._runtime import RuntimePacker
        from fspacker.packers._source import SourceResPacker

        self.info: Project = info

        # 打包器集合, 注意打包顺序
        self.packers: typing.Tuple[BasePacker, ...] = (
            PrePacker(self),
            SourceResPacker(self),
            LibraryPacker(self),
            BuiltinsPacker(self),
            EntryPacker(self),
            RuntimePacker(self),
            PostPacker(self),
        )

    def pack(self):
        logging.info(f"{'*' * 120}")
        logging.info(f"启动构建, 源码根目录: [[green underline]{self.info.project_dir}[/]]")
        t0 = time.perf_counter()

        for packer in self.packers:
            logging.info(packer)
            packer.pack()

        logging.info(f"打包完成! 总用时: [{time.perf_counter() - t0:.4f}]s.")
        if not get_settings().mode.debug:
            logging.info(f"{'*' * 120}")
