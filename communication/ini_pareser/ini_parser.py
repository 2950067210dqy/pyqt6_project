import configparser
from loguru import logger


class ini_parser():
    """
    ini文件读取器
    """

    def __init__(self):

        # 创建 ConfigParser 对象
        self.config = configparser.ConfigParser()
        self.file_path = None
        # config是否已经读取数据
        self.is_read = False

    def is_exist(self, section: str = None, dict: str = None, value: str = None):
        """
        :param section:ini文件的节值
        :param dict:ini文件该节值的键值对的键
        :param value:ini文件该节值的键值对的值
        :return:是否存在 True or False
        """
        if self.is_read:
            if 'database' in self.config:
                print("数据库配置存在")

            if self.config.has_option('server', 'timeout'):
                timeout = self.config.getint('server', 'timeout')
        else:
            logger.error(f"ini配置器还未读取数据，无法判断是否存在[{section}]{dict}={value}")
            return False

    def read(self, filepath: str = None):
        """
        获取ini文件的内容
        :param filepath (str) 文件地址
        :return 返回ini文件内容
        """
        if filepath == None and self.file_path == None:
            # 未设置文件地址参数
            logger.error("未设置ini读取器的文件地址参数file_path！")
            return None
        if filepath != None:
            # 覆盖参数
            self.file_path = filepath
        # 读取 INI 文件
        try:
            self.config.read('config.ini')
        except:
            pass
        finally:
            pass
        self.is_read = True
        # 获取所有节的名称
        sections = self.config.sections()
        return sections
        pass

    def read_sections(self, filepath: str = None):
        """
        获取ini文件的节
        :param filepath (str) 文件地址
        :return 返回ini文件的节
        """
        if filepath == None and self.file_path == None:
            # 未设置文件地址参数
            logger.error("未设置ini读取器的文件地址参数file_path！")
            return None
        if filepath != None:
            # 覆盖参数
            self.file_path = filepath
        # 读取 INI 文件
        self.config.read('config.ini')
        self.is_read = True
        # 获取所有节的名称
        sections = self.config.sections()  # 输出: [section,....]
        return sections
        pass

    def set_file_path(self, filepath: str = ""):
        """
        设置读取器的文件地址
        :param filepath (str) 需要读取的文件地址
        :return:无返回
        """
        self.file_path = filepath
