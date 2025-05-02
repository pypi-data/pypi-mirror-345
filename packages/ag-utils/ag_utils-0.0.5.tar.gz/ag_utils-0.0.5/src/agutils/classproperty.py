from typing import Callable, Generic, ParamSpec, TypeVar

T = TypeVar('T')



class classproperty(Generic[T]):

    def __init__(self, f:Callable[..., T]) -> None:
        self.__f = f
    def __get__(self, instance, owner) -> T:
        return self.__f(owner)