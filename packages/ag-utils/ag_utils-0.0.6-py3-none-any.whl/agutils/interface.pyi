from typing import (Callable, Generic, ParamSpec, Tuple, TypeVar, Union,
                    overload)

T = TypeVar('T')
P = ParamSpec('P')

class Interface(Generic[P, T]):
    """
    Decorator for declaring a class as an Interface.\n
    **For interface**: checks for missing method implementations, saves method signatures.\n
    **For implementation**: checks for method implementation, method signatures matching.\n
    The implementation of an interface is the first class that inherits the interface.\n

    ```python
    @Interface
    class IPerson:
        def get_name(self) -> str:...
        def get_age(self) -> int:...

    ```

    Alternative interface declaration

    ```python
    class Person:
        def get_name(self) -> str:...
        def get_age(self) -> int:...

    IPerson = Interface[Person]

    ```
    To view the interface description, you can pass it to the `print` function or call the `__description__()` method.\

    Call `print(IPerson)` or `IPerson.__description__(prnt=True)` show you:
    ```python

    IPerson[Interface]
    Methods:

        1. def get_name(self) -> str:...
        2. def get_age(self) -> int:...

    ```
    """
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

