# coding=utf-8
import traceback

import yaml
import os

from loguru import logger


class YamlParser():

    def __init__(self, file_path=None):
        self.file_path = file_path
        pass

    def set_file_path(self, file_path=None):
        self.file_path = file_path

    def load_single(self, file_path):
        try:
            with open(file_path, "r", encoding="UTF-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"读取{file_path}配置文件失败！失败原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}")
            return None

    def load_mutiple(self, file_path):
        try:
            with open(file_path, "r", encoding="UTF-8") as f:
                return yaml.safe_load_all(f.read(f))
        except Exception as e:
            logger.error(f"读取{file_path}配置文件失败！失败原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}")
            return None

    def save(self, file_path: str = None, save_data: object = None):
        try:
            with open(file_path, 'w', encoding="UTF-8") as fl:
                yaml.safe_dump_all(save_data, fl, encoding='utf-8')
        except Exception as e:
            logger.error(f"保存{file_path}配置文件失败！失败原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}")


class YamlParserObject():
    yaml_parser = YamlParser()
