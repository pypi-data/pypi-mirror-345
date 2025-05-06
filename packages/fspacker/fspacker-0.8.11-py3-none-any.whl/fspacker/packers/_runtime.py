import logging
import shutil
import time

from packaging.specifiers import SpecifierSet
from packaging.version import parse

from fspacker.exceptions import ProjectPackError
from fspacker.packers._base import BasePacker
from fspacker.settings import get_settings
from fspacker.utils.checksum import calc_checksum
from fspacker.utils.url import safe_read_url_data


class RuntimePacker(BasePacker):
    NAME = "运行时打包"

    def pack(self):
        if (self.info.runtime_dir / "python.exe").exists():
            logging.warning("目标文件夹 [purple]runtime[/] 已存在, 跳过 [bold green]:heavy_check_mark:")
            return

        specs = SpecifierSet(self.info.python_specifiers)
        if parse(self.info.python_ver) not in specs:
            logging.error(
                f"当前环境python版本: [green bold]{self.info.python_ver}[/], 与项目要求"
                f"[green bold]{self.info.python_specifiers}[/] 不匹配"
            )

        if self.info.embed_filepath.exists():
            logging.info("找到本地 [green bold]embed 压缩包")

            if not get_settings().mode.offline:
                logging.info(
                    f"非离线模式, 检查校验和: [green underline]{self.info.embed_filepath.name}"
                    " [bold green]:heavy_check_mark:"
                )
                src_checksum = get_settings().dirs.checksum
                dst_checksum = calc_checksum(self.info.embed_filepath)

                if src_checksum == dst_checksum:
                    logging.info("校验和一致, 使用[bold green] 本地运行时 :heavy_check_mark:")
                else:
                    logging.info("校验和不一致, 重新下载")
                    self._fetch_runtime()
        else:
            if not get_settings().mode.offline:
                logging.info("非离线模式, 获取运行时")
                self._fetch_runtime()
            else:
                raise ProjectPackError(f"离线模式且本地运行时不存在, {self.info.embed_filepath}")

        if self.info.embed_filepath.exists():
            logging.info(
                f"解压 runtime 文件: [green underline]{self.info.embed_filepath.name} "
                f"-> {self.info.runtime_dir.relative_to(self.info.project_dir)}[/] [bold green]:heavy_check_mark:"
            )
            shutil.unpack_archive(self.info.embed_filepath, self.info.runtime_dir, "zip")

    def _fetch_runtime(self):
        fastest_embed_url = get_settings().urls.fastest_embed_url
        archive_url = f"{fastest_embed_url}{self.info.python_ver}/{self.info.embed_filename}"

        if not archive_url.startswith("https://"):
            logging.error(f"url无效: {archive_url}")
            return

        content = safe_read_url_data(archive_url)
        if content is None:
            logging.error("下载运行时失败")
            return

        logging.info(f"从地址下载运行时: [[green bold]{archive_url}[/]]")
        t0 = time.perf_counter()

        if not get_settings().dirs.embed.exists():
            get_settings().dirs.embed.mkdir(parents=True)

        with open(self.info.embed_filepath, "wb") as f:
            f.write(content)

        download_time = time.perf_counter() - t0
        logging.info(f"下载完成, 用时: [green bold]{download_time:.2f}s")

        checksum = calc_checksum(self.info.embed_filepath)
        logging.info(f"更新校验和 [{checksum}]")
        get_settings().dirs.checksum = checksum
