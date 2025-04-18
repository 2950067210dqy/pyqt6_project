from communication.communication import communication


class communication_root():
    """
    这是用来串口通讯的入口类
    """

    def __init__(self):
        """
            类实例化函数
            :param
            :return 无返回值
        """
        self.communication_thread = communication()
        pass

    def start(self):
        """
        串口线程通讯开始
        :return:
        """
        self.communication_thread.start()

    pass
