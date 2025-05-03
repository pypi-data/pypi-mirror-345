class Provider:
    def __init__(self, log):
        self._log = log

    @classmethod
    def set_log(cls, log):
        cls._log = log
        return cls

    def get(self):
        return self._log