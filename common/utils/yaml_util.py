from pathlib import Path
from typing import Any

import yaml


class YamlUtil:
    """YAML 文件读 / 写 / 清空"""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def read(self) -> Any:
        """读取 YAML；文件不存在或为空时返回空字典"""
        if not self.file_path.exists():
            return {}
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return {} if data is None else data

    def write(self, data: Any) -> None:
        """覆盖写入 YAML"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

    def clear(self, empty: Any = None) -> None:
        """
        清空文件内容。
        - 默认写成 {}
        - 列表型数据可传 empty=[]
        """
        if empty is None:
            empty = {}
        self.write(empty)

    def update(self, key: str, value: Any) -> None:
        """按 key 更新（仅当根节点为 dict）"""
        data = self.read()
        if not isinstance(data, dict):
            data = {}
        data[key] = value
        self.write(data)
