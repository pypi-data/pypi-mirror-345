"""
**AveyTense Utility Tools** \n
\\@since 0.3.34 \\
© 2025-Present Aveyzan // License: MIT

Includes utility tools, including `Final`, `Abstract` and `Frozen` classes, \\
extracted from `aveytense.types_collection`. It formally doesn't use the `aveytense` \\
module.
"""
from __future__ import annotations

import abc as _abc
import dis as _dis
import sys as _sys

from . import _types as __
from ..exceptions import *
from ..exceptions import ErrorHandler as _E

del ErrorHandler

_ch = eval # checker

_P = __.ParamSpec("_P")
_T = __.TypeVar("_T")
_T_cov = __.TypeVar("_T_cov", covariant = True)
_T_func = __.TypeVar("_T_func", bound = __.Callable[..., __.Any])
_T_enum = __.TypeVar("_T_enum", bound = __.Enum)
_RichComparable = __.Union[__.LeastComparable, __.GreaterComparable]

_OptionSelection = __.Literal["frozen", "final", "abstract", "no_reassign"] # 0.3.27rc2

_compiler_flags = {
    "optimized": 1,
    "newlocals": 1 << 1,
    "varargs": 1 << 2,
    "varkeywords": 1 << 3,
    "nested": 1 << 4,
    "generator": 1 << 5,
    "nofree": 1 << 6,
    "coroutine": 1 << 7,
    "iterable_coroutine": 1 << 8,
    "async_generator": 1 << 9
} # 0.3.42

_dis_compiler_flags = {_dis.COMPILER_FLAG_NAMES[k].lower(): k for k in _dis.COMPILER_FLAG_NAMES} # 0.3.42

assert _compiler_flags == _dis_compiler_flags # 0.3.42

def _reckon(i: __.Iterable[_T], /):
    
    _i = 0
    
    for _ in i:
        _i += 1
        
    return _i

def _ih(id: int, /): # internal helper
    
    _m = "eval"
    _c = _i = ""
    
    if id == 10:
        
        _c, _i = "_E(113, t.__name__)", "<final-class inspect>"
        
    elif id == 11:
        
        _c, _i = "_E(116, type(self).__name__)", "<final-class inspect>"
        
    elif id == 12:
        
        _c, _i = "_E(116, t.__name__)", "<final-class inspect>"
        
    elif id == 20:
        
        _c, _i = "_E(104, type(self).__name__)", "<abstract-class inspect>"
    
    elif id == 21:
        
        _c, _i = "_E(115, type(self).__name__)", "<abstract-class inspect>"
        
    elif id == 22:
        
        _c, _i = "_E(115, t.__name__)", "<abstract-class inspect>"
        
    return compile(_c, _i, _m)


def _verify_func(f): # 0.3.42
     
    from functools import partial
    
    func = f.func if isinstance(f, partial) else f if callable(f) else None
    
    if func is not None and func.__code__.co_argcount != 1:
        
        error = TypeError("expected a callable with proper implementation")
        raise error


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
            
            self.__dict__[name] = value
            
        def _no_da(self: _T, name: str): # no delattr
            
            if name in type(self).__dict__:
                _E(117, name)
                
        def _no_inst(self: _T, *args, **kwds): # no initialize
            _ch(_ih(20))
            
        def _no_cinst(o: object): # no check instance
            nonlocal t
            _ch(_ih(22))
            
        def _no_sub(*args, **kwds): # no subclass
            nonlocal t
            _ch(_ih(10))
            
        def _no_csub(cls: type): # no check subclass
            nonlocal t
            _ch(_ih(12))
            
        def _no_re(op: str): # no reassignment; must return callback so assigned attributes can be methods
            
            def _no_re_internal(self: __.Self, other: _T):
                
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

class _FinalVar(__.NamedTuple, __.Generic[_T]): # 0.3.35
    x: _T
    """\\@since 0.3.35. This attribute holds the value"""
    
    def __pos__(self):
        
        return self.x
    
    def __str__(self):
        
        return "FinalVar({})".format(str(self.x) if type(self.x) is not str else self.x)
    
    def __repr__(self): # 0.3.40
        
        return "<{}.{} object: {}>".format(self.__module__, type(self).__name__, self.__str__())
    
# if not that, then it will behave like normal NamedTuple
_FinalVar = _InternalHelper(_FinalVar, "no_reassign")

types = __
"""\\@since 0.3.37"""


class Abstract:
    """
    \\@since 0.3.26b3 \\
    https://aveyzan.glitch.me/tense#aveytense.util.Abstract
    
    Creates an abstract class. This type of class forbids class initialization. To prevent this class \\
    being initialized, this class is a protocol class.
    """
    
    def __init__(self):
        _ch(_ih(20))
        
    def __init_subclass__(cls):
        cls = _InternalHelper(cls, "abstract")
    
    def __instancecheck__(self, instance: object):
        "\\@since 0.3.27b1. Error is thrown, because class may not be instantiated"
        _ch(_ih(21))
    
    def __subclasscheck__(self, cls: type):
        "\\@since 0.3.27b1. Check whether a class is a subclass of this class"
        return issubclass(cls, type(self))
    
    if False: # 0.3.28 (use abstractmethod instead)
        @staticmethod
        def method(f: _T_func):
            """\\@since 0.3.27rc2"""
            from abc import abstractmethod as _a
            return _a(f)

def abstract(t: type[_T], /): # <- 0.3.41 slash
    """
    \\@since 0.3.27a5 (formally)
    
    Decorator for abstract classes. To 0.3.27rc2 same `abc.abstractmethod()`
    """
    t = _InternalHelper(t, "abstract")
    return t

def abstractmethod(f: _T_func, /): # <- 0.3.41 slash
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

        Equivalent invoking decorators `aveytense.types_collection.abstract` and in-built `property`.
        """
        __isabstractmethod__ = True

if hasattr(_abc, "abstractstaticmethod"):
    from abc import abstractstaticmethod as abstractstaticmethod # deprecated since 3.3
    
else:
    class abstractstaticmethod(staticmethod):
        """
        \\@since 0.3.26rc1

        A decorator class for abstract static methods.

        Equivalent invoking decorators `aveytense.types_collection.abstract` and in-built `staticmethod`.
        """
        __isabstractmethod__ = True
        
        def __init__(self, f: __.Callable[_P, _T_cov]):
            f.__isabstractmethod__ = True
            super().__init__(f)

if hasattr(_abc, "abstractclassmethod"):
    from abc import abstractclassmethod as abstractclassmethod # deprecated since 3.3
    
else:
    class abstractclassmethod(classmethod):
        """
        \\@since 0.3.26rc1

        A decorator class for abstract class methods.

        Equivalent invoking decorators `aveytense.types_collection.abstract` and in-built `classmethod`.
        """
        __isabstractmethod__ = True
        
        def __init__(self, f: __.Callable[__.Concatenate[type[_T], _P], _T_cov]):
            f.__isabstractmethod__ = True
            super().__init__(f)

# reference to enum.Enum; during experiments and not in use until it is done
# tests done for 0.3.27rc1
class Frozen:
    """
    \\@since 0.3.27b1 (experiments finished 0.3.27rc1, updated: 0.3.27rc2) \\
    https://aveyzan.glitch.me/tense#aveytense.util.Frozen
    
    Creates a frozen class. This type of class doesn't allow change of provided fields \\
    once class has been declared and then initialized.
    """
    
    def __init_subclass__(cls):
        cls = type(cls.__name__, tuple([]), {k: _FinalVar(cls.__dict__[k]) for k in cls.__dict__ if k[:1] != "_"})

def frozen(t: type[_T], /): # <- 0.3.41 slash
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
    https://aveyzan.glitch.me/tense#aveytense.util.Final

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
        _ch(_ih(11))
       
    def __mro_entries__(self):
        return None
    
    @property
    def __mro__(self):
        return None
    
    if False: # 0.3.28 (use finalmethod instead)
        @staticmethod
        def method(f: _T_func):
            """\\@since 0.3.27rc2"""
            
            if _sys.version_info >= (3, 11):
                from typing import final as _f
                
            else:
                from typing_extensions import final as _f
                
            return _f(f)
    
def final(t: type[_T], /): # <- 0.3.41 slash
    """
    \\@since 0.3.26b3
    """
    t = _InternalHelper(t, "final")
    return t

def finalmethod(f: _T_func, /): # <- 0.3.41 slash
    """
    \\@since 0.3.27rc2
    """
    if False:
        return Final.method(f)
    
    else:
        return __.final(f)
    
class classproperty(__.Generic[_T]):
    """
    @since 0.3.43. *Experimental*
    
    Same as `@classmethod + @property` decorator combination, which was retracted on Python 3.13.
    """
    def __init__(
        self,
        fget: __.Optional[__.Callable[[__.Any], _T]] = None,
        fset: __.Optional[__.Callable[[__.Any, __.Any], None]] = None,
        fdel: __.Optional[__.Callable[[__.Any], None]] = None,
        doc: __.Optional[str] = None,
    ):
        
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or fget.__doc__
    
    def __str__(self):
        
        if self.fget is not None:
            return self.fget.__name__
        
        else:
            return "<anonymous>"
        
    def __repr__(self): # 0.3.44
        
        if self.fget is not None:
            return "<classproperty {}>".format(self.fget.__qualname__)
        
        else:
            return "<anonymous>"
    
    def __get__(self, instance, owner = None):
        
        if self.fget is None:
            error = TypeError("class property '{}' isn't readable".format(self.__str__()))
            raise error
        
        return self.fget(instance)
    
    def __set__(self, instance, value):
        
        if self.fset is None:
            error = TypeError("can't set a value to class property '{}'".format(self.__str__()))
            raise error
        
        self.fset(instance, value)
        
    def __delete__(self, instance):
        
        if self.fdel is None:
            error = TypeError("can't delete class property '{}'".format(self.__str__()))
            raise error
        
        self.fdel(instance)
        
    def getter(self, f: __.Callable[[__.Any], _T], /):
        
        if not callable(f) or f.__code__.co_argcount != 1 or f.__code__.co_kwonlyargcount != 0:
            error = TypeError("expected a callable with one parameter")
            raise error
        
        self.fget = f
        return type(self)(f, self.fset, self.fdel, f.__doc__ or self.__doc__)
        
    def setter(self, f: __.Callable[[__.Any, __.Any], None], /):
        
        if not callable(f) or f.__code__.co_argcount != 2 or f.__code__.co_kwonlyargcount != 0:
            error = TypeError("expected a callable with two parameters")
            raise error
        
        self.fset = f
        return type(self)(self.fget, f, self.fdel, self.__doc__)
    
    def deleter(self, f: __.Callable[[__.Any], None], /):
        
        if not callable(f) or f.__code__.co_argcount != 1 or f.__code__.co_kwonlyargcount != 0:
            error = TypeError("expected a callable with one parameter")
            raise error
        
        self.fdel = f
        return type(self)(self.fget, self.fset, f, self.__doc__)

# it is worth noticing that even if 'finalproperty' class doesn't formally inherit
# from 'property' builtin, it is considered a 'property' builtin anyway. reason it
# does is because of descriptor methods __get__, __set__ and __delete__
# 18.03.2025

class finalproperty(__.Generic[_T]):
    """
    \\@since 0.3.37
    
    A decorator which creates a final (constant) property. \\
    This property cannot receive new values nor be deleted, what makes \\
    this property read-only. This class doesn't inherit from `property`, \\
    however, it returns a new property - just classified as final.
    
    To create static final properties it is advisable to use `~.finalpropertycontainer` (>= 0.3.43) \\
    with parameter `_static_` set to `True`.
    
    Usage of `~.finalproperty` is as simple as `property` inbuilt decorator::
    
        from aveytense.util import finalproperty
        
        class R:
            
            @finalproperty
            def val(self):
                return 42
        
        print(R.val) # <final-property 'R.val'>
        print(R().val) # 42
    """
    
    def __init__(self, f: __.Callable[[__.Any], _T], /):
        
        if isinstance(f, staticmethod):
            f = f.__func__
        
        if not callable(f) or (f.__code__.co_argcount != 1 or f.__code__.co_kwonlyargcount != 0):
            error = TypeError("expected callable with one parameter, or attempt to create final static property with no parameters")
            raise error
        
        self.func = f
        self.__name__ = f.__name__
        self.__doc__ = f.__doc__
        
    def __str__(self):
        
        if _sys.version_info >= (0, 3, 44):
        
            return "<finalproperty '{}'>".format(self.func.__qualname__)
        
        else:
            
            return "<final-property '{}'>".format(self.func.__qualname__)
        
    @__.overload
    def __get__(self, instance: None, owner: __.Optional[type] = None) -> finalproperty[_T]: ...
    
    @__.overload
    def __get__(self, instance: __.Any, owner: __.Optional[type] = None) -> _T: ...
        
    def __get__(self, instance, owner = None):
        
        if instance is None:
            return self
        
        return self.func(instance)
    
    def __set__(self, instance, value):
        
        v = self.func.__name__
        _E(122, v)
        
    def __delete__(self, instance):
        
        v = self.func.__name__
        _E(122, v)

if False: # >= 0.3.43
    
    class finalstaticproperty(__.Generic[_T]):
        
        def __init__(self, f: __.Callable[[], _T], /):
            
            if isinstance(f, staticmethod):
                f = f.__func__
            
            if not callable(f) or (f.__code__.co_argcount != 0 or f.__code__.co_kwonlyargcount != 0):
                error = TypeError("expected callable with no parameters")
                raise error
            
            self.func = f
            self.__name__ = f.__name__
            self.__doc__ = f.__doc__
            
        def __get__(self, instance, owner = None):
            
            if owner is not None and isinstance(owner, type(self)):
                return owner.func.__func__()
            
            return self.func.__func__()
        
        def __set__(self, instance, value):
            
            v = self.func.__name__
            _E(122, v)
            
        def __delete__(self, instance):
            
            v = self.func.__name__
            _E(122, v)

class finalpropertycontainer:
    """
    @since 0.3.43
    
    Creates final properties much easier, using this decorator and keyword arguments as final property names and their values. Unlike \\
    for enumerator classes, this kind of classes need to be instiatiated in order to have effect. It has no effect if none of properties were \\
    defined (like mere invocation `~.finalpropertycontainer()`). It is recommended to use it instead of `~.finalproperty` decorator, \\
    as it may not work as intended. In this case it is better to use `~.FinalVar` class.
    
    Final properties are assigned to type's `__dict__` read-only attribute as mere inbuilt `property` class instances. If a class already \\
    has attributes, and `properties` keyword-only parameter contains some of their names, then these attributes are transformed to \\
    `property` class instances and are defined as final. Attributes receive values as defined in `properties` keyword-only parameter. \\
    It does not apply to properties nor any kind of methods.
    
    `_static_` in `properties` makes attributes look like in enumerator classes: accessible via reference (worth noticing class itself \\
    becomes an object of itself), so using it with `type()` will lose its meaning. All instance methods and properties are accessible \\
    via this 'class reference' (while it is its instance). In this case class cannot be marked abstract.
    
    Usage is simple::
    
        from aveytense.util import finalpropertycontainer
        
        @finalpropertycontainer(x = 65, y = True)
        class R:
            x = 16
        
        print(R().x, R().y) # 65 True
    """
    
    def __new__(cls, **properties): # 0.3.43
        
        def _internal(t: type[_T], /):
            
            def _no_re(v):
                
                def _no_re_internal(i):
                    
                    nonlocal v
                    
                    if i == 2:
                        return lambda self, val: _E(122, v)
                
                    else:
                        return lambda self: _E(122, v)
                    
                return _no_re_internal
            
            _members, _properties = ({k for k in t.__dict__}, {k for k in properties if k != "_static_"})
            _new_dict = {"": StopIteration.value}
            del _new_dict[""]
            
            for member in _members:
                for property_ in _properties:
                    
                    _2 = _no_re(property_)(2)
                    _3 = _no_re(property_)(3)
                    
                    if member != property_:
                        
                        _1 = lambda self: properties[property_]
                        _new_dict[property_] = property(_1, _2, _3)
                        
                    else:
                        
                        # must be an attribute
                        if not isinstance(t.__dict__[member], (__.MethodType, property)):
                            
                            _1 = lambda self: t.__dict__[member]
                            _new_dict[property_] = property(_1, _2, _3)
                            
                    # if not this statement, values of each attributes would be randomized  
                    break 
            
            # normally 'dict' doesn't allow concatenating with +, so we need to create temporary 2 lists with 2-item tuples to convert them
            # to 'dict'
            _new_dict = dict(sorted([(k, t.__dict__[k]) for k in t.__dict__] + [(k, _new_dict[k]) for k in _new_dict], key = lambda x: x[0]))
            
            if "_static_" in properties and properties["_static_"] is True:
                
                # __new__ is revoked too, since it doesnt necessarily have to return class instance
                if "__new__" in _new_dict:
                    error = TypeError("static final properties do not require definition of __new__ method in the target class")
                    raise error
                
                _inspect_init = __.cast(__.Optional[__.AnyCallable], _new_dict.get("__init__"))
                
                if _inspect_init is not None and (_inspect_init.__code__.co_argcount != 1 or _inspect_init.__code__.co_kwonlyargcount != 0):
                    error = TypeError("when __init__ method is defined, expected argumentless (excluding first parameter) implementation of the method")
                    raise error
                
                try:
                    _new_type = __.cast(type[_T], type(t.__name__, t.__bases__, _new_dict)())
                    
                except:
                    
                    try:
                        _new_type = __.cast(type[_T], __.new_class(t.__name__, t.__bases__, _new_dict)())
                        
                    except:
                        
                        error = TypeError("cannot define static final attributes while the class is abstract")
                        raise error
            
            else:
                # one of these must be invoked
                try:
                    _new_type = __.cast(type[_T], type(t.__name__, t.__bases__, _new_dict))
                    
                except:
                    _new_type = __.cast(type[_T], __.new_class(t.__name__, t.__bases__, _new_dict))
                
            t = _new_type
            return t
        
        return _internal

class FinalVar:
    """
    \\@since 0.3.26rc1 (experiments ended on 0.3.35)
    
    To 0.3.35 this class was in `aveytense.types_collection`. This class formalizes a final variable. On 0.3.35 all ways to get the value \\
    (expect with unary `+`) has been replaced with `x` attribute access. Hence you use the following: `instance.x`.
    """
    
    def __new__(cls, value: _T, /):
        
        return _FinalVar(value)
    
    def __init_subclass__(cls):
        
        def _tmp(cls: type[__.Self], value: _T, /):
        
            return _FinalVar(value)
        
        cls.__new__ = _tmp
        
FinalVarType = _FinalVar # 0.3.38; see ~.Tense.isFinalVar()
        
@final
class ClassLike(__.Generic[_P, _T]):
    """
    \\@since 0.3.27a3
    
    To 0.3.35 this class was in `aveytense.types_collection`. \\
    A class decorator for functions, transforming them to declarations \\
    similar to classes. Example::
    
        @ClassLike
        def test():
            return 42

        a = test() # returns 42

    """
    def __init__(self, f: __.Callable[_P, _T]):
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
    \\@since 0.3.27rc1 https://aveyzan.glitch.me/tense#aveytense.util.AbstractFinal
    
    Creates an abstract-final class. Typically blend of `Abstract` and `Final` classes \\
    within submodule `aveytense.util`. Classes extending this class are \\
    only restricted to modify fields (as in `TenseOptions`) or invoke static methods, \\
    because they cannot be neither initialized nor inherited.
    """
    __slots__ = ("__weakref__",)
    
    def __init__(self):
        _ch(_ih(20))
    
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
        _ch(_ih(21))
    
    def __subclasscheck__(self, cls: type):
        "\\@since 0.3.27rc1. Error is thrown, because class may not be subclassed"
        _ch(_ih(11))

class FinalFrozen:
    """
    \\@since 0.3.27rc1
    
    Creates a final-frozen class. Typically blend of `Final` and `Frozen` classes \\
    within submodule `aveytense.util`. Classes extending this class cannot \\
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
        _ch(_ih(11))
       
    def __mro_entries__(self):
        return None
    
    @property
    def __mro__(self):
        return None  

class AbstractFrozen:
    """
    \\@since 0.3.27rc1
    
    Creates an abstract-frozen class. Typically blend of `Abstract` and `Frozen` classes \\
    within submodule `aveytense.util`. Classes extending this class cannot \\
    be initialized, nor have their fields modified. During experiments
    
    Possible way to end the experiments would be:
    - extending `enum.Enum` and overriding only some of its declarations, such as `__new__` method
    - extending `type` and raising error in `__setattr__` and `__delattr__`
    - creating private dictionary which will store class names as keys and fields as values, further \\
        used by both pre-mentioned methods
    """
    __slots__ = ()
    
    def __init_subclass__(cls):
        
        def _no_init(self: __.Self):
            _ch(_ih(2))
        
        cls = abstract(frozen(cls))
        
        if cls.__init__.__code__ is not _no_init.__code__:
           error = LookupError("cannot remake __init__ method code on class " + cls.__name__)
           raise error
        
    def __instancecheck__(self, instance: object):
        "\\@since 0.3.27rc1. Error is thrown, because class may not be instantiated"
        _E(115, type(self).__name__)
        
    def __subclasscheck__(self, cls: type):
        "\\@since 0.3.27rc1. Check whether a class is a subclass of this class"
        return issubclass(cls, type(self))


class SortedList(__.Generic[_T]):
    """
    \\@since 0.3.35
    
    Creates a sorted list. Note this class doesn't inherit from `list` builtin itself.
    """
    
    def __init__(self, i: __.Iterable[_T], /, key: __.Optional[__.Callable[[_T], _RichComparable]] = None, reverse = False): # 0.3.35
        
        if not isinstance(i, __.Iterable):
            
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
            
            
    def setKey(self, v: __.Optional[__.Callable[[_T], _RichComparable]] = None, /):
        """\\@since 0.3.35"""
        
        self.__sorted = self.__l
        if v is not None:
            self.__sorted.sort(key = v)

if False:
    class All:
        """
        @since 0.3.41 (in-code)
        
        A special class featuring `__all__` variable for all its subclasses. Experimental
        """
        
        def __new__(cls, handler: __.Callable[[], __.Union[dict[str, __.Any], __.MappingProxyType[str, __.Any]]] = locals, mode = "public"):
            
            from re import match as _match
            from inspect import getfullargspec
            
            if not callable(handler) or _reckon(getfullargspec(handler).args) != 0:
                error = TypeError("expected a callable without arguments")
                raise error
            
            __all__ = sorted([k for k in handler() if not k.startswith("_")])
            
            if mode == "normal": # everything provided
                __all__ = sorted([k for k in handler()])
                    
            elif mode == "non-private": # no double underscore preceding
                __all__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is not None])
                
            elif mode == "non-protected": # no single underscore preceding
                __all__ = sorted([k for k in handler() if _match(r"^_[^_]+$", k) is not None])
            
            elif mode == "non-public": # no matter how many underscores preceding
                __all__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is not None])
                
            elif mode == "non-sunder": # no single underscores around
                __all__ = sorted([k for k in handler() if _match(r"^_[^_]+_$", k) is None])
                
            elif mode == "non-dunder": # no double underscores around
                __all__ = sorted([k for k in handler() if _match(r"^__[^_]+__$", k) is None])    
                
            elif mode == "non-underscored": # chars other than underscore
                __all__ = sorted([k for k in handler() if _match(r"^_+$", k) is None])
                
            elif mode == "private": # two or more underscores preceding
                __all__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is not None])
                
            elif mode == "protected": # single underscore preceding
                __all__ = sorted([k for k in handler() if _match(r"^_[^_]+$", k) is not None])
                
            elif mode == "public": # no underscores preceding
                __all__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is None])
                
            elif mode == "sunder": # one underscore around
                __all__ = sorted([k for k in handler() if _match(r"^_[^_]+_$", k) is not None])
                
            elif mode == "dunder": # two underscores around
                __all__ = sorted([k for k in handler() if _match(r"^__[^__]+__$", k) is not None])
                
            elif mode == "underscored": # no other chars than underscore
                __all__ = sorted([k for k in handler() if _match(r"^_+$", k) is not None])
                
            else:
                error = TypeError("expected a valid mode")
                raise error
            
            return __all__
        
        @classmethod
        def deprecated(self, handler: __.Callable[[], __.Union[dict[str, __.Any], __.MappingProxyType[str, __.Any]]] = locals, mode = "public"):
            """
            @since 0.3.41
            
            All deprecated declarations. Use as::
            
                __all_deprecated__ = All.deprecated()
            """
            
            from re import match as _match
            from inspect import getfullargspec
            
            if not callable(handler) or _reckon(getfullargspec(handler).args) != 0:
                error = TypeError("expected a callable without arguments")
                raise error
            
            __all_deprecated__ = sorted([k for k in handler() if not k.startswith("_") and hasattr(handler()[k], "__deprecated__")])
            
            if mode == "normal": # everything provided
                __all_deprecated__ = sorted([k for k in handler()])
                    
            elif mode == "non-private": # no double underscore preceding
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "non-protected": # no single underscore preceding
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_[^_]+$", k) is not None and hasattr(handler()[k], "__deprecated__")])
            
            elif mode == "non-public": # no matter how many underscores preceding
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "non-sunder": # no single underscores around
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_[^_]+_$", k) is None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "non-dunder": # no double underscores around
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^__[^_]+__$", k) is None and hasattr(handler()[k], "__deprecated__")])    
                
            elif mode == "non-underscored": # chars other than underscore
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_+$", k) is None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "private": # two or more underscores preceding
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "protected": # single underscore preceding
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_[^_]+$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "public": # no underscores preceding
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "sunder": # one underscore around
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_[^_]+_$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "dunder": # two underscores around
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^__[^__]+__$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "underscored": # no other chars than underscore
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_+$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            else:
                error = TypeError("expected a valid mode")
                raise error
            
            return __all_deprecated__
                
    # override builtins.all()
    def all(mode = "public", deprecated = False):
        """
        @since 0.3.41 (in-code)
        
        As a decorator, defines `__all__` variable in specific class. Possible modes (case sensitive):
        - `"normal"` - gets all members, no matter the status.
        - `"private"` - gets all private members that aren't dunder.
        - `"protected"` - gets all protected members that aren't private, sunder and dunder.
        - `"public"` (default value) - gets all public members. This also includes sunder and dunder members.
        - `"sunder"` - gets all sunder (single-underscored) members.
        - `"dunder"` - gets all dunder (doubly-underscored) members.
        - `"non-private"` - gets all non-private members. This list features public, protected, sunder and dunder members.
        - `"non-protected"` - gets all non-protected members. This list features public, private, sunder and dunder members.
        - `"non-public"` - gets all non-public members. This list features private and protected members only.
        - `"non-sunder"` - gets all non-sunder members. This list features public, protected, private and dunder members.
        - `"non-dunder"` - gets all non-dunder members. This list features public, protected, private and sunder members.
        
        There are also some discouraging modes:
        - `"underscored"` - gets all members whose names are created with underscores only (like `__`).
        - `"non-underscored"` - gets all members whose names aren't created with underscores only. This list features \\
            all public, protected, private, sunder and dunder methods, what means its very similar to `"normal"`.
            
        Use as::
        
            @~.util.all("<mode>") # valid value from above except <mode> or leave it empty,
            # as ~.util.all()
            class Test: ... # members
        
        In this example, `Test.__all__` will normally obtain all public members.
        """
        
        def _all(t: type[_T], /):
            
            from re import match as _match
            
            if not isinstance(t, type):
                error = TypeError("expected a class or type alias")
                raise error
            
            v = t.__dict__
            t = __.cast(type[_T], t)
            t.__all__ = sorted([k for k in v if not k.startswith("_")])
            
            if mode == "normal": # everything provided
                t.__all__ = sorted([k for k in v])
                    
            elif mode == "non-private": # no double underscore preceding
                t.__all__ = sorted([k for k in v if _match(r"^_(_)+[^_]+$", k) is not None])
                
            elif mode == "non-protected": # no single underscore preceding
                t.__all__ = sorted([k for k in v if _match(r"^_[^_]+$", k) is not None])
            
            elif mode == "non-public": # no matter how many underscores preceding
                t.__all__ = sorted([k for k in v if _match(r"^_(_)+[^_]+$", k) is not None])
                
            elif mode == "non-sunder": # no single underscores around
                t.__all__ = sorted([k for k in v if _match(r"^_[^_]+_$", k) is None])
                
            elif mode == "non-dunder": # no double underscores around
                t.__all__ = sorted([k for k in v if _match(r"^__[^_]+__$", k) is None])    
                
            elif mode == "non-underscored": # chars other than underscore
                t.__all__ = sorted([k for k in v if _match(r"^_+$", k) is None])
                
            elif mode == "private": # two or more underscores preceding
                t.__all__ = sorted([k for k in v if _match(r"^_(_)+[^_]+$", k) is not None])
                
            elif mode == "protected": # single underscore preceding
                t.__all__ = sorted([k for k in v if _match(r"^_[^_]+$", k) is not None])
                
            elif mode == "public": # no underscores preceding
                t.__all__ = sorted([k for k in v if _match(r"^_(_)+[^_]+$", k) is None])
                
            elif mode == "sunder": # one underscore around
                t.__all__ = sorted([k for k in v if _match(r"^_[^_]+_$", k) is not None])
                
            elif mode == "dunder": # two underscores around
                t.__all__ = sorted([k for k in v if _match(r"^__[^__]+__$", k) is not None])
                
            elif mode == "underscored": # no other chars than underscore
                t.__all__ = sorted([k for k in v if _match(r"^_+$", k) is not None])
                
            else:
                error = TypeError("expected a valid mode")
                raise error
            
            if deprecated:
                t.__all_deprecated__ = sorted([n for n in vars(t) if hasattr(vars(t)[n], "__deprecated__")])
                
            t.__all__ = [e for e in t.__all__ if e != "__all__"]
            return t
                
        return _all
    
class ParamVar:
    """
    @since 0.3.42 (was in code since 0.3.33)
    
    A special class similar to `inspect.getfullargspec()`.
    If `f` is overloaded function, used is `i` index to denote specific signature
    """
    
    def __init__(self, f: __.Callable[..., __.Any], i = 0, /): # 0.3.42
        
        from functools import partial
        
        if not callable(f) and not isinstance(f, partial):
            error = TypeError("expected a callable with a proper implementation")
            raise error
        
        if type(i) is not int or (_reckon(__.get_overloads(f)) > 0 and i not in range(_reckon(__.get_overloads(f)))):
            error = TypeError("expected an integer in second parameter. keep this parameter as-is, when function isn't overloaded. otherwise, ensure the parameter value is in range <0; overloads_length>")
            raise error
        
        try:
            c = f.__code__
            
        except AttributeError:
            error = TypeError("expected a callable with a proper implementation")
            raise error
        
        def _restrict_setattr(name, value):
            
            if name == "func":
            
                if not callable(value) and not isinstance(value, partial):
                    error = TypeError("expected a callable with a proper implementation")
                    raise error
                
                self.func = value.func if isinstance(value, partial) else value
            
            else:
                error = TypeError("none of this class's attributes are writable; consider passing callable to 'func' instead")
                raise error
        
        self.__vartype = ""
        
        if isinstance(f, partial):
            self.__func = f.func
            
        elif _reckon(__.get_overloads(f)) > 0:
            self.__func = __.cast(__.Callable[..., __.Any], __.get_overloads(f)[i])
            
        else:
            self.__func = f
        
        func = f.func if isinstance(f, partial) else f
        c = self.__func.__code__
        
        def _inspect_func():
            
            import typing
            
            nonlocal self, c
            
            # We are looking for __self__ attribute, what would explain that a function is bound to specific class.
            # However, first parameter in a method doesn't have to be 'self' or 'cls', which are common in all types of methods,
            # so we cannot assume first parameter is one of them, with first item inspection in tuple returned from attribute
            # CodeType.co_varnames. Static methods do not have first parameter referring to the class, instance/class methods do.
            # 27.03.2025
            
            return (
                isinstance(self.__func, __.MethodType) and not isinstance(self.__func, staticmethod)) or (
                    _reckon(__.get_overloads(func)) > 0 or
                    func.__module__ in typing._overload_registry or
                    func.__qualname__ in typing._overload_registry[f.__module__] and # 0.3.43
                isinstance(self.__func, __.MethodType) and not isinstance(self.__func, staticmethod)
            )
        
        if _inspect_func():
            self.__no_first = 1
        
        else:
            self.__no_first = 0
            
        self.__setattr__ = _restrict_setattr
        
    def __str__(self): # 0.3.42
        
        return "{}(positional: {}, positionalDefaults: {}, universal: {}, universalDefaults: {}, keyword: {}, keywordDefaults: {}, annotated: {}, annotatedDefaults: {}, variable: {}, all: {}, allDefaults: {})".format(
            type(self).__name__,
            self.positionalCount,
            self.positionalDefaultsCount,
            self.universalCount,
            self.universalDefaultsCount,
            self.keywordCount,
            self.keywordDefaultsCount,
            self.annotatedCount, # >= 0.3.44
            self.annotatedDefaultsCount, # >= 0.3.44
            str(self.variableCount) + self.__vartype,
            self.allCount,
            self.allDefaultsCount
        )
        
    def __repr__(self): # 0.3.42
        
        return "<{}.{} object :: {} :: Inspected function -> {}>".format(self.__module__, type(self).__name__, self.__str__(), self.func.__qualname__)
    
    @property
    def func(self): # 0.3.42
        
        return self.__func
    
    @func.setter
    def func(self, v): # 0.3.42
        type(self).__init__(self, v)
        
    @func.deleter
    def func(self): # 0.3.43
        
        error = TypeError("unable to delete property {}".format(self.func.__name__))
        raise error
    
    @finalproperty
    def signature(self): # 0.3.42
        """
        Returns function's signature.
        """
        
        if _sys.version_info >= (0, 3, 44):
            
            _sig = "("
            
            # inner tuples have 2 items, so it is possible to convert entire tuple into a dict
            _variable = dict(self.variable)
            
            # inverting keys and values pairs, because <args> and <kwargs> are normally values (not keys) in dictionary (in tuples: second item)
            _inverted = {_variable[k]: k for k in _variable}
            
            # on terminals quotes are omitted, so we will be including them to indicate these values are strings
            _quote = lambda x: x if type(x) is not str else "\"{}\"".format(x)
            
            # pep 570, Py>=3.8
            if self.positionalCount > 0:
                
                _positional_defaults = dict(self.positionalDefaults)
                _no_positional_defaults = [e for e in self.positional if e not in _positional_defaults]
                
                _sig += ", ".join(_no_positional_defaults + ["{} = {}".format(e, _quote(_positional_defaults[e])) for e in _positional_defaults]) + ", /, "
                
            if self.universalCount > 0:
                
                _universal_defaults = dict(self.universalDefaults)
                _no_universal_defaults = [e for e in self.universal if e not in _universal_defaults]
                
                _sig += ", ".join(_no_universal_defaults + ["{} = {}".format(e, _quote(_universal_defaults[e])) for e in _universal_defaults]) + ", "
                
            # if this is True, that means we don't have any universal arguments
            if "<args>" in _inverted:
                _sig += "*{}, ".format(_inverted["<args>"])
            
            # pep 3102, Py>=3.0
            if self.keywordCount > 0:
                
                _keyword_defaults = dict(self.keywordDefaults)
                _no_keyword_defaults = [e for e in self.keyword if e not in _keyword_defaults]
                
                if "<args>" not in _inverted:
                    _sig += "*, "
                    
                _sig += ", ".join(_no_keyword_defaults + ["{} = {}".format(e, _quote(_keyword_defaults[e])) for e in _keyword_defaults])
                
            if "<kwargs>" in _inverted:
                _sig += "**{}, ".format(_inverted["<kwargs>"])
            
            
            if _sig.endswith(", "):
                _sig = _sig[: _reckon(_sig) - 2]
                # same as:
                # import re
                # _sig = re.sub(r", $", "", _sig)
                
            _sig += ")"
            
        else:
        
            import inspect, re
            
            _sig = str(inspect.signature(self.func))
            _sig = re.sub(r"=", " = ", _sig)
            
        return _sig
        
    @finalproperty
    def all(self): # 0.3.42
        """
        Returns all arguments. Last items may be variable argument and keyword argument. \\
        It only depends on the passed function to the constructor.
        """
        
        c = self.func.__code__
        n = c.co_argcount + c.co_kwonlyargcount
            
        if _sys.version_info >= (0, 3, 44):
            
            _all = c.co_varnames[self.__no_first : n]
            _if_varargs = c.co_flags & _compiler_flags["varargs"]
            _if_varkeywords = c.co_flags & _compiler_flags["varkeywords"]

            ### NOTE ###
            # If there is vararg (*<param-name>), then all left-side parameters are positional-only, and all right-side parameters are keyword-only.
            # This means there are NO universal arguments. Varkeyword (**<param-name>) can only occur at the end of parameter definition section.
            # Universal arguments take place only if there is no vararg (varkeyword is optional).
            if self.universalCount == 0:
                
                if _if_varargs and _if_varkeywords:
                    # n (vararg), n + 1 (varkeyword)
                    _all = [e for e in _all if e in self.positional] + [c.co_varnames[n]] + [e for e in _all if e in self.keyword] + [c.co_varnames[n + 1]]
                    
                elif _if_varargs or _if_varkeywords:
                    # there n points either vararg or varkeyword
                    _all = [e for e in _all if e in self.positional] + [c.co_varnames[n]] + [e for e in _all if e in self.keyword]
            
            else:
                
                if _if_varkeywords:
                    _all = [e for e in _all if e in self.positional] + [e for e in _all if e in self.universal] + [c.co_varnames[n]]
                    
                    
            return tuple(_all)        
            
        else:
            
            if c.co_flags & _compiler_flags["varargs"]:
                n += 1
        
            if c.co_flags & _compiler_flags["varkeywords"]:
                n += 1
            
            return c.co_varnames[self.__no_first : n]
    
    @finalproperty
    def allDefaults(self): # 0.3.42
        """
        Returns tuple holding 2-item tuples with content:
        - 0 - names of all arguments
        - 1 - their default values
        
        Convertible to `dict`
        """
        
        return self.positionalDefaults + self.universalDefaults + self.keywordDefaults
    
    @finalproperty
    def allNoDefaults(self): # 0.3.44
        """
        Returns tuple holding all kind of parameters whose don't have a default value.
        """
        
        return tuple([e for e in self.all if e not in self.allDefaults])
    
    @finalproperty
    def positional(self): # 0.3.42
        """
        Returns tuple holding all positional arguments.
        
        See PEP 570 for details.
        """
        
        return self.func.__code__.co_varnames[self.__no_first : self.func.__code__.co_posonlyargcount]
    
    @finalproperty
    def positionalDefaults(self): # 0.3.42
        """
        Returns tuple holding 2-item tuples with content:
        - 0 - names of positional arguments
        - 1 - their default values
        
        Convertible to `dict`
        """
        
        c = self.func.__code__
        
        if self.func.__defaults__ is not None:
            _defaults = self.func.__defaults__[: c.co_posonlyargcount - self.__no_first]
            
        else:
            
            a = [("", StopIteration.value)]
            a.clear()
            return tuple(a)

        if _reckon(_defaults) == _reckon(self.positional):
            
            if _reckon(c.co_varnames[: c.co_argcount - self.__no_first]) == _reckon(self.func.__defaults__):
                
                try:
                    return tuple([(self.positional[i], _defaults[i]) for i in range(_reckon(self.positional))])
                
                except IndexError:
                    pass
        
        # We are reversing the tuples, because items from right side can have a default value.
        # Left-side items do not need to be necessarily optional. It is an error for vice versa.
        # 31.03.2025
        
        r1 = c.co_varnames[self.__no_first : c.co_argcount][::-1]
        r2 = self.func.__defaults__[::-1]
        
        return tuple([(r1[i], r2[i]) for i in range(min(_reckon(r1), _reckon(r2))) if r1[i] in self.positional])[::-1]
    
    
    @finalproperty
    def positionalNoDefaults(self): # 0.3.44
        """
        Returns tuple holding all positional arguments whose don't have a default value.
        """
        
        return tuple([e for e in self.positional if e not in self.positionalDefaults])
    
    
    @finalproperty
    def keyword(self): # 0.3.42
        """
        Returns tuple holding all keyword arguments.
        
        See PEP 3102 for details.
        """
        
        return self.func.__code__.co_varnames[self.func.__code__.co_argcount : self.func.__code__.co_argcount + self.func.__code__.co_kwonlyargcount]
    
    @finalproperty
    def keywordDefaults(self): # 0.3.42
        """
        Returns tuple holding 2-item tuples with content:
        - 0 - names of keyword arguments
        - 1 - their default values
        
        Convertible to `dict`
        """
        
        if self.func.__kwdefaults__ is None:
            
            a = [("", StopIteration.value)]
            a.clear()
            return tuple(a)
        
        return tuple([(k, self.func.__kwdefaults__[k]) for k in self.func.__kwdefaults__])
    
    @finalproperty
    def keywordNoDefaults(self): # 0.3.44
        """
        Returns tuple holding all keyword arguments whose don't have a default value.
        """
        
        return tuple([e for e in self.keyword if e not in self.keywordDefaults])
    
    @finalproperty
    def universal(self): # 0.3.42
        """
        Returns tuple holding all universal arguments.
        
        *Universal* arguments are arguments that can have their values assigned \\
        either by position or keyword.
        """
        
        # Prevent negative integer slice arguments
        if self.func.__code__.co_posonlyargcount - self.__no_first <= 0:
        
            _left = self.__no_first
        
        else:
            
            _left = self.func.__code__.co_posonlyargcount - self.__no_first
        
        return self.func.__code__.co_varnames[_left + 1 : self.func.__code__.co_argcount]
    
    @finalproperty
    def universalDefaults(self): # 0.3.42
        """
        Returns tuple holding 2-item tuples with content:
        - 0 - names of universal arguments
        - 1 - their default values
        
        Convertible to `dict`
        """
        
        c = self.func.__code__
        
        if self.func.__defaults__ is not None and _reckon(self.func.__defaults__) > 0:
            _defaults = self.func.__defaults__[c.co_posonlyargcount - self.__no_first : c.co_argcount]
            
        else:
            
            a = [("", StopIteration.value)]
            a.clear()
            return tuple(a)
        
        if _reckon(_defaults) == _reckon(self.universal):
            
            if _reckon(c.co_varnames[self.__no_first : c.co_argcount]) == _reckon(self.func.__defaults__):
                
                try:
                    return tuple([(self.universal[i], _defaults[i]) for i in range(_reckon(self.universal))])
                
                except IndexError:
                    pass
        
        # We are reversing the tuples, because items from right side can have a default value.
        # Left-side items do not need to be necessarily optional. It is an error for vice versa.
        # 31.03.2025
        
        r1 = c.co_varnames[c.co_posonlyargcount : c.co_argcount][::-1]
        r2 = self.func.__defaults__[::-1]
            
        return tuple([(r1[i], r2[i]) for i in range(min(_reckon(r1), _reckon(r2)))])[::-1]
    
    @finalproperty
    def universalNoDefaults(self): # 0.3.44
        """
        Returns tuple holding all universal arguments whose don't have a default value.
        """
        
        return tuple([e for e in self.universal if e not in self.universalDefaults])
    
    @finalproperty
    def annotated(self): # 0.3.42
        """
        Returns tuple holding names of arguments whose have been annotated a type.
        
        See PEP 484 for details.
        """
        
        return tuple([k for k in self.func.__annotations__])
    
    @finalproperty
    def annotatedDefaults(self): # 0.3.44
        """
        Returns tuple holding 2-item tuples with content:
        - 0 - names of arguments whose have been annotated a type
        - 1 - their default values
        
        Convertible to `dict`
        """
        
        return tuple([e for e in self.allDefaults if e[0] in self.annotated])
    
    @finalproperty
    def annotatedNoDefaults(self): # 0.3.44
        """
        Returns tuple holding names of arguments whose have been annotated a type, \\
        but do not have a default value.
        """
        
        _defaults = dict(self.annotatedDefaults)
        return tuple([e for e in self.annotated if e not in _defaults])
    
    @finalproperty
    def annotations(self): # 0.3.42
        """
        Same as invocation `self.func.__annotations__`.
        """
        
        return tuple([(k, self.func.__annotations__[k]) for k in self.func.__annotations__])
        
    @finalproperty
    def variable(self): # 0.3.42
        """
        Returns tuple holding 2-item tuples with content:
        - if there are both varargs and varkeywords, then
            - 1st tuple = `("vararg_name", "<args>")`
            - 2nd tuple = `("varkeyword_name", "<kwargs>")`
        - if there are either varargs or varkeywords, then \\
            there is one tuple with content either \\
            `("vararg_name", "<args>")` or `("varkeyword_name", "<kwargs>")`
        - if none of these are defined, returned is empty tuple
        """
        
        c = self.func.__code__
        
        if c.co_flags & _compiler_flags["varargs"] and c.co_flags & _compiler_flags["varkeywords"]:
            
            self.__vartype = " <args, kwargs>"
            return tuple([(c.co_varnames[self.allCount], "<args>"), (c.co_varnames[self.allCount + 1], "<kwargs>")])
        
        elif c.co_flags & _compiler_flags["varargs"] or c.co_flags & _compiler_flags["varkeywords"]:
            
            if c.co_flags & _compiler_flags["varargs"]:
                
                self.__vartype = " <args>"
                
            else:
                self.__vartype = " <kwargs>"
            
            return tuple([(c.co_varnames[self.allCount], self.__vartype.lstrip())])
            
        else:
            
            a = [("", "")]
            a.clear()
            return tuple(a)
        
    @finalproperty
    def positionalCount(self): # 0.3.44
        """Returns count of all positional parameters."""
        
        return _reckon(self.positional)
    
    @finalproperty
    def positionalDefaultsCount(self): # 0.3.44
        """Returns count of all positional parameters with default values."""
        
        return _reckon(self.positionalDefaults)
    
    @finalproperty
    def positionalNoDefaultsCount(self): # 0.3.44
        """Returns count of all positional parameters without default values."""
        
        return _reckon(self.positionalNoDefaults)
    
    @finalproperty
    def universalCount(self): # 0.3.44
        """Returns count of all universal parameters."""
        
        return _reckon(self.universal)
    
    @finalproperty
    def universalDefaultsCount(self): # 0.3.44
        """Returns count of all universal parameters with default values."""
        
        return _reckon(self.universalDefaults)
    
    @finalproperty
    def universalNoDefaultsCount(self): # 0.3.44
        """Returns count of all universal parameters without default values."""
        
        return _reckon(self.universalNoDefaults)
    
    @finalproperty
    def keywordCount(self): # 0.3.44
        """Returns count of all keyword parameters."""
        
        return _reckon(self.keyword)
    
    @finalproperty
    def keywordDefaultsCount(self): # 0.3.44
        """Returns count of all keyword parameters with default values."""
        
        return _reckon(self.keywordDefaults)
    
    @finalproperty
    def keywordNoDefaultsCount(self): # 0.3.44
        """Returns count of all keyword parameters without default values."""
        
        return _reckon(self.keywordNoDefaults)
    
    @finalproperty
    def allCount(self): # 0.3.44
        """Returns count of all parameters."""
        
        return _reckon(self.all)
    
    @finalproperty
    def allDefaultsCount(self): # 0.3.44
        """Returns count of all parameters with default values."""
        
        return _reckon(self.allDefaults)
    
    @finalproperty
    def allNoDefaultsCount(self): # 0.3.44
        """Returns count of all parameters without default value."""
        
        return _reckon(self.allNoDefaults)
    
    @finalproperty
    def annotatedCount(self): # 0.3.44
        """Returns count of all parameters which have been annotated a type."""
        
        return _reckon(self.annotated)
    
    @finalproperty
    def annotatedDefaultsCount(self): # 0.3.44
        """Returns count of all parameters which have been annotated a type, and a default value."""
        
        return _reckon(self.annotatedDefaults)
    
    @finalproperty
    def annotatedNoDefaultsCount(self): # 0.3.44
        """Returns count of all parameters which have been annotated a type, however, don't have default value."""
        
        return _reckon(self.annotatedNoDefaults)
    
    @finalproperty
    def variableCount(self): # 0.3.44
        """Returns count of all variable parameters (0-2)."""
        
        return _reckon(self.variable)
        
class MutableString:
    """
    @since 0.3.42
    
    Represents a string, which can be mutated.
    """
    
    ### Initializer ###
    def __init__(self, string, /): # 0.3.42
        
        if type(string) is not str:
            error = TypeError("expected a string")
            raise error
        
        self.__str = list(string)
    
    ### Conversions ###
    def __str__(self): # 0.3.42
        
        if not all([isinstance(e, str) for e in self.__str]):
            error = TypeError("internal variable isn't a string")
            raise error
        
        else:
            return "".join(self.__str)
    
    def __repr__(self): # 0.3.42
        
        return "<{}.{} object :: {}(\"{}\")> ".format(self.__module__, type(self).__name__, type(self).__name__, self.__str__())
    
    def __hash__(self): # 0.3.42
        
        return hash(str(self))
    
    def __format__(self, format_spec): # 0.3.42
        
        if type(format_spec) is not str:
            error = TypeError("expected a string")
            raise error
        
        return format_spec.format(str(self))  
    
    ### Length ###
    def __len__(self): # 0.3.42
        
        return _reckon(self.__str__())
    
    def __reckon__(self): # 0.3.42
        
        return _reckon(self.__str__())
    
    ### Indexes ###
    @__.overload
    def __getitem__(self, value: __.Union[int, slice]) -> str: ...
    
    @__.overload
    def __getitem__(self, value: str) -> int: ...
    
    def __getitem__(self, value): # 0.3.42
        
        if type(value) is int or type(value) is slice:
            
            if type(value) is int and -(_reckon(self.__str) + 1) >= value >= _reckon(self.__str):
                error = IndexError("index out of range")
                raise error
            
            return str(self)[value]
        
        elif type(value) is str:
            
            return str(self).count(value)
        
        else:
            error = TypeError("expected a slice, substring or integer")
            raise error
        
    def __setitem__(self, name, value):
        
        if type(name) is int or type(name) is slice:
                
            if type(name) is int and -(_reckon(self.__str) + 1) >= name >= _reckon(self.__str):
                error = IndexError("index out of range")
                raise error
            
            self.__str[name] = value
            
        elif type(name) is str:
            
            if type(value) is str:
                self.__str = list(self.__str__().replace(name, value))
                
            else:
                error = TypeError("expected string for string indexes")
                raise error
            
        else:
            error = TypeError("expected a slice, substring or integer")
            raise error
        
    def __delitem__(self, name): # 0.3.42
        
        if type(name) is not int and type(name) is not slice:
            error = TypeError("expected a slice or integer")
            raise error
        
        if type(name) is int and -(_reckon(self.__str) + 1) >= name >= _reckon(self.__str):
            error = IndexError("index out of range")
            raise error
        
        del self.__str[name]
        
    ### Other ###
        
    def __add__(self, other): # 0.3.42
        
        if type(other) is type(self):
            
            return type(self)(str(self) + str(other))
        
        elif type(other) is str:
            
            return type(self)(str(self) + other)
        
        else:
            
            error = TypeError("operation with unsupported type of right operand: '{}'".format(type(other).__name__))
            raise error
        
    def __radd__(self, other): # 0.3.42
        
        try:
            
            return self.__add__(other)
        
        except TypeError:
            
            error = TypeError("operation with unsupported type of left operand: '{}'".format(type(other).__name__))
            raise error
        
    def __iadd__(self, other): # 0.3.42
        
        if type(other) is type(self):
            
            self.__str += list(str(other))
        
        elif type(other) is str:
            
            self.__str += list(other)
        
        else:
            
            error = TypeError("operation with unsupported type of right operand: '{}'".format(type(other).__name__))
            raise error
        
        return self
        
    def __mul__(self, other): # 0.3.42
        
        if type(other) is int:
            
            if other > 0:
                return type(self)(str(self) * other)
            
            elif other == 0: # >= 0.3.43
                return type(self)("")
            
            else:
                error = IndexError("expected an integer above zero")
                raise error
            
        else:
            error = TypeError("expected an integer")
            raise error
        
    def __rmul__(self, other): # 0.3.42
        
        try:
            
            return self.__mul__(other)
        
        except TypeError:
            
            error = TypeError("operation with unsupported type of left operand: '{}'".format(type(other).__name__))
            raise error
        
    def __imul__(self, other): # 0.3.42
        
        if type(other) is int:
            
            if other > 0:
                s = str(self)
                self.__str = list(s * other)
            
            else:
                error = IndexError("expected an integer above zero")
                raise error
            
        else:
            error = TypeError("expected an integer")
            raise error
        
        return self
    
    def __mod__(self, other): # 0.3.42
        
        return str(self.__str__() % other)
    
    def __getnewargs__(self): # 0.3.42
        
        return self.__str__().__getnewargs__()
      
    ### Checking ###
    def __contains__(self, key): # 0.3.42
        
        return key in self.__str__() if type(key) is str else str(key) in self.__str__() if type(key) is type(self) else False
    
    def __lt__(self, other): # 0.3.42
        
        return self.__str__() < other if type(other) is str else self.__str__() < str(other) if type(other) is type(self) else False
    
    def __gt__(self, other): # 0.3.42
        
        return self.__str__() > other if type(other) is str else self.__str__() > str(other) if type(other) is type(self) else False
    
    def __le__(self, other): # 0.3.42
        
        return self.__str__() <= other if type(other) is str else self.__str__() <= str(other) if type(other) is type(self) else False
    
    def __ge__(self, other): # 0.3.42
        
        return self.__str__() >= other if type(other) is str else self.__str__() >= str(other) if type(other) is type(self) else False
    
    def __eq__(self, other): # 0.3.42
        
        return self.__str__() == other if type(other) is str else self.__str__() == str(other) if type(other) is type(self) else False
    
    def __ne__(self, other): # 0.3.42
        
        return self.__str__() != other if type(other) is str else self.__str__() != str(other) if type(other) is type(self) else False
    
    ### Other ###
    def clear(self): # 0.3.42
        
        a = [""]
        del a[0]
        self.__str = a
        
    @property
    def value(self): # 0.3.42
        
        return self.__str__()
    
    @value.setter
    def value(self, value): # 0.3.42
        
        if type(value) is type(self):
            
            self.__str = list(str(value))
            
        elif type(value) is str:
            
            self.__str = list(value)
            
        else:
            
            error = TypeError("expected a string or instance of '{}.MutableString'".format(self.__module__))
            raise error
        
    @value.deleter
    def value(self):
        
        error = TypeError("unable to delete property '" + type(self).value.fget.__name__ + "'")
        raise error
    
        
def simpleEnum(etype: type[_T_enum] = __.Enum, boundary: __.Optional[__.FlagBoundary] = None, useArgs = False):
    """
    @since 0.3.42
    
    Globally scoped version of `enum._simple_enum()`
    """
    
    import enum
    
    return __.cast(__.Callable[[type[__.Any]], type[_T_enum]], enum._simple_enum(etype, boundary = boundary, use_args = useArgs))
            
if __name__ == "__main__":
    error = RuntimeError("This file is not for compiling, consider importing it instead.")
    raise error

class StrictEnum:
    """
    @since 0.3.43. *Experimental*
    
    This class decorator allows to create enumerators similar as these in TypeScript.
    
    It doesn't use any kind of solutions from `enum` module. 
    """
    
    def __new__(cls, t: type[_T], /):
        
        if not isinstance(t, type):
            error = TypeError("expected a class")
            raise error
        
        # Don't permit dunder names defined by default in every class (e.g. allow __slots__)
        _receive_user_defined_members = {k: t.__dict__[k] for k in t.__dict__ if k not in (
            "__module__",
            "__firstlineno__", # >= Py3.13
            "__static_attributes__", # >= Py3.13
            "__dict__",
            "__weakref__",
            "__doc__"
        )}
        
        for k in _receive_user_defined_members:
            
            if isinstance(_receive_user_defined_members[k], (__.MethodType, property)) or hasattr(_receive_user_defined_members[k], "__self__"):
                
                error = TypeError("expected attributes only")
                raise error
        
        # Revoke dunder names
        t.__all__ = [k for k in _receive_user_defined_members if not isinstance(_receive_user_defined_members[k], (__.MethodType, property)) and not k.startswith("__") and not k.endswith("__")]
        t = _InternalHelper(t, "no_reassign")
        
        try:
            t = __.cast(type[_T], t())
                
        except:
            error = TypeError("class cannot be marked abstract, or metaclass conflict between base classes")
            raise error
        
        return t

Any = __.Any # >= 0.3.43

if False:
    
    class Unbound:
        """
        @since 0.3.44 (in code)
        
        Indicates unbound variable. Once referenced, throws an error
        """
        
        def __init__(self):
            pass
        
        def __get__(self, instance, owner = None):
            
            if instance is not None:
                error = UnboundLocalError("cannot access local variable '{}' where it is not associated with a value")
                raise error
            
            return type(self)
    
__all__ = sorted([k for k in globals() if not k.startswith("_")]) # 0.3.41: sorted()
__all_deprecated__ = sorted([k for k in globals() if hasattr(globals()[k], "__deprecated__")])
"""
@since 0.3.41

Returns all deprecated declarations within this module.
"""

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error