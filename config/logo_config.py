from loguru import logger


class logger_diy():
    log = None

    @classmethod
    def add_env(cls):
        cls.log = logger
        # ：按天分割日志，保留7天，异步写入
        cls.log.add(
            "prod_{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="7 days",
            enqueue=True,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
        pass

    pass
