import hashlib
import logging
import pathlib


def calc_checksum(filepath: pathlib.Path, block_size: int = 4096) -> str:
    """计算文件校验和"""

    hash_method = hashlib.sha256()
    logging.info(f"计算文件校验和: [green underline]{filepath.name}[/] [bold green]:heavy_check_mark:")

    try:
        with open(filepath, "rb") as file:
            for chunk in iter(lambda: file.read(block_size), b""):
                hash_method.update(chunk)

    except FileNotFoundError:
        logging.error(f"文件不存在: [red underline]{filepath}[/] [bold red]:white_exclamation_mark:")
        return ""
    except OSError as e:
        logging.error(f"读取文件 IO 错误: [red underline]{filepath}: {e}[/] [bold red]:white_exclamation_mark:")
        return ""

    checksum = hash_method.hexdigest()
    logging.debug(f"校验和计算值: [green underline]{checksum}[/] [bold green]:heavy_check_mark:")
    return checksum
