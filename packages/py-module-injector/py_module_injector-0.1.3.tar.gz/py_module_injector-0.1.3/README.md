# python-module
Uma biblioteca de modularização em Python que fornece funcionalidades para injeção de dependências e registro de módulos, facilitando a criação de sistemas modulares e extensíveis.

## Instalação
Para instalar a biblioteca, execute o seguinte comando no terminal:
```
pip install .
```

## Uso
Injeção de Dependências
A biblioteca oferece suporte à injeção de dependências, permitindo que você registre e injete automaticamente as dependências necessárias em classes e métodos.

Exemplo de uso da injeção de dependências em uma classe:

```
from python_module import Inject

@Inject
class ServiceBase:
    def __init__(self, provider: Provider):
        self.provider = provider

    def get_log(self):
        return self.provider.get_log()
```

## Registro de Módulos
Com o decorador ``@Module``, você pode registrar módulos e suas dependências no injetor de dependências. Esse registro permite que você defina quais implementações ou fábricas serão utilizadas em diferentes partes do seu aplicativo.

Exemplo de uso do decorador Module:

```
from python_module import Module
from python_module.typing import RegisterModuleType

@Module(
    module_name="ExampleModule",
    instances=[
        RegisterModuleType(
            implementation=Provider,  # Deve ser uma referência à classe, não uma string
            factory=lambda: Provider(log="Provider Injetado")
        )
    ]
)
class ExampleModule:
    def run(self):
        service = Service()
        return service.process()

if __name__ == '__main__':
    example_module = ExampleModule()
    print(example_module.run())
```
## Testes
Para rodar os testes da biblioteca, execute o seguinte comando:

```
python -m unittest discover -s tests
```
Isso irá descobrir e rodar todos os testes na pasta tests.

## Contribuição
Sinta-se à vontade para contribuir com melhorias, correções de bugs ou novas funcionalidades! Para isso, basta fazer um fork do repositório, criar uma nova branch e enviar um pull request