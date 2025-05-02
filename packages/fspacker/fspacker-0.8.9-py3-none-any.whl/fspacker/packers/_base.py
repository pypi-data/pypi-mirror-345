from fspacker.packers.factory import PackerFactory


class BasePacker:
    """针对特定场景打包工具"""

    NAME = "基础打包"

    def __init__(self, parent: PackerFactory):
        self.parent = parent

    def __repr__(self):
        return f"调用 [[green]{self.NAME} - {self.__class__.__name__}[/]] 打包工具"

    @property
    def info(self):
        return self.parent.info

    @property
    def dependencies(self):
        return self.info.dependencies

    def pack(self): ...
