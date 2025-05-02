from dataclasses import dataclass
from functools import update_wrapper
from inspect import getfullargspec
from typing import (Annotated, Callable, Dict, Generic, List, ParamSpec, Tuple,
                    TypeVar, get_args, get_origin)

T = TypeVar('T')
P = ParamSpec('P')


class annotatable(Generic[P, T]):

    @dataclass
    class ArgsKwargs:
        args:Tuple
        kwargs:Dict

    @dataclass
    class Kwarg:
        name:str
        pos:int
        t:type
        generator:Callable

    __akwargs:List[Kwarg]

    def __init__(self, func:Callable[P, T]) -> Callable[P, T]:
        if not callable(func):
            raise ValueError("Func must be callable. Are you sure you are using class as a decorator?")
        update_wrapper(self, func)
        self.__func = func
        self.__gen_akwargs()

    def __gen_akwargs(self) -> None:
        self.__akwargs = []
        argspec = getfullargspec(self.__func)
        for i, arg in enumerate(argspec.args):
            annot = argspec.annotations.get(arg, None)
            if not annot: continue
            if get_origin(annot) is Annotated:
                t = annot.__origin__
                meta = annot.__metadata__[0]
                if callable(meta):
                    self.__akwargs.append(
                        self.Kwarg(
                            name=arg, pos=i, t=t, generator=meta
                        )
                    )
        if len(argspec.args) > 0 and (argspec.args[0] == 'self' or argspec.args[0] == 'cls'):
            for akwarg in self.__akwargs:
                akwarg.pos -= 1

    def __process_func_args(self, argkw:ArgsKwargs) -> ArgsKwargs:
        for akwarg in self.__akwargs:
            if akwarg.pos < 0: continue

            kw = argkw.kwargs.get(akwarg.name, None)
            if kw:
                if not isinstance(kw, akwarg.t):
                    argkw.kwargs.update({akwarg.name: akwarg.generator()})
            else:
                if len(argkw.args) >= (akwarg.pos+1):
                    if not isinstance(argkw.args[akwarg.pos], akwarg.t):
                        argkw.args = argkw.args[:akwarg.pos] + (akwarg.generator(),) + argkw.args[akwarg.pos+1:]
                else:
                    argkw.kwargs.update({akwarg.name: akwarg.generator()})
        return argkw

    def __call__(self, *args:P.args, **kwargs:P.kwargs) -> T:
        result = self.__process_func_args(self.ArgsKwargs(args, kwargs))
        return self.__func(*result.args, **result.kwargs)