from secondary_module.services import ServiceBase

class Service(ServiceBase):
    def __init__(self, fruit = None):
        super().__init__(fruit=fruit)

    def process(self):
        return self.get_log()