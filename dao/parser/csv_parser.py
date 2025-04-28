class csv_parser():
    """
    txt解析器
    """

    def __init__(self, files_path=[]):
        """
        实例化方法
        :param files_path:文件地址list [{‘port’:'COM3','file_path':'./data/..'},....]
        """
        self.files_path = files_path
        pass
