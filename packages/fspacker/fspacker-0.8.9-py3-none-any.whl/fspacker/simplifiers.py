"""提供库打包精简配置功能"""

from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Set

__all__ = [
    "get_simplify_options",
]


@dataclass
class SimplifierOption:
    """库简化打包配置"""

    # 白名单匹配规则
    patterns: Optional[Set[str]] = None

    # 黑名单匹配规则
    excludes: Optional[Set[str]] = None


# 简化配置
_simplifier_options_dict: Dict[str, SimplifierOption] = dict(
    pyside2=SimplifierOption(
        patterns={
            "PySide2/__init__.py",
            "PySide2/pyside2.abi3.dll",
            "PySide2/QtCore.pyd",
            "PySide2/Qt5Core.dll",
            "PySide2/QtGui.pyd",
            "PySide2/Qt5Gui.dll",
            "PySide2/QtWidgets.pyd",
            "PySide2/Qt5Widgets.dll",
            "PySide2/QtNetwork.pyd",
            "PySide2/Qt5Network.dll",
            "PySide2/QtQml.pyd",
            "PySide2/Qt5Qml.dll",
            "*plugins/iconengines/qsvgicon.dll",
            "*plugins/imageformats/*.dll",
            "*plugins/platforms/*.dll",
        },
    ),
    pygame=SimplifierOption(
        excludes={
            "pygame/docs/*",
            "pygame/examples/*",
            "pygame/tests/*",
            "pygame/__pyinstaller/*",
            "pygame*data/*",
        }
    ),
    matplotlib=SimplifierOption(
        excludes={"matplotlib-.*.pth"},
        patterns={
            "matplotlib/*",
            "matplotlib.libs/*",
            "mpl_toolkits/*",
            "pylab.py",
        },
    ),
    numba=SimplifierOption(
        patterns={
            "numba/*",
            "numba*data/*",
        }
    ),
    numpy=SimplifierOption(
        excludes={
            "numpy/_pyinstaller/*",
            "numpy/tests/*",
        }
    ),
    torch=SimplifierOption(
        excludes={
            # for debug
            "torch/utils/bottleneck/*",
            "torch/utils/checkpoint/*",
            "torch/utils/tensorboard/*",
            # for test
            "torch/utils/data/dataset/*",
            "torch/utils/data/dataloader/*",
        }
    ),
)


def get_simplify_options(name: str) -> Optional[SimplifierOption]:
    """获取库打包精简配置

    Args:
        name (str): 库名称

    Returns:
        SimplifierOption: 库打包精简配置
    """
    return _simplifier_options_dict.get(name, None)
