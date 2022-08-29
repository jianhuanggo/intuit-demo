import yaml
import json
from typing import Dict
from pathlib import Path
from os.path import isfile, join
from os import listdir, remove, path


def yaml_load(content: str) -> Dict:
    try:
        return yaml.safe_load(content)
    except Exception as err:
        raise err


def yaml_dump(filepath: str, data: Dict):
    try:
        with open(filepath, 'w') as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False)
    except Exception as err:
        raise err


def yaml_load_from_f(filepath):
    with open(filepath, "r") as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as err:
            raise err


def json_dump(filepath: str, data) -> bool:
    try:
        with open(filepath, 'w') as file:
            json.dump(data, file)
        return True
    except Exception as err:
        raise


def json_load(filepath: str) -> Dict:
    try:
        with open(filepath) as json_file:
            return json.load(json_file)
    except Exception as err:
        raise err


def json_loads(filepath: str) -> str:
    try:
        with open(filepath) as json_file:
            _data = json.load(json_file)
            return json.dumps(_data)
    except Exception as err:
        raise err


def is_file_exist(filepath):
    return Path(filepath).is_file()

def get_all_file_in_dir(dirpath):
    return [f for f in listdir(dirpath) if isfile(join(dirpath, f))]


def remove_file(filepath):
    try:
        if path.exists(filepath):
            remove(filepath)
    except Exception as err:
        raise err
