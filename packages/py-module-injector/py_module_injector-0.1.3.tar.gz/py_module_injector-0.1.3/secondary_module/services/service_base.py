from python_module import Inject
from secondary_module.services import Provider


@Inject
class ServiceBase:
    def __init__(self, provider: Provider, fruit = None):
        self.provider = provider

    def get_log(self):
        log = self.provider.get()
        self.provider.set_log("Log alterado!")
        return log