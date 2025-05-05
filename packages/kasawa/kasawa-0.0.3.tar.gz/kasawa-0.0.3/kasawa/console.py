import os
import ctypes
from pystyle import Colors

class console:
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def title(text):
        ctypes.windll.kernel32.SetConsoleTitleW(text)

    class log:
        @staticmethod
        def info(text):
            prefix = f"{Colors.green}[INFO]{Colors.reset} "
            message = f"{Colors.white}{text}"
            print(prefix + message)

        @staticmethod
        def error(text):
            prefix = f"{Colors.red}[ERROR]{Colors.reset} "
            message = f"{Colors.white}{text}"
            print(prefix + message)

        @staticmethod
        def success(text):
            prefix = f"{Colors.green}[SUCCESS]{Colors.reset} "
            message = f"{Colors.white}{text}"
            print(prefix + message)

        @staticmethod
        def warning(text):
            prefix = f"{Colors.yellow}[WARING]{Colors.reset} "
            message = f"{Colors.white}{text}"
            print(prefix + message)

        @staticmethod
        def ask(text):
            prefix = f"{Colors.yellow}[ASK]{Colors.reset} "
            message = f"{Colors.white}{text}"
            print(prefix + message)
