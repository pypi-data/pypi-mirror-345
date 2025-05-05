from typing import Callable, Generic, ParamSpec, TypeVar, overload

T = TypeVar('T')
P = ParamSpec('P')


class annotatable(Generic[P, T]):

    """
    The decorator will find all `Annotated[Type, GeneratorMethod]` arguments and if no value is passed for them when called or the value does not match the `Type`, it will fill it with the value obtained from `GeneratorMethod`

    ```
    def get_session() -> Session:
        return Session(engine)

    SessionT = Annotated[Session, get_session]

    @annotatable
    def get_user(id:int, sess:SessionT):...

    ```
    Now, if we don't pass a `Session` object to the function, the object will be created by calling the `get_session()` method.
    ```
    user = get_user(id=1)
    ```

    An argument with an `Annotated` type can appear anywhere in the function declaration and can be passed as either a positional or named argument.
    All metadata in `Annotated` except the first element is ignored and can be used for other purposes. The first element must be a default value generator.
    """

    @overload
    def __init__(self, func:Callable[P, T]) -> Callable[P, T]:...
    @overload
    def __call__(self, *args:P.args, **kwargs:P.kwargs) -> T:...