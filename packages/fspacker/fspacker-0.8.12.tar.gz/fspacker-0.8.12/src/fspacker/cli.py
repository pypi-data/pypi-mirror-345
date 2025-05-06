"""应用客户端命令行接口"""

from pathlib import Path

from rich.console import Console
from typer import Argument
from typer import Option
from typer import Typer

from fspacker.models.mode import PackMode
from fspacker.parsers.manager import ProjectManager
from fspacker.settings import get_settings

app = Typer()
console = Console()
settings = get_settings()


@app.command(name="build", short_help="构建应用程序")
@app.command(name="b", short_help="构建应用程序, 别名: build")
def build(
    archive: bool = Option(False, help="打包模式, 将应用打包为 zip 格式."),
    rebuild: bool = Option(False, help="重构模式, 构建前清理项目文件."),
    recursive: bool = Option(True, help="递归搜索模式，搜索当前路径下的所有项目, 默认开启"),
    debug: bool = Option(False, help="调试模式, 显示调试信息."),
    simplify: bool = Option(False, help="简化模式"),
    use_tk: bool = Option(False, help="打包tk库"),
    offline: bool = Option(False, help="离线模式, 本地构建."),
    name: str = Argument(None, help="匹配名称"),
):
    """构建项目命令"""
    settings.mode = PackMode(
        archive=archive,
        debug=debug,
        offline=offline,
        rebuild=rebuild,
        recursive=recursive,
        simplify=simplify,
        use_tk=use_tk,
    )
    settings.set_logger(debug)
    settings.show()

    manager = ProjectManager(root_dir=Path.cwd(), match_name=name)
    manager.build()
    settings.dump()


@app.command(name="version", short_help="显示版本信息")
@app.command(name="v", short_help="显示版本信息, 别名: version")
def version():
    from fspacker import __build_date__
    from fspacker import __version__

    console.print(f"fspacker {__version__}, 构建日期: {__build_date__}")


@app.command(name="run", short_help="运行项目")
@app.command(name="r", short_help="运行项目, 别名: run")
def run(
    name: str = Argument(None, help="可执行文件名, 支持模糊匹配, 仅有一个时可留空."),
    debug: bool = Option(False, help="调试模式, 显示调试信息."),
):
    """运行项目命令"""
    settings.mode.recursive = True
    settings.set_logger(debug)

    manager = ProjectManager(Path.cwd(), match_name=name)
    manager.run(name)


@app.command(name="clean", short_help="清理项目")
@app.command(name="c", short_help="清理项目, 别名: clean")
def clean(
    directory: str = Argument(None, help="源码目录路径"),
    debug: bool = Option(False, help="调试模式, 显示调试信息."),
    recursive: bool = Option(True, help="递归搜索模式，搜索当前路径下的所有项目, 默认开启"),
):
    """清理项目命令"""
    settings.mode.recursive = recursive
    settings.mode.debug = debug
    settings.set_logger(debug)

    manager = ProjectManager(directory or Path.cwd())
    manager.clean()


def main():
    app()


if __name__ == "__main__":
    main()
