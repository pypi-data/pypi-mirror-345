from setuptools import setup, find_packages
from os import path

# Obtendo o caminho do arquivo README.md
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="py-module-injector",
    version="0.1.3",
    description="Uma biblioteca de modularização em python",
    author="Cleverson Pedroso",
    author_email="cleverson212121@gmail.com",
    packages=find_packages(),
    package_data={
        "python_module": ["py.typed"],
    },
    install_requires=[
        "typing-extensions",  # Adiciona suporte para extensões de tipagem
    ],
    entry_points={
        "console_scripts": [
            "python-module = python_module.__main__:main",
        ],
    },
    long_description=long_description,
    long_description_content_type='text/markdown',  # Especificando o tipo de conteúdo como markdown
)