from typing import (Callable, Generic, ParamSpec, Tuple, TypeVar, Union,
                    overload)

T = TypeVar('T')
P = ParamSpec('P')

class Interface(Generic[P, T]):
    @overload
    def __class_getitem__(cls, Type:Union[type, Tuple[type]]) -> type[T]:...
    @overload
    def __init__(self, cls:Callable[P, T], bases:tuple = None, params:dict = None) -> None:...
    @overload
    def __call__(self, *args:P.args, **kwargs:P.kwargs) -> T:...
    @overload
    def __description__(self,*, showdoc:bool=False, prnt:bool=True) -> str:...
    @overload
    def __repr__(self) -> str:...

