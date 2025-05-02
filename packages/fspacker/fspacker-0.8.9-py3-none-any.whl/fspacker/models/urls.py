from functools import cached_property
from typing import Dict

from pydantic import BaseModel

from fspacker.utils.url import get_fastest_url

_embed_url_prefixes: Dict[str, str] = dict(
    official="https://www.python.org/ftp/python/",
    huawei="https://mirrors.huaweicloud.com/python/",
)

_pip_url_prefixes: Dict[str, str] = dict(
    aliyun="https://mirrors.aliyun.com/pypi/simple/",
    tsinghua="https://pypi.tuna.tsinghua.edu.cn/simple/",
    ustc="https://pypi.mirrors.ustc.edu.cn/simple/",
    huawei="https://mirrors.huaweicloud.com/repository/pypi/simple/",
)


class Urls(BaseModel):
    embed: str = ""
    pip: str = ""

    def __str__(self):
        return f"embed=[[green bold]{self.embed}[/]], pip=[[green bold]{self.pip}[/]]"

    @cached_property
    def fastest_pip_url(self) -> str:
        """Get fastest pip url if local config is empty."""

        self.pip = self.pip or get_fastest_url(_pip_url_prefixes)
        return self.pip

    @cached_property
    def fastest_embed_url(self) -> str:
        """Get fastest embed python url if local config is empty."""

        self.embed = self.embed or get_fastest_url(_embed_url_prefixes)
        return self.embed
