from __future__ import annotations

from datetime import datetime
from functools import wraps
from logging import (CRITICAL, DEBUG, ERROR, INFO, WARN, WARNING, FileHandler,
                     Formatter, Handler, Logger, LoggerAdapter, StreamHandler)
from logging.handlers import (HTTPHandler, QueueHandler, RotatingFileHandler,
                              SMTPHandler, SocketHandler,
                              TimedRotatingFileHandler)
from sys import stdout
from typing import Iterable, Tuple
from uuid import uuid4

from .classproperty import classproperty


class LogMeta(type):


    class DefaultConfig:
        level = INFO
        handlers = [StreamHandler(stdout)]
        fmt = Formatter(
            style='{',
            datefmt='%Y-%m-%d %H:%M:%S',
            fmt='{asctime} - {levelname} - {LoggerName} - {message}'
        )

    def __init__(self, name:str, bases:Tuple, params:dict):
        self._logger = Logger(name=f'{name}.{uuid4().hex}.meta', level=DEBUG)
        self.__config_logger(params)
        self._logger_a = LoggerAdapter(self._logger, {"LoggerName": name})
        super(LogMeta, self).__init__(name, bases, params)

    def __call__(self, *args, **kwargs) -> LogMeta:
        raise ValueError('Cannot create instance')

    def __config_logger(self, params:dict) -> None:
        config = params.get('Config', self.DefaultConfig)

        level = getattr(config, 'level', self.DefaultConfig.level)
        if level not in [DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL]:
            level = self.DefaultConfig.level

        fmt = getattr(config, 'fmt', self.DefaultConfig.fmt)
        if not isinstance(fmt, Formatter):
            fmt = self.DefaultConfig.fmt

        handlers = getattr(config, 'handlers', self.DefaultConfig.handlers)
        if not isinstance(handlers, Iterable):
            handlers = self.DefaultConfig.handlers


        for h in handlers:
            if not isinstance(h, Handler):
                continue
            h.setLevel(level)
            h.setFormatter(fmt)
            self._logger.addHandler(h)

    def debug(self, message:object, *args, **kwargs):
        self._logger_a.debug(message, *args, **kwargs)

    def info(self, message:object, *args, **kwargs):
        self._logger_a.info(message, *args, **kwargs)

    def warning(self, message:object, *args, **kwargs):
        self._logger_a.warning(message, *args, **kwargs)

    def error(self, message:object, *args, **kwargs):
        self._logger_a.error(message, *args, **kwargs)

    def critical(self, message:object, *args, **kwargs):
        self._logger_a.critical(message, *args, **kwargs)

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

    @classproperty
    def level(cls) -> LogLevels:
        return LogLevels

    @classproperty
    def handler(cls) -> Handlers:
        return Handlers

    @classmethod
    def __decorator(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                cls.debug(f'Call func {func.__name__}. Args: {args}. Kwargs: {kwargs}')
                start = datetime.now()
                result = func(*args, **kwargs)
                ptime = (datetime.now() - start).microseconds/1000
                cls.debug(f'Func {func.__name__} work {ptime}ms and return {result}')
                return result
            except Exception as ex:
                cls.error(ex)
                raise ex
        return wrapper

    @classmethod
    def __getattribute(cls, func):
        @wraps(func)
        def wrapper(self, name:str):
            result = func(self, name)
            if callable(result):
                result = cls.__decorator(result)
            return result
        return wrapper

    @classmethod
    def inject(cls, obj:type):
        if not isinstance(obj, type):
            cls.warning(f'Cannot inject to {obj}. Value must be `type`')
            return
        try:
            obj.__getattribute__ = cls.__getattribute(obj.__getattribute__)
        except Exception as ex:
            cls.warning(f'Cannot inject to {obj}. {ex}')

    @classmethod
    def wrap(cls, obj:type):
        cls.inject(obj)
        return obj

    class Config:
        level = INFO
        handlers = [StreamHandler(stdout)]
        fmt = Formatter(
            style='{',
            datefmt='%Y-%m-%d %H:%M:%S',
            fmt='{asctime} - {levelname} - {LoggerName} - {message}'
        )


