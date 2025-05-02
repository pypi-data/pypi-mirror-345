import logging
import platform
from pathlib import Path
from typing import Optional
from typing import Set

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from rich.logging import RichHandler

from fspacker.models.dirs import default_cache_dir
from fspacker.models.dirs import Dirs
from fspacker.models.mode import PackMode
from fspacker.models.urls import Urls

__all__ = ["get_settings"]


_env_filepath = default_cache_dir / ".env"
_export_prefixes = {"urls", "dirs"}


class Settings(BaseSettings):
    """Settings for fspacker."""

    model_config = SettingsConfigDict(
        env_file=str(_env_filepath),
        env_prefix="FSP_",
        env_nested_delimiter="__",
        extra="allow",
    )

    MAX_THREAD: int = 6

    dirs: Dirs = Dirs()
    urls: Urls = Urls()
    mode: PackMode = PackMode()

    src_dir: Path = Path(__file__).parent
    assets_dir: Path = src_dir / "assets"
    python_exe: str = "python.exe" if platform.system() == "Windows" else "python3"
    ignore_folders: Set[str] = {"dist-info", "__pycache__", "site-packages", "runtime", "dist", ".venv"}
    # 窗口程序库
    gui_libs: Set[str] = {"PySide2", "PyQt5", "pygame", "matplotlib", "tkinter", "pandas"}
    # 使用tk的库
    tk_libs: Set[str] = {"matplotlib", "tkinter", "pandas"}
    # qt库
    qt_libs: Set[str] = {"PySide2", "PyQt5", "PySide6", "PyQt6"}

    def show(self):
        logging.info(f"模式: {self.mode}")
        logging.info(f"链接: {self.urls}")
        logging.info(f"目录: {self.dirs}")

    def set_logger(self, debug: bool = False) -> None:
        level = logging.DEBUG if (debug or self.mode.debug) else logging.INFO

        logging.basicConfig(
            level=level,
            format="[*] %(message)s",
            datefmt="[%X]",
            handlers=[
                RichHandler(markup=True),
            ],
        )

    def dump(self):
        """Dump settings to '.env' local config file."""
        prefix = self.model_config["env_prefix"]

        with open(_env_filepath, "w") as f:
            for name, value in self.model_dump(by_alias=True).items():
                if str(name) in _export_prefixes:
                    if isinstance(value, dict):
                        for sub_key, sub_val in value.items():
                            env_name = f"{name.upper()}__{sub_key.upper()}"
                            f.write(f"{prefix}{env_name}={sub_val}\n")
                    else:
                        f.write(f"{prefix}{name.upper()}={value}\n")


_settings: Optional[Settings] = None


def get_settings():
    """Get global settings"""

    global _settings

    if _settings is None:
        _settings = Settings()

        for directory in _settings.dirs.entries:
            if not directory.exists():
                directory.mkdir(parents=True)

    return _settings
