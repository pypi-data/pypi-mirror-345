from .typing import ModuleType


class DependencyInjector:
    def __init__(self):
        self._modules = ModuleType()

    def register(self, name, implementation, module_name, factory = None):
        if module_name not in self._modules:
            self._modules[module_name] = {}
        if factory:
            self._modules[module_name][name] = factory()
        else:
            self._modules[module_name][name] = implementation()

    def get(self, module_name, name):
        if not module_name:
            if not self._modules:
                raise ValueError("No modules have been registered yet.")
            # Pega o último módulo registrado
            module_name = list(self._modules.keys())[-1]

        module = self._modules[module_name]

        if name in module:
            return module[name]

        raise ValueError(
            f"Instance or provider ({name}) not found in module ({module_name})"
        )