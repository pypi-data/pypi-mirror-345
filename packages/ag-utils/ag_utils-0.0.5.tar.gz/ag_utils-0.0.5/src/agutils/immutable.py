

class ImmutableMeta(type):

    def __init__(self, name:str, bases:tuple, params:dict):
        super().__init__(name, bases, params)


    def __setattr__(self, name, value):
        raise ValueError(f"Cannot modify fields of class {self.__name__}[Immutable]")


class Immutable(metaclass=ImmutableMeta):
    def __init__(self):
        raise TypeError(f"Type {self.__class__.__name__}[Immutable] cannot be instantiated.")
    def __init_subclass__(cls):
        if len(cls.mro()) > 3:
            raise TypeError(f"Cannot subclass {cls.__base__.__name__}[Immutable]")