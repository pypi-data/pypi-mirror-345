import logging

from packaging.requirements import Requirement

from fspacker.packers._base import BasePacker
from fspacker.parsers.package import analyze_package_deps
from fspacker.settings import get_settings
from fspacker.utils.package import download_to_libs_dir
from fspacker.utils.package import get_cached_package
from fspacker.utils.package import install_package
from fspacker.utils.requirement import RequirementParser


class LibraryPacker(BasePacker):
    NAME = "依赖库打包"

    def _install_lib(self, req: Requirement):
        dist_dir = self.info.dist_dir / "site-packages"
        dist_dir.mkdir(parents=True, exist_ok=True)

        # 库解压目标可能为文件夹或者.py文件
        lib_file = dist_dir / f"{req.name}.py"
        lib_folder = dist_dir / req.name
        if lib_folder.exists() or lib_file.exists():
            logging.info(f"依赖库已存在, 跳过: [[red]{req.name}[/]]")
            return None

        logging.info(f"打包依赖: [[green bold]{req}[/]]")
        cached_file = get_cached_package(req)
        if cached_file:
            logging.info(f"找到本地满足要求的依赖: [[green]{cached_file.name}]")
        else:
            logging.info(f"下载依赖: [[green]{req}[/]]")
            cached_file = download_to_libs_dir(req)

        if cached_file.is_file():
            logging.info(f"安装依赖: [[green]{cached_file.name}[/]]")
            install_package(req, cached_file, dist_dir, simplify=get_settings().mode.simplify)
            return cached_file
        else:
            logging.error(f"处理依赖失败: [[red bold]{req}[/]]")
            return None

    def pack(self):
        req_libs = self.dependencies
        logging.info(f"分析一级依赖库: [[green bold]{req_libs}[/]]")
        for req_lib in req_libs:
            req = RequirementParser.parse(req_lib)
            logging.info(f"打包顶层依赖: [[green bold]{req}[/]]")

            cached_file = self._install_lib(req)
            if cached_file:
                secondary_reqs = analyze_package_deps(cached_file)
                logging.info(f"分析二级依赖: [[green]{secondary_reqs}[/]]")
                for secondary_req in secondary_reqs:
                    self._install_lib(secondary_req)
