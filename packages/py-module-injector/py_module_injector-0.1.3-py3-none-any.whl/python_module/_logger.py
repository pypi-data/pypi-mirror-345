import logging

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m',# Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m'# Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        # Aplica a cor no nível do log e na mensagem
        log_message = super().format(record)
        
        color = self.COLORS.get(record.levelname, self.RESET)
        colored_message = f"{color}{log_message}{self.RESET}"
        return colored_message

import logging
import threading

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m',# Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m'# Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        # Aplica a cor no nível do log e na mensagem
        log_message = super().format(record)
        
        color = self.COLORS.get(record.levelname, self.RESET)
        colored_message = f"{color}{log_message}{self.RESET}"
        return colored_message

class Logger(logging.Logger):
    def __init__(self):
        super().__init__("DynamicLogger")  # Nome genérico
        handler = logging.StreamHandler()
        # Usando o ColoredFormatter para colorir a mensagem
        formatter = ColoredFormatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.addHandler(handler)
        self.setLevel(logging.DEBUG)

    def message(self, message):
        # Chama diretamente o log ao invés de usar debug()
        self.log(logging.DEBUG, message)

    def error(self, message):
        # Chama diretamente o log ao invés de usar error()
        self.log(logging.ERROR, message)

    def success(self, message):
        # Chama diretamente o log ao invés de usar info()
        self.log(logging.INFO, message)

    def info(self, message):
        # Chama diretamente o log ao invés de usar info()
        self.log(logging.INFO, message)