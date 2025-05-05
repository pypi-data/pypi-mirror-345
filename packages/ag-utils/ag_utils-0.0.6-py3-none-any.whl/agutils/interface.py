
from __future__ import annotations

from dataclasses import dataclass
from inspect import Signature, getsourcelines
from types import NoneType
from typing import Callable, Dict, Generic, ParamSpec, Tuple, TypeVar, Union

from .colored_message import ColoredConsoleMessage as CCM

T = TypeVar('T')
P = ParamSpec('P')

@dataclass
class InterfaceMethod:
    cls:str
    name:str
    meth:Callable
    signature:Signature

    def __post_init__(self):
        sourcelines = getsourcelines(self.meth)[0]
        source = ''.join([line.replace('\n', '').strip().replace(' ', '') for line in sourcelines])

        left = f'def{self.name}{str(self.signature)}'.replace(' ', '')
        right = f'{source}'
        doc = (self.meth.__doc__ or '').replace('\n', '').replace(' ','').strip()
        if doc:
            doc = f'"""{doc}"""'
            right = right.replace(doc, '')
        right = right.replace(left, '')[1:].strip()

        allowed_body = ['pass', '...', '']
        if right not in allowed_body:
            ex = f'Method: {self.cls}.{self.name}: It is forbidden to define a method implementation in an interface.\nUse `pass` or Elipsis(...)'
            raise ValueError(ex)

    @property
    def sigrepr(self) -> str:
        return f'def {self.name}{self.signature}:...'


class Interface(Generic[P, T]):

    __isinterface__:bool
    __mro__:list[type]

    __methods__:Dict[str, list[InterfaceMethod]]
    __implimented__:Dict[str, bool]
    __name__:str

    def __class_getitem__(cls, Type:Union[type, Tuple[type]]):
        if isinstance(Type, tuple):
            ex = '`Interface` can only take one argument'
            raise ValueError(ex)
        return cls(Type)

    def __new__(cls, Type:Callable[P, T], bases:tuple = None, params:dict = None):
        ninstance = super().__new__(cls)
        ninstance.__init_vars__()
        name = Type.__name__ if isinstance(Type, type) else Type


        ninstance.__isinterface__ = isinstance(Type, type)
        ninstance.__validate_parent__(Type)
        ninstance.__validate_type__(Type)
        # ninstance.__validate_name__(name)

        if ninstance.__isinterface__:
            ninstance.__implimented__[name] = False
            ninstance.__methods__[name] = ninstance.__collect_methods(Type)
            ninstance.__mro__.insert(0, Type)


        ninstance.__name__ = name

        if bases:
            ninstance.__isinterface__ = False
            for instance in bases:
                if isinstance(instance, Interface):
                    ninstance.__mro__ += [mro for mro in instance.__mro__ if mro not in ninstance.__mro__]
                    ninstance.__methods__.update(instance.__methods__)

                ninstance.__implimented__.update(instance.__implimented__)

        return ninstance

    def __init_vars__(self) -> None:
        self.__mro__ = getattr(self, '__mro__', [])
        self.__methods__ = getattr(self, '__methods__', dict())
        self.__implimented__ = getattr(self, '__implimented__', dict())
        self.__name__ = getattr(self, '__name__', '')

    def __validate_type__(self, Type:Union[type, str]) -> None:
        if isinstance(Type, Interface):
            if hasattr(Type, '__methods__'):
                interfaces =' ' + ', '.join(f'{k}[Interface]' for k in Type.__methods__)
                ex = f'Cannot declare interface from implementation{interfaces}'
                raise TypeError(ex)

    def __validate_name__(self, name:str) -> None:
        if self.__isinterface__:
            check = [
                name.lower().startswith('i'),
                name.lower().endswith('able')
            ]
            if not any(check):
                vowels = ['a', 'e', 'i', 'o', 'u']
                mess = f'It is recommended to highlight the interface name with a capital `i` at the beginning of the name or with the ending `able`.'
                CCM.yellow('WARNING: ', end='')
                CCM.plain(mess)
                CCM.green('Example: ', end='')
                if name[-1] in vowels:
                    CCM.plain(f'I{name} or {name[:-1]}able')
                else:
                    CCM.plain(f'I{name} or {name}able')

    def __validate_parent__(self, Type:type) -> None:
        if self.__isinterface__:
            if isinstance(Type, type):
                if Type.__base__ != object:
                    ex = f'Interface cannot inherit `{Type.__base__.__name__}`'
                    raise TypeError(ex)

    def __init__(self, cls:Callable[P, T], bases:tuple = None, params:dict = None):
        if not isinstance(cls, type) and bases and params:
            cls = type(cls, tuple(self.__mro__ + [object]), params)
            self.__check_methods(cls)
            self.__mro__.insert(0, cls)
        self.__cls = cls

    def __call__(self, *args:P.args, **kwargs:P.kwargs) -> T:
        if self.__isinterface__:
            ex = f'Cannot create an instance of the interface {self.__cls.__name__}[Interface]'
            raise TypeError(ex)
        return self.__cls(*args, **kwargs)

    def __collect_methods(self, cls:Callable[P, T]) -> list:
        methods = []
        for k, v in cls.__dict__.items():
            if not callable(v): continue

            methods.append(
                InterfaceMethod(
                    cls.__name__,
                    k,
                    v,
                    Signature.from_callable(v)
                )
            )
        if not methods:
            ex = f'Defining an interface {cls.__name__}[Interface] without methods'
            raise ValueError(ex)
        return methods

    def __check_methods(self, cls:Callable[P, T]) -> None:
        for interface in self.__methods__:
            if self.__implimented__[interface]: continue
            for meth in self.__methods__[interface]:
                clsmeth = cls.__dict__.get(meth.name, None)

                try:
                    details = '...'
                    if clsmeth == None:
                        details = f'method `{cls.__name__}.{meth.name}` is not implemented'
                        raise

                    clsmethsig = Signature.from_callable(clsmeth)

                    if len(meth.signature.parameters) != len(clsmethsig.parameters):
                        details = f'`{cls.__name__}.{meth.name}` number of arguments does not match. Expected: {len(meth.signature.parameters)}. Passed: {len(clsmethsig.parameters)}'
                        raise
                    if meth.signature.return_annotation != clsmethsig.return_annotation:
                        details = f'`{cls.__name__}.{meth.name}` return type does not match. Expected: [{(meth.signature.return_annotation or NoneType).__name__}]. Passed: [{(clsmethsig.return_annotation or NoneType).__name__}]'
                        raise

                    for par, clspar in zip(meth.signature.parameters.values(), clsmethsig.parameters.values()):
                        if par.name != clspar.name:
                            details = f'`{cls.__name__}.{meth.name}` variable name does not match. Expected: `{par.name}`. Passed: `{clspar.name}`'
                            raise
                        if par.kind != clspar.kind:
                            details = f'`{cls.__name__}.{meth.name}` variable kind does not match. Expected: {par.name}[{par.kind}]. Passed: {clspar.name}[{clspar.kind}]'
                            raise
                        if par.annotation != clspar.annotation:
                            details = f'`{cls.__name__}.{meth.name}` variable annotation does not match. Expected: {par.name}[{(par.annotation or NoneType).__name__}]. Passed: {clspar.name}[{(clspar.annotation or NoneType).__name__}]'
                            raise

                except:
                    ex = f'Class {cls.__name__} must implement the {meth.name} interface method {meth.cls}[Interface] with signature:\n\n    {meth.sigrepr}\n\nDetails: {details}'
                    raise ValueError(ex)
                self.__implimented__[interface] = True

    def __description__(self,*, showdoc:bool=False, prnt:bool=True) -> str:
        text = ''
        for cls, methods in self.__methods__.items():
            text += f'\n{cls}[Interface]'
            if hasattr(self, '__implimented__'):
                if self.__implimented__.get(cls, False):
                    text += ' (implemented)'
            text += '\n'
            text += f'Methods:\n\n'
            for i, meth in enumerate(methods):
                text += f'  {i+1}. {meth.sigrepr}\n'
                if showdoc:
                    text += f'  Docstring: {(meth.meth.__doc__ or "...")} \n\n'
        if prnt: print(text)
        return text

    def __repr__(self):
        return self.__description__(prnt=False)

