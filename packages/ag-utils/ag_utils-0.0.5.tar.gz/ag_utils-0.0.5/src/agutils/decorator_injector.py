from functools import update_wrapper, wraps
from typing import (Any, Callable, Generic, ParamSpec, Sequence, Tuple,
                    TypeAlias, TypeVar, Union, overload)

T = TypeVar("T")
P = ParamSpec("P")


class All:...
_decorator: TypeAlias = Callable[P, T]



class DecoratorInjector(Generic[T]):

    ALL = All()

    def __init__(self, *decorators:Tuple[Callable[P, T]]):
        for decorator in decorators:
            self.__mark_as_decorator__(decorator)
        self.__decorators = decorators

    def _getattr_wrapper(self, func:Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(instance:object, name:str) -> T:
            attr = func(instance, name)
            if callable(attr):
                for decorator in self.__decorators:
                    if not self.__is_skipped__(attr, decorator):
                        attr = decorator(attr)
            return attr
        return wrapper


    def __call__(self, cls:type[T]) -> T:
        cls.__getattribute__ = self._getattr_wrapper(cls.__getattribute__)
        return cls

    @classmethod
    def __mark_as_decorator__(cls, func:Callable[P, T]) -> None:
        if callable(func):
            setattr(func, '__isdecorator__', True)

    @classmethod
    def __is_decorator__(cls, func:Callable[P, T]) -> bool:
        if callable(func):
            return getattr(func, '__isdecorator__', False)
        return False

    @classmethod
    def __add_skipped__(cls, func:Callable[P, T], *decorators:Tuple[Callable]) -> None:
        if not hasattr(func, '__skipped__'):
            func.__skipped__ = []

        all_f = list(filter(lambda el: isinstance(el ,All), decorators))
        if all_f:
            func.__skipall__ = True
            func.__skipped__ = []
        else:
            func.__skipall__ = False
            for decorator in decorators:
                if cls.__is_decorator__(decorator):
                    func.__skipped__.append(decorator)

    @classmethod
    def __is_skipped__(cls, func:Callable[P, T], decorator:Callable) -> bool:
        all_skip = getattr(func, '__skipall__', False)
        if all_skip: return True
        skip_list = getattr(func, '__skipped__', [])
        return decorator in skip_list

    @classmethod
    def __skip_wrapper__(cls, decorators:Sequence[_decorator]=[ALL]) -> Callable[P, T]:
        def func_wrapper(func:Callable[P, T]) -> Callable[P, T]:
            cls.__add_skipped__(func, *decorators)
            @wraps(func)
            def main_wrapper(*args:P.args, **kwargs:P.kwargs) -> T:
                return func(*args, **kwargs)
            return main_wrapper
        return func_wrapper


    @classmethod
    def skip(cls, func:Callable[P, T] = None, * , decorators: Union[All, Sequence[Callable]] = ALL) -> Callable[P, T]:

        if not isinstance(decorators, Sequence):
            decorators = (decorators, )
        decorators = list(decorators)
        if cls.__is_decorator__(func):
            decorators.append(func)
        decorators = list(set(decorators))

        wrapper = cls.__skip_wrapper__(decorators=decorators)
        if func and not cls.__is_decorator__(func):
            return wrapper(func)
        return wrapper






