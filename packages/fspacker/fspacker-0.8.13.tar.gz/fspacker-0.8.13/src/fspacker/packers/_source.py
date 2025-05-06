import logging
import pathlib
import re
import shutil

from fspacker.packers._base import BasePacker


class SourceResPacker(BasePacker):
    NAME = "源码 & 资源打包"

    # 忽视清单
    IGNORE_ENTRIES = ["dist-info", "__pycache__", "site-packages", "runtime", "dist", ".venv"]

    def _valid_file(self, filepath: pathlib.Path) -> bool:
        return all(x not in str(filepath) for x in self.IGNORE_ENTRIES)

    def pack(self) -> None:
        dest_dir = self.info.dist_dir / "src"
        source_files = list(file for file in self.info.project_dir.rglob("*.py") if self._valid_file(file))

        pattern = re.compile(
            r"(def\s+main\s*$.*?$\s*:)|"  # 匹配def main
            r'(if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:)',  # 匹配if __name__...
            flags=re.MULTILINE | re.DOTALL,
        )

        for source_file in source_files:
            with open(source_file, encoding="utf8") as f:
                content = "\n".join(f.readlines())
            matches = pattern.findall(content)
            if len(matches):
                logging.info(f"入口 Python 文件： [[green bold]{source_file}[/]]")
                self.info.source_file = source_file
                source_folder = source_file.absolute().parent
                break
        else:
            logging.error("未找到入口 Python 文件")
            return

        dest_dir.mkdir(parents=True, exist_ok=True)
        for entry in source_folder.iterdir():
            dest_path = dest_dir / entry.name

            # 不拷贝pyproject.toml文件
            if entry.is_file() and entry.name != "pyproject.toml":
                logging.info(f"复制目标文件: [green underline]{entry.name}[/] [bold green]:heavy_check_mark:")
                shutil.copy2(entry, dest_path)
            elif entry.is_dir():
                if entry.stem not in self.IGNORE_ENTRIES:
                    logging.info(f"复制目标文件夹: [purple underline]{entry.name}[/] [bold purple]:heavy_check_mark:")
                    shutil.copytree(entry, dest_path, dirs_exist_ok=True)
                else:
                    logging.info(f"目标文件夹 [red]{entry.name}[/] 已存在, 跳过")
