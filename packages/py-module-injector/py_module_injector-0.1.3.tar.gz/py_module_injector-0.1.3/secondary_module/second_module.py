from python_module import Inject, Module
from python_module.typing import RegisterModuleType
from secondary_module.services import Provider, Service, ServiceBase

@Module(
    instances=[
        RegisterModuleType(
            implementation=Provider,  # Deve ser uma referência à classe, não uma string
            factory=lambda: Provider(log="Provider Injetado")
        ),
        RegisterModuleType(
            implementation=ServiceBase  # Outra instância
        )
    ]
)
class ModuleExemple:
    def run(self):
        service = Service(fruit="Banana")
        return service.process()
