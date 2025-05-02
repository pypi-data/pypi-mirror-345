from os import getenv
from types import NoneType
from typing import Any, Generic, Tuple, TypeVar, get_args, overload

T = TypeVar('T')


class Empty:
    """Representation of an empty value
    """

class EnvVar(Generic[T]):
    """
    Descriptor for getting a value from environment variables.
    You can specify a `default value` and the `type` to which the obtained value will be cast\n
    Example:
    ```python
    class DataBaseConfig:
        host = EnvVar('DB_HOST', default='localhost')
        port = EnvVar('DB_PORT', default=3306, Type=int)
    ```
    When comparing two instances, the arg_name, type and value will be compared.\n
    The following example will return `True`
    ```python
    EnvVar('DB_PORT', default=3306, Type=int) == EnvVar('DB_PORT', default=3306, Type=int)
    ```
    """
    @overload
    def __init__(self, name:str, *, default:Any=Empty, Type:T = Empty) -> None:...
