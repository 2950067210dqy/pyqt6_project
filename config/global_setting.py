class global_setting():
    _setting = {}

    @classmethod
    def set_setting(cls, key, value):
        cls._setting[key] = value
        pass

    @classmethod
    def get_setting(cls, key):
        return cls._setting[key]

    pass
