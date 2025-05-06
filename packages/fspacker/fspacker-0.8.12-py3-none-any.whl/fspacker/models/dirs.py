from pathlib import Path
from typing import Tuple

from pydantic import BaseModel

__all__ = ["default_cache_dir", "Dirs"]

# cache settings
default_cache_dir = Path("~").expanduser() / ".cache" / "fspacker"


class Dirs(BaseModel):
    cache: Path = default_cache_dir
    embed: Path = cache / "embed-repo"
    libs: Path = cache / "libs-repo"
    checksum: str = ""

    def __str__(self):
        return f"cache=[{self.cache}], embed=[{self.embed}], libs=[{self.libs}]"

    @property
    def entries(self) -> Tuple[Path]:
        return (self.cache, self.embed, self.libs)
