import uuid
import re
from typing import List, Dict, Any
from os.path import isfile, join
from os import listdir, remove, path


def get_random_string(string_length: int = 10):
    return uuid.uuid4().hex.lower()[:string_length]


def index_find(string: str, start: str, end: str) -> str:
    return string[string.find(start) + len(start):string.rfind(end)]


def get_variable(content: str) -> List:
    return re.findall('<start>(.*?)<end>', content)


def partition_find(string, start, end):
    return string.partition(start)[2].rpartition(end)[0]


def get_value_by_key(content_dict: Dict, key: str) -> Any:
    _result = []
    try:
        def _dfs(cont_dict: Dict) -> Any:
            for _ind, _val in cont_dict.items():
                if _ind == key:
                    _result.append(_val)
                if isinstance(_val, List):
                    for _item in _val:
                        if isinstance(_item, Dict):
                            _dfs(_item)
                if isinstance(_val, Dict):
                    _dfs(_val)
        if isinstance(content_dict, Dict):
            _dfs(content_dict)
        else:
            raise "Something is wrong in get_value_by_key, pass-in value is not a dictionary"
        return _result
    except Exception as err:
        raise err


def get_all_file_in_dir(dirpath):
    return [f for f in listdir(dirpath) if isfile(join(dirpath, f))]


def remove_file(filepath):
    try:
        if path.exists(filepath):
            remove(filepath)
    except Exception as err:
        raise err
