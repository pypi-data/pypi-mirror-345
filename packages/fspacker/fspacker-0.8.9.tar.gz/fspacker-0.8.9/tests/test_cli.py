import os
import shutil

import pytest

from fspacker.cli import app
from fspacker.settings import get_settings


@pytest.fixture(autouse=True)
def enter_examples_dir(dir_examples):
    os.chdir(dir_examples)


@pytest.fixture(autouse=True)
def clear_dist_folders(dir_ex00_simple):
    """Clear dist folder in ex00."""

    dist_dir = dir_ex00_simple / "dist"
    if dist_dir.exists():
        print(f"Clear dist folder: {dist_dir}")
        shutil.rmtree(dist_dir, ignore_errors=True)


def test_build_command(typer_runner):
    # Build normal
    result = typer_runner.invoke(app, ["b", "ex00"])
    assert result.exit_code == 0
    assert get_settings().mode.archive is False
    assert get_settings().mode.debug is False
    assert get_settings().mode.offline is False
    assert get_settings().mode.rebuild is False
    assert get_settings().mode.simplify is False
    assert get_settings().mode.use_tk is False


def test_build_command_archive_rebuild(typer_runner):
    # Build with archive and rebuild
    result = typer_runner.invoke(app, ["b", "--archive", "--rebuild", "ex00"])
    assert result.exit_code == 0
    assert get_settings().mode.archive is True
    assert get_settings().mode.rebuild is True


def test_build_command_invalid_match_name(typer_runner, dir_ex00_simple, caplog):
    os.chdir(dir_ex00_simple)

    result = typer_runner.invoke(app, ["b", "invalid_match_name"])
    assert result.exit_code == 0
    assert "未找到匹配项目" in caplog.text


def test_version_command(typer_runner, mocker):
    mocker.patch("fspacker.__version__", "1.0.0")
    mocker.patch("fspacker.__build_date__", "2024-01-01")

    result = typer_runner.invoke(app, ["v"])
    assert "fspacker 1.0.0" in result.stdout
    assert "构建日期: 2024-01-01" in result.stdout
    assert result.exit_code == 0


def test_run_command(typer_runner, dir_ex00_simple):
    # Run before build, raise error
    result = typer_runner.invoke(app, ["r"])
    assert result.exit_code != 0

    # Build
    result = typer_runner.invoke(app, ["b", "ex00"])
    assert result.exit_code == 0

    # Run
    result = typer_runner.invoke(app, ["r", "ex00"])
    assert result.exit_code == 0


def test_clean_command(typer_runner, dir_ex00_simple):
    # Build
    result = typer_runner.invoke(app, ["b", "ex00"])
    assert result.exit_code == 0

    # Clean
    os.chdir(dir_ex00_simple)
    result = typer_runner.invoke(app, ["c"])
    assert not (dir_ex00_simple / "dist").exists()
