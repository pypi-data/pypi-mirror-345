import hashlib
import pathlib

import requests

from fspacker.utils.checksum import calc_checksum
from fspacker.utils.url import check_url_access_time
from fspacker.utils.url import get_fastest_url


def test_calc_checksum_valid_file(tmpdir):
    """Calculate checksum for a valid file."""

    test_file = tmpdir / "test_file.txt"
    test_file.write("test content")
    checksum = calc_checksum(pathlib.Path(test_file))

    expected_checksum = hashlib.sha256(b"test content").hexdigest()
    assert checksum == expected_checksum


def test_calc_checksum_file_not_found():
    """Calculate checksum for a non-existent file."""

    non_existent_file = pathlib.Path("non_existent_file.txt")
    checksum = calc_checksum(non_existent_file)
    assert checksum == ""


def test_calc_checksum_empty_file(tmpdir):
    """Calculate checksum for an empty file."""
    test_file = tmpdir / "empty_file.txt"
    test_file.write("")
    checksum = calc_checksum(pathlib.Path(test_file))

    expected_checksum = hashlib.sha256(b"").hexdigest()
    assert checksum == expected_checksum


def test_calc_checksum_different_block_size(tmpdir):
    """Calculate checksum with a different block size."""
    test_file = tmpdir / "test_file.txt"
    test_file.write("test content")
    checksum = calc_checksum(pathlib.Path(test_file), block_size=2)

    expected_checksum = hashlib.sha256(b"test content").hexdigest()
    assert checksum == expected_checksum


def test_calc_checksum_os_error(mocker, tmpdir):
    """Calculate checksum when an OSError occurs."""

    test_file = tmpdir / "test_file.txt"
    test_file.write("test content")
    test_file_path = pathlib.Path(test_file)

    mocker.patch("builtins.open", side_effect=OSError("Mocked OSError"))

    checksum = calc_checksum(test_file_path)
    assert checksum == ""


def test_check_url_access_time_success(mocker):
    """测试 check_url_access_time 函数在请求成功时返回访问时间"""

    mocker_get = mocker.patch("requests.get")
    mocker_get.return_value.status_code = 200

    url = "https://example.com"
    time_used = check_url_access_time(url)
    assert time_used < 0.1  # 假设访问时间小于0.1秒


def test_check_url_access_time_failure(mocker):
    """测试 check_url_access_time 函数在请求失败时返回 -1"""

    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("请求失败"))

    url = "https://example.com"
    time_used = check_url_access_time(url)
    assert time_used == -1


def test_check_url_access_time_timeout(mocker):
    """测试 check_url_access_time 函数在请求超时时返回 -1"""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout("请求超时"))

    url = "https://example.com"
    time_used = check_url_access_time(url)

    assert time_used == -1


def test_get_fastest_url_success(mocker):
    """测试 get_fastest_url 函数在所有 URL 都能访问时返回最快的 URL"""
    urls = {
        "url1": "https://example.com/url1",
        "url2": "https://example.com/url2",
        "url3": "https://example.com/url3",
    }
    mocker.patch("fspacker.utils.url.check_url_access_time", side_effect=[0.1, 0.2, 0.3])
    fastest_url = get_fastest_url(urls)
    assert fastest_url == "https://example.com/url1"


def test_get_fastest_url_one_failure(mocker):
    """测试 get_fastest_url 函数在有一个 URL 访问失败时返回最快的 URL"""
    urls = {
        "url1": "https://example.com/url1",
        "url2": "https://example.com/url2",
        "url3": "https://example.com/url3",
    }
    mocker.patch("fspacker.utils.url.check_url_access_time", side_effect=[-1, 0.2, 0.3])
    fastest_url = get_fastest_url(urls)
    assert fastest_url == "https://example.com/url2"


def test_get_fastest_url_all_failure(mocker):
    """测试 get_fastest_url 函数在所有 URL 都访问失败时返回空字符串"""
    urls = {
        "url1": "https://example.com/url1",
        "url2": "https://example.com/url2",
        "url3": "https://example.com/url3",
    }
    mocker.patch("fspacker.utils.url.check_url_access_time", side_effect=[-1, -1, -1])
    fastest_url = get_fastest_url(urls)
    assert fastest_url == ""


def test_get_fastest_url_empty_urls(mocker):
    """测试 get_fastest_url 函数在 URL 列表为空时返回空字符串"""
    urls = {}
    fastest_url = get_fastest_url(urls)
    assert fastest_url == ""
