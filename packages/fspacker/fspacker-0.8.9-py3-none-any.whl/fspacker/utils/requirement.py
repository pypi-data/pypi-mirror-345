"""本模块包含库所需常用函数"""

import re
from typing import Optional

from packaging.requirements import InvalidRequirement
from packaging.requirements import Requirement

from fspacker.exceptions import ProjectPackError


class RequirementParser:
    @classmethod
    def normalize(cls, req_str: str) -> Optional[str]:
        """
        规范化需求字符串，处理以下特殊情况：
        1. 括号包裹的版本：shiboken2 (==5.15.2.1) -> shiboken2==5.15.2.1
        2. 不规范的版本分隔符：package@1.0 -> package==1.0
        3. 移除多余空格和注释
        """
        # 移除注释和首尾空格
        req_str = re.sub(r"#.*$", "", req_str).strip()

        # 替换不规范的版本分隔符
        req_str = re.sub(r"([a-zA-Z0-9_-]+)@([0-9.]+)", r"\1==\2", req_str)

        # 标准化版本运算符（处理 ~= 和意外的空格）
        req_str = re.sub(r"~=\s*", "~=", req_str)
        req_str = re.sub(r"([=<>!~]+)\s*", r"\1", req_str)

        # 处理括号包裹的版本 (常见于PySide生态)
        req_str = re.sub(r"[()]", "", req_str)

        # 标准化版本运算符（处理 ; 以后的内容）
        req_str = re.sub(r";.*", "", req_str)

        # 处理空白符
        req_str = re.sub(r"\s+", "", req_str)

        return req_str

    @classmethod
    def parse(cls, req_str: str) -> Optional[Requirement]:
        """安全解析需求字符串为Requirement对象"""
        normalized = cls.normalize(req_str)

        try:
            return Requirement(normalized)
        except InvalidRequirement as e:
            raise ProjectPackError(f"解析依赖失败, '{req_str}': {str(e)}") from e
