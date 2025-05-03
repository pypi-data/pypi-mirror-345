import inspect
from functools import wraps

from .injector_instance import Injector
from ._logger import Logger

logger = Logger()

def Inject(target=None, module_name: str = None):
    """
    Decorator to inject dynamic dependencies into classes and __init__ methods.

    Parameters:
        module_name:
            - The name of the module where dependencies will be used.
            - If not provided, the last calling module's name registered will be used.
        target:
            - The target class where dependencies will be injected.
            - If used on an __init__ method, it applies dependency injection to its parameters.

    Usage Example:
        @Inject
        class Service:
            def __init__(self, provider: Provider):
                self.provider = provider
            def process(self):
                return 'Service processed'
    """

    if inspect.isclass(target):
        # Se for uma classe, aplicamos a injeção no __init__
        original_init = target.__init__

        @wraps(original_init)
        def wrapped_init(self, *args, **kwargs):
            # Debugging and logging
            injected_kwargs = {}
            nonlocal module_name

            # Get the signature of the __init__ method
            init_signature = inspect.signature(original_init)
            for name, param in init_signature.parameters.items():
                if name == "self":
                    continue
                # Se o parâmetro já foi fornecido, não devemos injetá-lo
                if name not in kwargs:
                    type_hint = param.annotation
                    if type_hint != param.empty:
                        # Get the instance from the Injector
                        instance = Injector.get(module_name, type_hint.__name__)
                        if instance:
                            injected_kwargs[name] = instance

            # Atualiza kwargs com os valores injetados
            kwargs.update(injected_kwargs)
            original_init(self, *args, **kwargs)

        # Substitui o __init__ original pela versão modificada
        target.__init__ = wrapped_init
        return target  # Retorna a classe modificada

    elif callable(target):
        # Se for um método, aplicamos a injeção apenas nele
        @wraps(target)
        def wrapped_function(self, *args, **kwargs):
            # Debugging and logging
            injected_kwargs = {}
            module_name = inspect.stack()[1].frame.f_globals.get('__name__', None)

            # Get the signature of the method
            func_signature = inspect.signature(target)
            for name, param in func_signature.parameters.items():
                if name == "self":
                    continue
                # Se o parâmetro já foi fornecido, não devemos injetá-lo
                if name not in kwargs:
                    type_hint = param.annotation
                    if type_hint != param.empty:
                        # Get the instance from the Injector
                        instance = Injector.get(module_name, type_hint.__name__)
                        if instance:
                            injected_kwargs[name] = instance

            # Atualiza kwargs com os valores injetados
            kwargs.update(injected_kwargs)
            return target(self, *args, **kwargs)  # Chama a função original

        return wrapped_function  # Retorna a função modificada

    else:
        # Caso o decorador seja chamado sem argumentos (ex: @Inject)
        def wrapper(inner_target):
            return Inject(inner_target)

        return wrapper
