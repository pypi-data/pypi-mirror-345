import logging
import shutil
import string

from fspacker.packers._base import BasePacker
from fspacker.settings import get_settings

# int file template
INT_TEMPLATE = string.Template(
    """\
import sys, os
sys.path.append(os.path.join(os.getcwd(), "src"))
from $SRC import main
main()
"""
)

INT_TEMPLATE_QT = string.Template(
    """\
import sys, os
import $LIB_NAME

qt_dir = os.path.dirname($LIB_NAME.__file__)
plugin_path = os.path.join(qt_dir, "plugins" , "platforms")
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
sys.path.append(os.path.join(os.getcwd(), "src"))
from $SRC import main
main()
"""
)


class EntryPacker(BasePacker):
    NAME = "入口程序打包"

    def pack(self):
        name = self.info.normalized_name

        if not self.info.source_file or not self.info.source_file.exists():
            logging.error(f"入口文件{self.info.source_file}无效")
            return

        source = self.info.source_file.stem

        exe_filename = "gui.exe" if self.info.is_gui else "console.exe"
        src_exe_path = get_settings().assets_dir / exe_filename
        dst_exe_path = self.info.dist_dir / f"{name}.exe"

        logging.info(f"打包目标类型: {'[green bold]窗口' if self.info.is_gui else '[red bold]控制台'}[/]")
        logging.info(
            f"复制可执行文件: [green underline]{src_exe_path.name} -> "
            f"{dst_exe_path.relative_to(self.info.project_dir)}[/] [bold green]:heavy_check_mark:"
        )
        shutil.copy(src_exe_path, dst_exe_path)

        dst_int_path = self.info.dist_dir / f"{name}.int"

        logging.info(
            f"创建 int 文件: [green underline]{name}.int -> {dst_int_path.relative_to(self.info.project_dir)}"
            f"[/] [bold green]:heavy_check_mark:"
        )

        for lib_name in get_settings().qt_libs:
            if lib_name in self.info.ast_modules:
                logging.info(f"检测到目标库: {lib_name}")
                content = INT_TEMPLATE_QT.substitute(SRC=f"src.{source}", LIB_NAME=lib_name)
                break
        else:
            content = INT_TEMPLATE.substitute(SRC=f"src.{source}")

        with open(dst_int_path, "w") as f:
            f.write(content)
