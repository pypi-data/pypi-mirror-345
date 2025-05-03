
import inspect
from typing import List, Type, TypeVar
from .typing import RegisterModuleType
from .injector_instance import Injector
from ._logger import Logger

logger = Logger()

T = TypeVar('T')


def Module(*, module_name: str = None, instances: List[RegisterModuleType] = []) -> Type:
    """
    Module decorator for registering instances in the dependency injector.

    Parameters:
        module_name (str, optional):
            - The name of the module where dependencies will be registered.
            - If not provided, the calling module's name will be used.

        instances (list):
            - A list of `RegisterModuleType` objects to be registered within the module.
            - Each `RegisterModuleType` object may contain:
                - `implementation`: The class or instance to be registered.
                - `factory`: A function or callable used to instantiate the dependency.

    Example Usage:
        @Module(
            instances=[
                RegisterModuleType(
                    implementation=Provider,
                    factory=lambda: Provider(log="Injected Provider")
                )
            ]
        )
        class ExampleModule:
            def run(self):
                service = Service()
                return service.process()
    """

    def decorator(cls):
        def __init__(self, *args, **kwargs):
            module_name = cls.__name__
            if not (instances and len(instances)):
                raise ValueError('Instances are required')
            for instance in instances:
                for instance in instances:
                    implementation = (
                        instance.implementation
                        if isinstance(instance, RegisterModuleType)
                        else instance.get("implementation", None)
                    )

                    factory = (
                        instance.factory
                        if isinstance(instance, RegisterModuleType)
                        else instance.get("factory", None)
                    )

                    if not implementation:
                        raise ValueError('Instance is required')

                    Injector.register(
                        implementation.__name__,
                        implementation,
                        module_name,
                        factory
                    )

            super(cls, self).__init__(*args, **kwargs)
        cls.__init__ = __init__
        return cls
    return decorator