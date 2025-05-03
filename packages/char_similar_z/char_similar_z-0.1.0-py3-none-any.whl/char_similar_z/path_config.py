import importlib.resources as pkg_resources
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from . import data  # 确保你的 data 是个 Python 包，包含所需 .dict 文件


def get_path(filename: str) -> Path:
    return pkg_resources.files(data).joinpath(filename)


def load_json(path: Path | str, parse_int: Optional[Any] = None) -> Any:
    if isinstance(path, str):
        path = Path(path)
    assert path.is_file(), f"File {path} does not exist."

    with path.open(mode="r", encoding="utf-8") as f:
        return json.load(f, parse_int=parse_int)


# 文件名映射
FILENAMES = {
    "component": "char_component.dict",
    "fourangle": "char_fourangle.dict",
    "frequency": "char_frequency.dict",
    "number": "char_number.dict",
    "pinyin": "char_pinyin.dict",
    "stroke": "char_stroke.dict",
    "struct": "char_struct.dict",
    "order": "char_order.dict",
}


def get_dict(name: str) -> Dict[str, Any]:
    if name not in FILENAMES:
        raise ValueError(f"Dictionary {name} not found.")
    return load_json(get_path(FILENAMES[name]))
