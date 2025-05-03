import importlib.resources as pkg_resources
import logging
import json
from . import data


def get_path(filename):
    """
    Get the path of the file in the package.
    Args:
        filename: The name of the file.
    Returns:
        The path of the file.
    """
    return pkg_resources.files(data).joinpath(filename)


def txt_write(lines, path, model="w", encoding="utf-8"):
    """
    Write Line of list to file
    Args:
        lines: lines of list<str> which need save
        path: path of save file, such as "txt"
        model: type of write, such as "w", "a+"
        encoding: type of encoding, such as "utf-8", "gbk"
    """

    try:
        file = open(path, model, encoding=encoding)
        file.writelines(lines)
        file.close()
    except Exception as e:
        logging.info(str(e))
        print("Error: ", str(e))


def txt_read(path, encoding="utf-8"):
    """
    Read Line of list form file
    Args:
        path: path of save file, such as "txt"
        encoding: type of encoding, such as "utf-8", "gbk"
    Returns:
        dict of word2vec, eg. {"macadam":[...]}
    """

    lines = []
    try:
        with open(path, "r", encoding=encoding) as file:
            lines = file.readlines()
    except FileNotFoundError:
        logging.info("File not found: %s", path)
    finally:
        return lines


def save_json(jsons, json_path, indent=4):
    """
        保存json
    Args:
        path[String]:, path of file of save, eg. "corpus/xuexiqiangguo.lib"
        jsons[Json]: json of input data, eg. [{"桂林": 132}]
        indent[int]: pretty-printed with that indent level, eg. 4
    Returns:
        None
    """
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(jsons, ensure_ascii=False, indent=indent))


def load_json(path, parse_int=None):
    """
        加载json
    Args:
        path_file[String]:, path of file of save, eg. "corpus/xuexiqiangguo.lib"
        parse_int[Boolean]: equivalent to int(num_str), eg. True or False
    Returns:
        data[Any]
    """
    with open(path, mode="r", encoding="utf-8") as f:
        model_json = json.load(f, parse_int=parse_int)
    return model_json


# path of basic
path_char_component = get_path("char_component.dict")
path_char_fourangle = get_path("char_fourangle.dict")
path_char_frequency = get_path("char_frequency.dict")
path_char_number = get_path("char_number.dict")
path_char_pinyin = get_path("char_pinyin.dict")
path_char_stroke = get_path("char_stroke.dict")
path_char_struct = get_path("char_struct.dict")
path_char_order = get_path("char_order.dict")
# 加载字典
dict_char_component = load_json(path_char_component)
dict_char_fourangle = load_json(path_char_fourangle)
dict_char_frequency = load_json(path_char_frequency)
dict_char_number = load_json(path_char_number)
dict_char_pinyin = load_json(path_char_pinyin)
dict_char_stroke = load_json(path_char_stroke)
dict_char_struct = load_json(path_char_struct)
dict_char_order = load_json(path_char_order)
