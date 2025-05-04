"""
**Tense Utility Tools** \n
\\@since 0.3.34 \\
© 2025-Present Aveyzan // License: MIT
```ts
module tense.util
```
Includes utility tools, including `Final`, `Abstract` and `Frozen` classes, \\
extracted from `tense.types_collection`. It formally doesn't use the `tense` \\
module.
"""


# standard imports
from __future__ import annotations
import abc as _abc
import collections.abc as _collections_abc
import typing as _typing
import typing_extensions as _typing_ext # not standard, ensure it is installed
import sys as _sys

from ._exceptions import *
from ._exceptions import ErrorHandler as _E
from . import _init_types as _types
from . import _abc as _tense_abc

del ErrorHandler

_P = _types.ParamSpec("_P")
_T = _types.TypeVar("_T")
_T_cov = _types.TypeVar("_T_cov", covariant = True)
_T_func = _types.TypeVar("_T_func", bound = _types.Callable[..., _types.Any])
_RichComparable = _types.Union[_tense_abc.LeastComparable, _tense_abc.GreaterComparable]

_OptionSelection = _types.Literal["frozen", "final", "abstract", "no_reassign"] # 0.3.27rc2

def _reckon(i: _tense_abc.Iterable[_T], /):
    
    _i = 0
    
    for _ in i:
        _i += 1
        
    return _i

class _InternalHelper:
    """
    \\@since 0.3.27rc2
    
    Class responsible to shorten code for several classes such as `Final` and `Abstract`
    """
    
    def __new__(cls, t: type[_T], o: _OptionSelection, /):
        
        _reassignment_operators = {
            "__iadd__": "+=",
            "__isub__": "-=",
            "__imul__": "*=",
            "__itruediv__": "/=",
            "__ifloordiv__": "//=",
            "__imod__": "",
            "__imatmul__": "@=",
            "__iand__": "&=",
            "__ior__": "|=",
            "__ixor__": "^=",
            "__ilshift__": "<<=",
            "__irshift__": ">>=",
            "__ipow__": "**="
        }
        
        _cannot_redo = {"tmp": "tmp2"}
        
        # assuming empty string-string dictionary
        
        if False: # < 0.3.37
            if _cannot_redo["tmp"]:
                del _cannot_redo["tmp"]
                
        else:
            _cannot_redo.clear()
        
        def _no_sa(self: _T, name: str, value): # no setattr
            
            if name in type(self).__dict__:
                _E(118, name)
                
            type(self).__dict__[name] = value
            
        def _no_da(self: _T, name: str): # no delattr
            
            if name in type(self).__dict__:
                _E(117, name)
                
        def _no_inst(self: _T, *args, **kwds): # no initialize
            _ref = type(self)
            _E(104, _ref.__name__)
            
        def _no_cinst(o: object): # no check instance
            _E(115, t.__name__)
            
        def _no_sub(*args, **kwds): # no subclass
            _E(113, t.__name__)
            
        def _no_csub(cls: type): # no check subclass
            _E(116, t.__name__)
            
        def _no_re(op: str): # no reassignment; must return callback so assigned attributes can be methods
            
            def _no_re_internal(self: _types.Self, other: _T):
                
                _op = "with operator {}".format(op)
                _E(102, _op)
                
            return _no_re_internal
        
        def _empty_mro(self: _T): # empty method resolution order; peculiar for final classes
            return None
        
        if o in ("frozen", "no_reassign"):
            
            t.__slots__ = ("__weakref__",)
            t.__setattr__ = _no_sa
            t.__delattr__ = _no_da
            
            _cannot_redo["__setattr__"] = _no_sa.__name__
            _cannot_redo["__delattr__"] = _no_da.__name__
            
            if o == "no_reassign":
                
                for key in _reassignment_operators:
                    
                    exec("t.{} = _no_re(\"{}\")".format(key, _reassignment_operators[key])) # f-strings since python 3.6
                    exec("_cannot_redo[\"{}\"] = _no_re(\"{}\").__name__".format(key, _reassignment_operators[key]))
                    
        elif o == "final":
            
            t.__slots__ = ("__weakref__",)
            t.__init_subclass__ = _no_sub
            t.__subclasscheck__ = _no_csub
            t.__mro_entries__ = _empty_mro
            
            _cannot_redo["__init_subclass__"] = _no_sub.__name__
            _cannot_redo["__subclasscheck__"] = _no_csub.__name__
            _cannot_redo["__mro_entries__"] = _empty_mro.__name__
            
        else:
            t.__init__ = _no_inst
            t.__instancecheck__ = _no_cinst
            
            _cannot_redo["__init__"] = _no_inst.__name__
            _cannot_redo["__instancecheck__"] = _no_cinst.__name__
            
        for key in _cannot_redo:
            if _cannot_redo[key] != "_no_re_internal" and eval("t.{}.__code__".format(key)) != eval("{}.__code__".format(_cannot_redo[key])):
                _E(120, key)    
        
        return t

class _FinalVar(_types.NamedTuple, _types.Generic[_T]): # 0.3.35
    x: _T
    """\\@since 0.3.35. This attribute holds the value"""
    
    def __pos__(self):
        
        return self.x
    
    def __str__(self):
        
        return "FinalVar({})".format(str(self.x) if type(self.x) is not str else self.x)   
    
# if not that, then it will behave like normal NamedTuple
_FinalVar = _InternalHelper(_FinalVar, "no_reassign")

types = _types
"""\\@since 0.3.37"""

@_types.runtime
class Abstract(_types.Protocol):
    """
    \\@since 0.3.26b3 \\
    https://aveyzan.glitch.me/tense/py/module.types_collection.html#Abstract
    
    Creates an abstract class. This type of class forbids class initialization. To prevent this class \\
    being initialized, this class is a protocol class.
    """
    
    def __init_subclass__(cls):
        cls = _InternalHelper(cls, "abstract")
    
    def __instancecheck__(self, instance: object):
        "\\@since 0.3.27b1. Error is thrown, because class may not be instantiated"
        _E(115, type(self).__name__)
    
    def __subclasscheck__(self, cls: type):
        "\\@since 0.3.27b1. Check whether a class is a subclass of this class"
        return issubclass(cls, type(self))
    
    if False: # 0.3.28 (use abstractmethod instead)
        @staticmethod
        def method(f: _T_func):
            """\\@since 0.3.27rc2"""
            from abc import abstractmethod as _a
            return _a(f)

def abstract(t: type[_T]):
    """
    \\@since 0.3.27a5 (formally)
    
    Decorator for abstract classes. To 0.3.27rc2 same `abc.abstractmethod()`
    """
    t = _InternalHelper(t, "abstract")
    return t

def abstractmethod(f: _T_func):
    """\\@since 0.3.27rc2"""
    # to accord python implementation
    if False:
        return Abstract.method(f)
    else:
        return _abc.abstractmethod(f)
    
if hasattr(_abc, "abstractproperty"):
    from abc import abstractproperty as abstractproperty # deprecated since 3.3
    
else:
    class abstractproperty(property):
        """
        \\@since 0.3.26rc1

        A decorator class for abstract properties.

        Equivalent invoking decorators `tense.types_collection.abstract` and in-built `property`.
        """
        __isabstractmethod__ = True

if hasattr(_abc, "abstractstaticmethod"):
    from abc import abstractstaticmethod as abstractstaticmethod # deprecated since 3.3
    
else:
    class abstractstaticmethod(staticmethod):
        """
        \\@since 0.3.26rc1

        A decorator class for abstract static methods.

        Equivalent invoking decorators `tense.types_collection.abstract` and in-built `staticmethod`.
        """
        __isabstractmethod__ = True
        
        def __init__(self, f: _types.Callable[_P, _T_cov]):
            f.__isabstractmethod__ = True
            super().__init__(f)

if hasattr(_abc, "abstractclassmethod"):
    from abc import abstractclassmethod as abstractclassmethod # deprecated since 3.3
    
else:
    class abstractclassmethod(classmethod):
        """
        \\@since 0.3.26rc1

        A decorator class for abstract class methods.

        Equivalent invoking decorators `tense.types_collection.abstract` and in-built `classmethod`.
        """
        __isabstractmethod__ = True
        
        def __init__(self, f: _types.Callable[_types.Concatenate[type[_T], _P], _T_cov]):
            f.__isabstractmethod__ = True
            super().__init__(f)
        

# reference to enum.Enum; during experiments and not in use until it is done
# tests done for 0.3.27rc1
class Frozen:
    """
    \\@since 0.3.27b1 (experiments finished 0.3.27rc1, updated: 0.3.27rc2) \\
    https://aveyzan.glitch.me/tense/py/module.types_collection.html#Frozen
    
    Creates a frozen class. This type of class doesn't allow change of provided fields \\
    once class has been declared and then initialized.
    """
    
    def __init_subclass__(cls):
        cls = type(cls.__name__, tuple([]), {k: _FinalVar(cls.__dict__[k]) for k in cls.__dict__ if k[:1] != "_"})

def frozen(t: type[_T]):
    """
    \\@since 0.3.27rc1

    Alias to `dataclass(frozen = True)` decorator (for 0.3.27rc1). \\
    Since 0.3.27rc2 using different way.
    """
    t = _InternalHelper(t, "frozen")
    return t


class Final:
    """
    \\@since 0.3.26b3 (experimental; to 0.3.27b3 `FinalClass`, experiments ended 0.3.27rc1) \\
    https://aveyzan.glitch.me/tense/py/module.types_collection.html#Final

    Creates a final class. This type of class cannot be further inherited once a class extends this \\
    class. `class FinalClass(Final)` is OK, but `class FinalClass2(FinalClass)` not. \\
    However, class can be still initialized, but it is not recommended. It's purpose is only to create \\
    final classes (to 0.3.29 - error occuring due to class initialization)
    
    This class is a reference to local class `_Final` from `typing` module, with lack of necessity \\
    providing the `_root` keyword to inheritance section.
    """
    __slots__ = ("__weakref__",)

    def __init_subclass__(cls):
        cls = _InternalHelper(cls, "final")
       
    def __instancecheck__(self, instance: object):
        "\\@since 0.3.27rc1. Check whether an object is instance to this class"
        return isinstance(instance, type(self))
    
    def __subclasscheck__(self, cls: type):
        "\\@since 0.3.27rc1. Error is thrown, because this class may not be subclassed"
        _E(116, type(self).__name__)
       
    def __mro_entries__(self):
        return None
    
    @property
    def __mro__(self):
        return None
    
    if False: # 0.3.28 (use finalmethod instead)
        @staticmethod
        def method(f: _T_func):
            """\\@since 0.3.27rc2"""
            if sys.version_info >= (3, 11):
                from typing import final as _f
            else:
                from typing_extensions import final as _f
            return _f(f)
    
def final(t: type[_T]):
    """
    \\@since 0.3.26b3
    """
    t = _InternalHelper(t, "final")
    return t

def finalmethod(f: _T_func):
    """
    \\@since 0.3.27rc2
    """
    if False:
        return Final.method(f)
    else:
        
        if _sys.version_info >= (3, 11):
            return _typing.final(f)
        
        else:
            return _typing_ext.final(f)
        
class finalproperty:
    """
    \\@since 0.3.37
    
    A decorator which creates a final (constant) property. \\
    This property cannot receive new values nor be deleted, what makes \\
    this property read-only.
    
    It does not work with `classmethod` nor `staticmethod`. If either \\
    of these has been used along with this decorator, internal code \\
    neutralizes effects of both decorators, and error will be always \\
    thrown when setting or deleting final property via instance (not via \\
    reference).
    """
    
    def __new__(cls, f: _types.Callable[_P, _T], /):
        
        _f = property(f)
        
        if isinstance(f, staticmethod):
            
            def _no_de():
            
                if _sys.version_info >= (3, 13):
                    _E(122, _f.__name__)
                    
                else:
                    _E(122, _f.fget.__name__)
                    
            def _no_se(x):
                
                if _sys.version_info >= (3, 13):
                    _E(122, _f.__name__)
                    
                else:
                    _E(122, _f.fget.__name__)
                    
        else:
        
            def _no_de(self):
                
                if _sys.version_info >= (3, 13):
                    _E(122, _f.__name__)
                    
                else:
                    _E(122, _f.fget.__name__)
                    
            def _no_se(self, x):
                
                if _sys.version_info >= (3, 13):
                    _E(122, _f.__name__)
                    
                else:
                    _E(122, _f.fget.__name__)
                
        _f = _f.deleter(_no_de)
        _f = _f.setter(_no_se)
        _f = _f.getter(f)
        
        return _f

class FinalVar:
    """
    \\@since 0.3.26rc1 (experiments ended on 0.3.35)
    
    To 0.3.35 this class was in `tense.types_collection`. This class formalizes a final variable. On 0.3.35 all ways to get the value \\
    (expect with unary `+`) has been replaced with `x` attribute access. Hence you use the following: `instance.x`.
    """
    
    def __new__(cls, value: _T, /):
        
        return _FinalVar(value)
    
    def __init_subclass__(cls):
        
        def _tmp(cls: type[_types.Self], value: _T, /):
        
            return _FinalVar(value)
        
        cls.__new__ = _tmp
        
FinalVarType = _FinalVar # 0.3.38; see Tense.isFinalVar()
        
@final
class ClassLike(_types.Generic[_P, _T]):
    """
    \\@since 0.3.27a3
    
    To 0.3.35 this class was in `tense.types_collection`. \\
    A class decorator for functions, transforming them to declarations \\
    similar to classes. Example::
    
        @ClassLike
        def test():
            return 42

        a = test() # returns 42

    """
    def __init__(self, f: _types.Callable[_P, _T]):
        self.f = f
        
    def __call__(self, *args: _P.args, **kwds: _P.kwargs):
        return self.f(*args, **kwds)
    
classlike = ClassLike # since 0.3.27a3
        
AbstractMeta = _abc.ABCMeta
"""
\\@since 0.3.27b1. Use it as::
```
class AbstractClass(metaclass = AbstractMeta): ...
```
"""

class AbstractFinal:
    """
    \\@since 0.3.27rc1
    
    Creates an abstract-final class. Typically blend of `Abstract` and `Final` classes \\
    within submodule `tense.types_collection`. Classes extending this class are \\
    only restricted to modify fields (as in `TenseOptions`) or invoke static methods, \\
    because they cannot be neither initialized nor inherited.
    """
    __slots__ = ("__weakref__",)
    
    def __init_subclass__(cls):
        cls = _InternalHelper(cls, "abstract")
        cls = _InternalHelper(cls, "final")
       
    def __mro_entries__(self):
        return None
    
    @property
    def __mro__(self):
        return None
    
    def __instancecheck__(self, instance: object):
        "\\@since 0.3.27rc1. Error is thrown, because class may not be instantiated"
        _E(115, type(self).__name__)
    
    def __subclasscheck__(self, cls: type):
        "\\@since 0.3.27rc1. Error is thrown, because class may not be subclassed"
        _E(116, type(self).__name__)

class FinalFrozen:
    """
    \\@since 0.3.27rc1
    
    Creates a final-frozen class. Typically blend of `Final` and `Frozen` classes \\
    within submodule `tense.types_collection`. Classes extending this class cannot \\
    be further extended nor have fields modified by their objects.
    """
    __slots__ = ("__weakref__",)
    
    def __init_subclass__(cls):
        cls = _InternalHelper(cls, "final")
        cls = _InternalHelper(cls, "frozen")
       
    def __instancecheck__(self, instance: object):
        "\\@since 0.3.27rc1. Check whether an object is instance to this class"
        return isinstance(instance, type(self))
    
    def __subclasscheck__(self, cls: type):
        "\\@since 0.3.27rc1. Error is thrown, because this class may not be subclassed"
        _E(116, type(self).__name__)
       
    def __mro_entries__(self):
        return None
    
    @property
    def __mro__(self):
        return None  

class AbstractFrozen:
    """
    \\@since 0.3.27rc1
    
    Creates an abstract-frozen class. Typically blend of `Abstract` and `Frozen` classes \\
    within submodule `tense.types_collection`. Classes extending this class cannot \\
    be initialized, nor have their fields modified. During experiments
    
    Possible way to end the experiments would be:
    - extending `enum.Enum` and overriding only some of its declarations, such as `__new__` method
    - extending `type` and raising error in `__setattr__` and `__delattr__`
    - creating private dictionary which will store class names as keys and fields as values, further \\
        used by both pre-mentioned methods
    """
    __slots__ = ()
    
    def __init_subclass__(cls):
        
        def _no_init(self: _types.Self):
            _E(104, cls.__name__)
        
        cls = abstract(frozen(cls))
        
        if cls.__init__.__code__ != _no_init.__code__:
           error = LookupError("cannot remake __init__ method code on class " + cls.__name__)
           raise error
        
    def __instancecheck__(self, instance: object):
        "\\@since 0.3.27rc1. Error is thrown, because class may not be instantiated"
        _E(115, type(self).__name__)
        
    def __subclasscheck__(self, cls: type):
        "\\@since 0.3.27rc1. Check whether a class is a subclass of this class"
        return issubclass(cls, type(self))


class SortedList(_types.Generic[_T]):
    """
    \\@since 0.3.35
    
    Creates a sorted list. Note this class doesn't inherit from `list` builtin itself.
    """
    
    def __init__(self, i: _collections_abc.Iterable[_T], /, key: _types.Optional[_types.Callable[[_T], _RichComparable]] = None, reverse = False): # 0.3.35
        
        if not isinstance(i, _collections_abc.Iterable):
            
            error = ValueError("expected an iterable")
            raise error
        
        self.__l = self.__sorted = [e for e in i]
        self.__sorted.sort(key = key, reverse = reverse)
        
    
    def __iter__(self): # 0.3.35
        
        return iter(self.__sorted)
    
    
    def __len__(self): # 0.3.35
        
        return _reckon(self.__sorted)
    
    
    def __getitem__(self, index: int, /): # 0.3.35
        
        return self.__sorted[index]
    
    
    def __contains__(self, item: _T, /): # 0.3.35
        
        return item in self.__sorted
    
    
    def __eq__(self, other, /): # 0.3.35
        
        return type(other) is type(self) and list(self) == list(other)
    
    
    def __ne__(self, other, /): # 0.3.35
        
        return (type(other) is not type(self)) or self.__eq__(other)
        
        
    def __str__(self): # 0.3.35
        
        return "{}({})".format(type(self).__name__, _reckon(self.__l))
    
    
    def __repr__(self): # 0.3.35
        
        return "<{}.{} object: {}>".format(self.__module__, type(self).__name__, self.__str__())
        
        
    def reverse(self, v = False, /):
        """\\@since 0.3.35"""
        
        if v:
            self.__sorted.reverse()
            
            
    def setKey(self, v: _types.Optional[_types.Callable[[_T], _RichComparable]] = None, /):
        """\\@since 0.3.35"""
        
        self.__sorted = self.__l
        if v is not None:
            self.__sorted.sort(key = v)
            
    
    
__all__ = [k for k in globals() if k[:1] != "_"]