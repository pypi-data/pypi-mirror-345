from typing import Callable, Generic, ParamSpec, TypeVar

T = TypeVar('T')



class classproperty(Generic[T]):

    """
    Analog of `property` for a class without instantiation. No `setter` or `deleter`

    ```python
        class MyClass:

            @classproperty
            def prop(cls):
                return 'Some value'

        value = MyClass.prop
        ```
    """

    def __init__(self, f:Callable[..., T]) -> None:
        self.__f = f
    def __get__(self, instance, owner) -> T:
        return self.__f(owner)