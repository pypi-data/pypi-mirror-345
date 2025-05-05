
from sys import stderr, stdout


class ColoredConsoleMessage:
    RED   = "\033[1;31m"
    BLUE  = "\033[1;34m"
    CYAN  = "\033[1;36m"
    GREEN = "\033[0;32m"
    YELLOW = "\x1b[1;33m"
    RESET = "\033[0;0m"
    BOLD    = "\033[;1m"
    REVERSE = "\033[;7m"

    @classmethod
    def set(cls, color:str) -> None:
        stdout.write(color)
        stderr.write(color)

    @classmethod
    def reset(cls) -> None:
        stdout.write(cls.RESET)
        stderr.write(cls.RESET)

    @classmethod
    def colored(cls, color:str, message:str, end:str='\n') -> None:
        cls.set(color)
        print(message, end=end)
        cls.reset()

    @classmethod
    def red(cls, message:str, end:str='\n') -> None:
        cls.colored(cls.RED, message, end)

    @classmethod
    def green(cls, message:str, end:str='\n') -> None:
        cls.colored(cls.GREEN, message, end)

    @classmethod
    def yellow(cls, message:str, end:str='\n') -> None:
        cls.colored(cls.YELLOW, message, end)

    @classmethod
    def cyan(cls, message:str, end:str='\n') -> None:
        cls.colored(cls.CYAN, message, end)

    @classmethod
    def bold(cls, message:str, end:str='\n') -> None:
        cls.colored(cls.BOLD, message, end)

    @classmethod
    def plain(cls, message:str, end:str='\n') -> None:
        print(message, end=end)

    @classmethod
    def warn(cls, error:str=None, end:str='\n') -> None:
        if error:
            cls.colored(cls.YELLOW, 'WARN', '')
            cls.reset()
            print(f' [{error}]')
        else:
            cls.colored(cls.YELLOW, 'WARN', end)

    @classmethod
    def fail(cls, error:str=None, end:str='\n', close:bool=True) -> None:
        if error:
            cls.colored(cls.RED, 'FAIL', '')
            cls.reset()
            print(f' [{error}]')
        else:
            cls.colored(cls.RED, 'FAIL', end)
        if close:
            exit(1)

    @classmethod
    def ok(cls, end:str='\n') -> None:
        cls.colored(cls.GREEN, 'OK', end)

    @classmethod
    def up(cls, end:str='\n') -> None:
        cls.colored(cls.GREEN, 'UP', end)

    @classmethod
    def down(cls, end:str='\n') -> None:
        cls.colored(cls.RED, 'DOWN', end)

    @classmethod
    def command(cls, message:str, end:str='') -> None:
        cls.reset()
        message = f'{message:.<70}'
        if not message.endswith('.'):
            message = f'{message}...'
        print(message, end=end)