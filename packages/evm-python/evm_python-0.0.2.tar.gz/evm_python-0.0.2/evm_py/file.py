def read_file(file_path: str, split: str = '\n'):
    contents = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip(split)
            if line == '':
                continue
            contents.append(line)
    return contents


import os
from pathlib import Path


def get_data_path(file_name: str):
    home_directory = os.environ.get("HOME")
    return Path(home_directory).joinpath('data', file_name)


def get_file_data(file_name: str, split: str = '\n'):
    return read_file(file_path=get_data_path(file_name=file_name), split=split)


import json


def get_json(file_path: str):
    with open(file_path, 'r') as f:
        return json.load(f)


def get_json_data(file_name: str):
    return get_json(file_path=get_data_path(file_name=file_name))
