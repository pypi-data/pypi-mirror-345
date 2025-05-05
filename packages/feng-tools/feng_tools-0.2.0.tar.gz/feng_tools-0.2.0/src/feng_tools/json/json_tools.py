"""
JSON工具
"""
import json
from typing import Any, Union


def read_json(file_path: str) -> dict:
    """
    读取JSON文件
    :param file_path: JSON文件路径
    :return: 解析后的字典对象
    :raises: FileNotFoundError, json.JSONDecodeError
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件未找到: {file_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"JSON解析失败: {e.msg}", e.doc, e.pos)


def write_json(data: Any, file_path: str) -> bool:
    """
    写入JSON文件
    :param data: 要写入的数据
    :param file_path: JSON文件路径
    :return: 写入是否成功
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except (OSError, TypeError) as e:
        print(f"写入JSON文件失败: {str(e)}")
        return False


def pretty_print_json(data: Any) -> None:
    """
    美化打印JSON数据
    :param data: 要打印的JSON数据
    """
    try:
        print(json.dumps(data, ensure_ascii=False, indent=4))
    except (TypeError, OverflowError) as e:
        print(f"JSON美化打印失败: {str(e)}")


def is_valid_json(data: Union[str, bytes]) -> bool:
    """
    检查字符串或字节流是否为有效的JSON
    :param data: 待检查的字符串或字节流
    :return: 是否为有效JSON
    """
    try:
        json.loads(data)
        return True
    except (json.JSONDecodeError, TypeError):
        return False
