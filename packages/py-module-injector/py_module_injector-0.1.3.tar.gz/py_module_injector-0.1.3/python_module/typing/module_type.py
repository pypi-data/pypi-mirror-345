from typing import Callable, Dict, Any


class RegisterModuleType:
    implementation: Dict[str, Dict[str, Any]] = {}
    factory: Callable = None

    def __init__(self, implementation: Dict[str, Dict[str, Any]] = {}, factory: Callable = None):
        self.implementation = implementation
        self.factory = factory


class ModuleType:
    def __init__(self):
        self._modules: Dict[str, Dict[str, Any]] = {}

    def __getitem__(self, key: str) -> Dict[str, Any]:
        return self._modules.get(key, {})

    def __setitem__(self, key: str, value: Any):
        self._modules[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._modules

    def keys(self):
        return self._modules.keys()