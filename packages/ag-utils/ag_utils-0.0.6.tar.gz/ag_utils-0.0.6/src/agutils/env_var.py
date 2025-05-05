from os import getenv
from types import NoneType
from typing import Any, Generic, Tuple, TypeVar, get_args

T = TypeVar('T')


class Empty:
    def __init__(self, *args, **kwarg):
        raise TypeError(f"Type `Empty` cannot be instantiated.")

class EnvVar(Generic[T]):

    def __init__(self, name:str, *, default:Any=Empty, Type:T = Empty) -> None:
        value = getenv(name, Empty)
        optional, Type = self.__is_optional(Type)
        if value is Empty:
            value = default
            if optional and value is Empty:
                value = None
        if value is not Empty and Type is not Empty:
            if Type is bool:
                value = str(value).lower() == 'true' or str(value).lower() == '1'
            else:
                TypeCheck = (Type, NoneType,) if optional else (Type,)
                if not isinstance(value, TypeCheck):
                    try: value = Type(value)
                    except Exception as ex:
                        raise ValueError(f'{name} Type cast error: {ex}')
        if Type == Empty:
            if value is not Empty:
                self.Type = type(value)
        else:
            self.Type = Type
        self.value = value

    def __is_optional(self, Type:T) -> Tuple[bool, T]:
        TypeArgs = get_args(Type)
        if isinstance(TypeArgs, tuple):
            if len(TypeArgs) == 2 and NoneType in TypeArgs:
                for elem in TypeArgs:
                    if elem != NoneType:
                        return True, elem
            elif len(TypeArgs) > 0:
                raise ValueError('Only one type can be specified for a variable. Union is not allowed')
        return False, Type

    def __set_name__(self, owner, name) -> None:
        if self.value is Empty:
            raise TypeError(f'Value {owner.__name__}.{name} cannot be `Empty`')
        self.arg_name = name

    def __get__(self, obj, owner) -> T:
        return self.value

    def __repr__(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, value:Any) -> bool:
        if isinstance(value, EnvVar):
            if self.Type == value.Type:
                return all(
                    [
                        self.value == value.value,
                        self.arg_name == self.arg_name
                    ]
                    )
            return False
        return False