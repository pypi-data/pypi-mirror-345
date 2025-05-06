import ast
import logging
import platform
import sys
from functools import cached_property
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set

from packaging.requirements import Requirement

from fspacker.exceptions import ProjectParseError
from fspacker.settings import get_settings

try:
    # Python 3.11+标准库
    import tomllib
except ImportError:
    # 兼容旧版本Python
    import tomli as tomllib

__all__ = ["Project"]


class Project:
    """项目构建信息"""

    def __init__(self, project_dir: Optional[Path] = None):
        self.name = ""
        self.project_dir = project_dir
        self.python_specifiers = ""
        self.source_file: Optional[Path] = None
        self.dependencies = []
        # 导入模块
        self.ast_modules = set()

        # 解析数据
        self.data: Optional[Dict[str, Any]] = None
        self._parse()

    def __repr__(self):
        return f"[green bold]{self.name}[/]"

    def _parse(self) -> None:
        """解析项目目录下的 pyproject.toml 文件，获取项目信息"""

        self._parse_config()
        self._parse_ast()

        if self.data:
            self._parse_dependencies()

    @property
    def dist_dir(self):
        return self.project_dir / "dist"

    @property
    def runtime_dir(self):
        return self.dist_dir / "runtime"

    @property
    def exe_file(self) -> Path:
        return self.dist_dir / f"{self.normalized_name}.exe"

    @cached_property
    def python_ver(self) -> str:
        return platform.python_version()

    @cached_property
    def embed_filename(self) -> str:
        machine_code = platform.machine().lower()
        return f"python-{self.python_ver}-embed-{machine_code}.zip"

    @cached_property
    def embed_filepath(self) -> Path:
        return get_settings().dirs.embed / self.embed_filename

    @property
    def is_gui(self):
        """判断是否为 GUI 项目"""
        return bool(self.ast_modules & get_settings().gui_libs)

    @property
    def normalized_name(self):
        """名称归一化，替换所有'-'为'_'"""

        return self.name.replace("-", "_")

    def _parse_config(self) -> None:
        """读取配置文件"""
        if not self.project_dir or not self.project_dir.exists():
            raise ProjectParseError(f"项目路径无效: {self.project_dir}")

        config_path = self.project_dir / "pyproject.toml"

        if not config_path.is_file():
            logging.error(f"路径下未找到 pyproject.toml 文件: {self.project_dir}")
            return

        try:
            with config_path.open("rb") as f:
                self.data = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            logging.error(f"TOML解析错误: [red]{e}[/], 路径: [red]{self.project_dir}")
        except Exception as e:
            logging.error(f"未知错误: [red]{e}[/], 路径: [red]{self.project_dir}")

    def _parse_ast(self) -> Set[str]:
        """解析项目导入模块"""
        builtin_modules = set(sys.builtin_module_names)

        for py_file in self.project_dir.rglob("*.py"):
            # 跳过无效目录
            if any(p.name in get_settings().ignore_folders for p in py_file.parents):
                continue

            # 解析AST语法树
            with py_file.open("r", encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read())
                except SyntaxError:
                    logging.error(f"源文件解析语法错误, 文件: [red]{py_file}[/], 路径: [red]{self.project_dir}")
                    continue

            # 遍历Import节点
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split(".", 1)[0]
                        if module.lower() not in builtin_modules:
                            self.ast_modules.add(module)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module.split(".", 1)[0] if node.module else ""
                    if module.lower() not in builtin_modules:
                        self.ast_modules.add(module)

    def _parse_dependencies(self) -> None:
        """解析依赖项"""
        if "project" in self.data:
            self._parse_pep621(self.data["project"])
        elif "tool" in self.data and "poetry" in self.data["tool"]:
            self._parse_poetry(self.data["tool"]["poetry"])
        else:
            logging.error(f"pyproject.toml 配置项无效, 路径: [red]{self.project_dir}")

    def _parse_pep621(self, project_data: dict) -> None:
        """解析 PEP 621 格式的 pyproject.toml"""
        self.name = project_data.get("name", "")
        if not self.name:
            logging.error(f"未设置项目名称, 路径: [red]{self.project_dir}")

        self.python_specifiers = project_data.get("requires-python", "")
        if not self.python_specifiers:
            logging.error(f"未指定python版本, 路径: [red]{self.project_dir}")

        self.dependencies = project_data.get("dependencies", [])
        if not isinstance(self.dependencies, list):
            logging.error(f"依赖项格式错误: {self.dependencies}, 路径: [red]{self.project_dir}")

    def _parse_poetry(self, project_data: dict) -> None:
        """解析 Poetry 格式的 pyproject.toml"""
        self.name = project_data.get("name", "")
        if not self.name:
            logging.error(f"未设置项目名称, 路径: [red]{self.project_dir}")

        dependencies = project_data.get("dependencies", {})

        # 移除python版本声明
        if "python" in dependencies:
            self.python_specifiers = _convert_poetry_specifiers(dependencies.get("python"))
            dependencies.pop("python")
        else:
            logging.error(f"未指定python版本, 路径: [red]{self.project_dir}")

        # 处理依赖项
        self.dependencies = _convert_dependencies(dependencies)
        if not isinstance(self.dependencies, list):
            logging.error(f"依赖项格式错误: {self.dependencies}, 路径: [red]{self.project_dir}")


def _convert_dependencies(deps: dict) -> list:
    """将 Poetry 的依赖语法转换为 PEP 621 兼容格式"""
    converted = []
    for pkg, constraint in deps.items():
        req = Requirement(pkg)
        req.specifier = _convert_poetry_specifiers(constraint)
        converted.append(str(req))
    return converted


def _convert_poetry_specifiers(constraint: str) -> str:
    """处理 Poetry 的版本约束符号"""
    if constraint.startswith("^"):
        base_version = constraint[1:]
        return f">={base_version},<{_next_major_version(base_version)}"
    elif constraint.startswith("~"):
        base_version = constraint[1:]
        return f">={base_version},<{_next_minor_version(base_version)}"
    else:
        return constraint  # 直接传递 >=, <= 等标准符号


def _next_major_version(version: str) -> str:
    """计算下一个主版本号（如 1.2.3 → 2.0.0）"""
    parts = list(map(int, version.split(".")))
    parts[0] += 1
    parts[1:] = [0] * (len(parts) - 1)
    return ".".join(map(str, parts))


def _next_minor_version(version: str) -> str:
    """计算下一个次版本号（如 1.2.3 → 1.3.0）"""
    parts = list(map(int, version.split(".")))
    if len(parts) < 2:
        parts += [0]
    parts[1] += 1
    parts[2:] = [0] * (len(parts) - 2) if len(parts) > 2 else []
    return ".".join(map(str, parts))
