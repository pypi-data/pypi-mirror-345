from logging.handlers import (HTTPHandler, QueueHandler, RotatingFileHandler,
                              SMTPHandler, SocketHandler,
                              TimedRotatingFileHandler)
from typing import Tuple, overload

from .classproperty import classproperty

class LogMeta(type):
    @overload
    def __init__(self, name:str, bases:Tuple, params:dict):...
    @overload
    def __call__(self, *args, **kwargs) -> LogMeta:...
    @overload
    def debug(self, message:object, *args, **kwargs):...
    @overload
    def info(self, message:object, *args, **kwargs):...
    @overload
    def warning(self, message:object, *args, **kwargs):...
    @overload
    def error(self, message:object, *args, **kwargs):...
    @overload
    def critical(self, message:object, *args, **kwargs):...

class LogLevels:
    DEBUG = DEBUG
    INFO = INFO
    WARN = WARN
    WARNING = WARNING
    ERROR = ERROR
    CRITICAL = CRITICAL

class Handlers:
    StreamHandler = StreamHandler
    FileHandler = FileHandler
    RotatingFileHandler = RotatingFileHandler
    TimedRotatingFileHandler = TimedRotatingFileHandler
    SocketHandler = SocketHandler
    HTTPHandler = HTTPHandler
    QueueHandler = QueueHandler
    SMTPHandlers = SMTPHandler


class LoggerBase(metaclass=LogMeta):
    """
    Class for configuring a logger without creating an instance.\n
    To use, inherit the LoggerBase class:\n
    ```
    class MainLog(LoggerBase):...
    ```
    After this you can call the class anywhere:\n
    ```
    MainLog.debug('Test message')
    ```

    To configure, define the `Config` class inside (see `DefaultConfig` in `LogMeta`)\n
        ```
        class MainLog(LoggerBase):
            class Config:
                level = DEBUG
                handlers = [
                    StreamHandler(stdout),
                    FileHandler('test.log')
                ]
                fmt = Formatter(
                    style='{',
                    datefmt='%Y:%m:%d %H:%M:%S',
                    fmt='{LoggerName} - {asctime} - {levelname} - {message}'
                )
        ```

    To use the logger name, use the variable `LoggerName`
    """

    @classproperty
    @overload
    def level(cls) -> LogLevels:...

    @classproperty
    @overload
    def handler(cls) -> Handlers:...


    @classmethod
    @overload
    def inject(cls, obj:type) -> None:
        """
        The function replaces and wraps the __getattribute__ method.
        ```
        class MainLog(Loggerbase):...

        class MyClass:...

        MainLog.inject(MyClass)
        ```
        When the __getattribute__ method is called, the result obtained, if it is a function, 
        is wrapped in a decorator with a try/except block:\n
        ```
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as ex:
                cls.error(ex)
                raise ex
        ```
        """

    @classmethod
    @overload
    def wrap(cls, obj:type):
        """
        Method to inject as a decorator. Calls the `inject` method on the class being decorated.\n
        ```
        class MainLog(LoggerBase):...

        @MainLog.wrap
        class MyClass:...
        ```
        """


