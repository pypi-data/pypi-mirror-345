from typing import (Callable, Generic, ParamSpec, Sequence, Tuple, TypeAlias,
                    TypeVar, overload)

T = TypeVar("T")
P = ParamSpec("P")


class All:...
_decorator: TypeAlias = Callable[P, T]

class DecoratorInjector(Generic[T]):
    """
    Used to wrap all methods of a class into a list of decorators
    ```python
    def d1(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def d2(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @DecoratorInjector(d1, d2)
    class MyClass:...

    ```
    """
    @overload
    def __init__(self, *decorators:Tuple[_decorator]) -> None:...
    @overload
    def __call__(self, cls:type[T]) -> T:...
    @classmethod
    @overload
    def skip(cls, func:Callable[P, T]) -> Callable[P, T]:...
    @classmethod
    @overload
    def skip(cls, decorators:All) ->  Callable[P, T]:...
    @classmethod
    @overload
    def skip(cls, decorators:_decorator) ->  Callable[P, T]:...
    @classmethod
    @overload
    def skip(cls, decorators:Sequence[_decorator]) ->  Callable[P, T]:...
