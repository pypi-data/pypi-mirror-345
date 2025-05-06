import importlib
import pathlib

import pytest

import fspacker.settings


@pytest.fixture(autouse=True)
def reload_module():
    importlib.reload(fspacker.settings)


def test_pack_mode_default_val():
    mode = fspacker.settings.PackMode()
    assert all(not v for v in (mode.debug, mode.archive, mode.offline, mode.simplify, mode.rebuild))


def test_get_cache_dir_env_set(monkeypatch, tmp_path):
    """测试当 FSPACKER_CACHE 环境变量被设置时，get_cache_dir 返回正确路径"""

    monkeypatch.setenv("FSP_DIRS__CACHE", str(tmp_path))

    assert fspacker.settings.get_settings().dirs.cache == tmp_path


def test_get_cache_dir_env_not_set(monkeypatch):
    """测试当 FSPACKER_CACHE 环境变量未设置时，get_cache_dir 返回默认路径"""

    monkeypatch.delenv("FSP_DIRS__CACHE", raising=False)
    expected_path = pathlib.Path("~").expanduser() / ".cache" / "fspacker"

    assert fspacker.settings.get_settings().dirs.cache == expected_path


def test_get_libs_dir_env_set(monkeypatch, tmp_path):
    """测试当 FSPACKER_LIBS 环境变量被设置且路径存在时，get_libs_dir 返回正确路径"""

    monkeypatch.setenv("FSP_DIRS__LIBS", str(tmp_path))
    tmp_path.mkdir(exist_ok=True)

    assert fspacker.settings.get_settings().dirs.libs == tmp_path


def test_get_libs_dir_env_not_set(monkeypatch):
    """测试当 FSPACKER_LIBS 环境变量未设置时，get_libs_dir 返回默认路径"""

    monkeypatch.delenv("FSP_DIRS__CACHE", raising=False)
    monkeypatch.delenv("FSP_DIRS__LIBS", raising=False)

    expected_path = fspacker.settings.get_settings().dirs.cache / "libs-repo"
    assert fspacker.settings.get_settings().dirs.libs == expected_path


def test_get_xxx_dir_creates_directory(monkeypatch, tmp_path):
    """测试当缓存目录不存在时，get_cache_dir 是否创建目录"""

    cache_dir = tmp_path / "nonexistent_cache"
    monkeypatch.setenv("FSP_DIRS__CACHE", str(cache_dir))

    assert not cache_dir.exists()

    fspacker.settings.get_settings()

    assert cache_dir.exists()
