# coding=utf-8
import yaml
import os


class YamlParser():

    def __init__(self, file_path=None):
        self.file_path = file_path
        pass

    def set_file_path(self, file_path=None):
        self.file_path = file_path

    def load_single(self, file_path):
        with open(file_path, "r", encoding="UTF-8") as f:
            return yaml.safe_load(f)

    def load_mutiple(self, file_path):
        with open(file_path, "r", encoding="UTF-8") as f:
            return yaml.safe_load_all(f.read(f))

    def save(self, file_path: str = None, save_data: object = None):
        with open(file_path, 'w', encoding="UTF-8") as fl:
            yaml.safe_dump_all(save_data, fl, encoding='utf-8')
        pass


class YamlParserObject():
    yaml_parser = YamlParser()