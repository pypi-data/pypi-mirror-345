import logging
import ssl
import time
import typing
import urllib
from urllib.error import URLError
from urllib.parse import urlparse

import requests


def check_url_access_time(url: str) -> float:
    """测试 url 访问时间"""

    start = time.perf_counter()
    try:
        response = requests.get(url, timeout=2)
        response.raise_for_status()
        time_used = time.perf_counter() - start
        logging.info(f"地址 [[green]{url}[/]] 访问时间: [green] {time_used:.2f}s")
        return time_used
    except requests.exceptions.RequestException:
        logging.info(f"地址 [[red bold]{url}[/]] 访问超时")
        return -1


def get_fastest_url(urls: typing.Dict[str, str]) -> str:
    """获取 Embed python 最快访问链接地址"""

    min_time, fastest_url = 10.0, ""
    for embed_url in urls.values():
        time_used = check_url_access_time(embed_url)
        if time_used > 0:
            if time_used < min_time:
                fastest_url = embed_url
                min_time = time_used

    logging.info(f"找到最快地址: [[green bold]{fastest_url}[/]]")
    return fastest_url


def safe_read_url_data(url: str, timeout: int = 10) -> typing.Optional[bytes]:
    """Safely read data from a URL with HTTPS schema.

    Args:
        url: The URL to read from.
        timeout: Connection timeout in seconds.

    Returns:
        The content as bytes if successful, None otherwise.
    """
    parsed_url = urlparse(url)
    allowed_schemes = {"https"}

    try:
        if parsed_url.scheme not in allowed_schemes:
            raise ValueError(f"不支持的 URL scheme: {parsed_url.scheme}")

        context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, timeout=timeout, context=context) as response:
            return response.read(1024 * 1024 * 100)  # limited to 100MB
    except (ValueError, URLError) as e:
        logging.error(f"读取 URL 数据失败: {e}")
        return None
