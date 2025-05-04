"""
**AveyTense Types Collection**

\\@since 0.3.26b3 \\
© 2023-Present Aveyzan // License: MIT \\
https://aveyzan.glitch.me/tense/py/module.types_collection.html
```ts
module aveytense.types_collection
```
Types package for AveyTense. It also contains ABCs (Abstract Base Classes) and exception classes. To 0.3.26rc3 `aveytense.tcs`. \\
Constants have been moved to separate submodule `aveytense.constants`.

Despite Python e.g. in version 3.10 provides union type expression with bar (`|`), in version 3.12 - preceding `type` keyword notations \\
still it is recommended to write the code in accordance to older Python versions.

If downloading `typing_extensions` module went unsuccessfully, try to manually run `pip install typing_extensions`.
"""
from __future__ import annotations

import collections.abc as _collections_abc
import collections as _collections
import hashlib as _hashlib
import os as _os
import subprocess as _subprocess
import sys as _sys

from ._ᴧv_collection._types import *
from .exceptions import ErrorHandler as _E
from .constants import VERSION
from . import util as _util

try:
    import typing_extensions as _typing_ext # type: ignore
except (ModuleNotFoundError, ImportError, NameError):
    _subprocess.run([_sys.executable, "-m", "pip", "install", "typing_extensions"])

import typing_extensions as _typing_ext # type: ignore

NULL = type(None) # 0.3.26b3 (0.3.34 - type[None])
null = NULL # 0.3.41

###### TYPES ######

_var = TypeVar
_uni = Union
_opt = Optional
_cal = Callable
_par = ParamSpec
_pro = Protocol
_lit = Literal

_T = _var("_T")
_P = _par("_P")
_T_cov = _var("_T_cov", covariant = True)
_T_con = _var("_T_con", contravariant = True)
_KT = _var("_KT")
_VT = _var("_VT")

###### ABCs OUTSIDE collections.abc ######
# Most of them are also undefined in _typeshed module, which is uncertain module to import at all.

@runtime
class NotReassignable(_pro[_T_con]):
    """
    \\@since 0.3.26b3

    This class does not support any form of re-assignment, those are augmented \\
    assignment operators: `+=`, `-=`, `*=`, `**=`, `/=`, `//=`, `%=`, `>>=`, `<<=`, \\
    `&=`, `|=`, `^=`. Setting new value also is prohibited.
    """
    __slots__ = ("__weakref__",)
    __op = (
        "; used operator '+='", # 0
        "; used operator '-='", # 1
        "; used operator '*='", # 2
        "; used operator '/='", # 3
        "; used operator '//='", # 4
        "; used operator '**='", # 5
        "; used operator '<<='", # 6
        "; used operator '>>='", # 7
        "; used operator '%='", # 8
        "; used operator '&='", # 9
        "; used operator '|='", # 10
        "; used operator '^='", # 11
    )
    
    def __set__(self, i: Self, v: _T_con):
        
        s = " variable that isn't assignable and re-assignable"
        _E(102, s)
            
    def __iadd__(self, o: _T_con):
        i = 0
        _E(102, self.__op[i])
        
    def __isub__(self, o: _T_con):
        i = 1
        _E(102, self.__op[i])
        
    def __imul__(self, o: _T_con):
        i = 2
        _E(102, self.__op[i])
        
    def __ifloordiv__(self, o: _T_con):
        i = 4
        _E(102, self.__op[i])
        
    def __idiv__(self, o: _T_con):
        i = 3
        _E(102, self.__op[i])
        
    def __itruediv__(self, o: _T_con):
        i = 3
        _E(102, self.__op[i])
        
    def __imod__(self, o: _T_con):
        i = 8
        _E(102, self.__op[i])
        
    def __ipow__(self, o: _T_con):
        i = 5
        _E(102, self.__op[i])
        
    def __ilshift__(self, o: _T_con):
        i = 6
        _E(102, self.__op[i])
        
    def __irshift__(self, o: _T_con):
        i = 7
        _E(102, self.__op[i])
        
    def __iand__(self, o: _T_con):
        i = 9
        _E(102, self.__op[i])
        
    def __ior__(self, o: _T_con):
        i = 10
        _E(102, self.__op[i])
        
    def __ixor__(self, o: _T_con):
        i = 11
        _E(102, self.__op[i])

@runtime
class NotComparable(_pro[_T_con]):
    """
    \\@since 0.3.26b3

    Cannot be compared with operators `==`, `!=`, `>`, `<`, `>=`, `<=`, `in`
    """
    __slots__ = ()
    __op = (
        "; used operator '<'", # 0
        "; used operator '>'", # 1
        "; used operator '<='", # 2
        "; used operator '>='", # 3
        "; used operator '=='", # 4
        "; used operator '!='", # 5
        "; used operator 'in'", # 6
    )
    def __lt__(self, other: _T_con):
        i = 0
        _E(102, self.__op[i])
        
    def __gt__(self, other: _T_con):
        i = 1
        _E(102, self.__op[i])
        
    def __le__(self, other: _T_con):
        i = 2
        _E(102, self.__op[i])
        
    def __ge__(self, other: _T_con):
        i = 3
        _E(102, self.__op[i])
        
    def __eq__(self, other: _T_con):
        i = 4
        _E(102, self.__op[i])
        
    def __ne__(self, other: _T_con):
        i = 5
        _E(102, self.__op[i])
        
    def __contains__(self, other: _T_con):
        i = 6
        _E(102, self.__op[i])

# class Deprecated:
#    """
#    \\@since 0.3.26b3 (experimental) (alias since 0.3.26)
#
#    This class marks a class as deprecated. Every keyword parameter accord to \\
#    the ones `warnings.warn()` method has. Instead of `skip_file_prefixes` you \\
#    can also use `skipFilePrefixes` and instead of `stacklevel` - `stackLevel`. \\
#    Excluded is only `category` parameter, which has value `DeprecationWarning`.
#
#    Parameters: `message`, `stacklevel`, `source`, `skip_file_prefixes`, as in:
#    ```py \\
#    class IAmDeprecatedClass(Deprecated, message = ..., stacklevel = ..., ...)
#    ```
#    """
    # def __init_subclass__(cls, /, *args, **kwds):
    #     wa.simplefilter("always", DeprecationWarning)
    #     wa.warn(
    #         str(kwds["message"]) if "message" in kwds else "Deprecated class.",
    #         DeprecationWarning,
    #         int(kwds["stacklevel"]) if "stacklevel" in kwds else 2,
    #         kwds["source"] if "source" in kwds else None,
    #         skip_file_prefixes = kwds["skipFilePrefixes"] if "skipFilePrefixes" in kwds else kwds["skip_file_prefixes"] if "skip_file_prefixes" in kwds else ()
    #     )
    #    wa.simplefilter("default", DeprecationWarning)

@runtime
class NotIterable(_pro):
    """
    \\@since 0.3.26b3

    Cannot be used with `for` loop
    """
    # usage as in typing module (0.3.26c3)
    __iter__ = None

@runtime
class NotInvocable(_pro[_T_cov]):
    """
    \\@since 0.3.26rc1

    Cannot be called as a function (as `self()`)
    """
    def __call__(self, *args, **kwds):
        _E(107)

@runtime
class NotUnaryOperable(_pro):
    """
    \\@since 0.3.26rc1

    Cannot be used with preceding operators `+`, `-` and `~`
    """
    def __pos__(self):
        _E(108)
        
    def __neg__(self):
        _E(108)
        
    def __invert__(self):
        _E(108)

# @runtime
# class AbroadOperable(_pro[_T_cov]):
    """
    \\@since 0.3.26c2?

    An ABC with one method `__abroad__`.

    This magic method is used for `abroad()` function
    """
    # def __abroad__(self) -> _T_cov: ...
    
class Allocator:
    """
    \\@since 0.3.27b3

    An allocator class. Classes extending this class have access to `__alloc__` magic method, \\
    but it is advisable to use it wisely.
    """
    __a = bytearray()

    def __init__(self, b: _uni[bytearray, BytearrayConvertible], /):
        
        if isinstance(b, BytearrayConvertible):
            self.__a = b.__bytearray__()
            
        elif isinstance(b, bytearray):
            self.__a = b
            
        else:
            error = TypeError("Expected a bytearray object or object of class extending 'BytearrayConvertible' class")
            raise error
    
    def __alloc__(self):
        return self.__a.__alloc__()

if False: # < 0.3.27rc1
    @deprecated("Deprecated since 0.3.27a3, use class 'tense.types_collection.ClassVar' instead.")
    def classvar(v: _T, /):
        """
        \\@since 0.3.26b3 (experimental) \\
        \\@deprecated 0.3.27a3

        Transform variable in a class to a class variable.

        This will be valid only whether this function is \\
        invoked inside a class.
        Use it as:
        ```py \\
        class Example:
            test = classvar(96000) # has value 96000
        ```
        """
        class _t:
            _v: ClassVar[_T] = v
        return _t._v

    @deprecated("Deprecated since 0.3.26c3, use class 'tense.FinalVar' instead.")
    def finalvar(v: _T, /):
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c3 (use `tense.FinalVar` class-like instead)

        Use it as:
        ```py \\
        reassign_me = finalvar(96000) # has value 96000
        reassign_me += 3 # error
        ```
        """
        return _util.FinalVar(v)
    

RichComparable = _uni[LeastComparable[Any], GreaterComparable[Any]]

EnchantedBookQuantity = _lit[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36] # 0.3.26b3

FileType = _uni[str, int, bytes, _os.PathLike[str], _os.PathLike[bytes]] # 0.3.26b3

if False: # < 0.3.41
    
    
    FileMode = _lit[
        'r+', '+r', 'rt+', 'r+t', '+rt', 'tr+', 't+r', '+tr', 'w+', '+w', 'wt+', 'w+t', '+wt', 'tw+', 't+w', '+tw', 'a+', '+a', 'at+', 'a+t', '+at', 'ta+', 't+a', '+ta', 'x+', '+x', 'xt+',
        'x+t', '+xt', 'tx+', 't+x', '+tx', 'w', 'wt', 'tw', 'a', 'at', 'ta', 'x', 'xt', 'tx', 'r', 'rt', 'tr', 'U', 'rU', 'Ur', 'rtU', 'rUt', 'Urt', 'trU', 'tUr', 'Utr', 'rb+', 'r+b', '+rb',
        'br+', 'b+r', '+br', 'wb+', 'w+b', '+wb', 'bw+', 'b+w', '+bw', 'ab+', 'a+b', '+ab', 'ba+', 'b+a', '+ba', 'xb+', 'x+b', '+xb', 'bx+', 'b+x', '+bx', 'rb', 'br', 'rbU', 'rUb', 'Urb',
        'brU', 'bUr', 'Ubr', 'wb', 'bw', 'ab', 'ba', 'xb', 'bx'
    ] # 0.3.26b3
    FileOpener = _cal[[str, int], int] # 0.3.26b3
    TicTacToeBoard = list[list[str]] # 0.3.26b3

    AnySequenceForPick = _uni[Sequence[_T], MutableSequence[_T], Uniqual[_T], MutableUniqual[_T]] # 0.3.26c3

    SequencePickType = _uni[
        list[_T],
        tuple[_T, ...],
        set[_T],
        frozenset[_T],
        AnySequenceForPick[_T],
        ListConvertible[_T]
    ] # 0.3.26c3

    SequencePickNGT = _uni[
        list,
        tuple,
        set,
        frozenset,
        Sequence,
        ListConvertible
    ] # 0.3.26c3

Hash = type(_hashlib.sha1())  # it can appear as local hashlib._Hash class in Python versions before 3.13 (0.3.41)
"\\@since 0.3.26rc3"
    
VarLenHash = type(_hashlib.shake_256()) # it can appear as local hashlib._VarLenHash class in Python versions before 3.13 (0.3.41)
"\\@since 0.3.26rc3"

BlakeHash = _hashlib.blake2b
"\\@since 0.3.26rc3"

List = list # 0.3.26b3
"\\@since 0.3.26b3"

Tuple = tuple # 0.3.26b3
"\\@since 0.3.26b3"

Deque = _collections.deque # 0.3.26b3
"\\@since 0.3.26b3"

Dict = dict # 0.3.26b3
"\\@since 0.3.26b3"

Bytes = bytes # 0.3.26b3
"\\@since 0.3.26b3"

ByteArray = bytearray # 0.3.26b3
"\\@since 0.3.26b3"

Filter = filter # 0.3.26b3
"\\@since 0.3.26b3"

Type = type # 0.3.26b3
"\\@since 0.3.26b3"

Zip = zip # 0.3.26b3
"\\@since 0.3.26b3"

Slice = slice # 0.3.26c1
"\\@since 0.3.26rc1"

Object = object
"\\@since 0.3.26rc3"

ColorType = IntegerStringUnion[None] # since 0.3.25, renamed from SupportsColor (0.3.26b3)
ColourType = ColorType # 0.3.26b3

if False: # < 0.3.41 (if no removal version was provided, then all of these were removed in 0.3.41)
    
    class _FinalVar(NamedTuple, Generic[_T]):
        x: _T
    
    ModernReplace = _uni[list[_T], tuple[_T, ...], _T]
    # since 0.3.25, expected string; renamed from SupportsModernReplace (0.3.26b3)
    PickSequence = _uni[list[_T], tuple[_T, ...], set[_T], frozenset[_T], _collections.deque[_T], _collections_abc.Sequence[_T], _collections_abc.MutableSequence[_T]]
    # since 0.3.25, added support for Sequence and MutableSequence, renamed from SupportsPick (0.3.26b3)
    SanitizeMode = _lit[0, 1, 2, 3, 4, 5]
    # since 0.3.25, renamed from SupportsSanitizeMode (0.3.26b3)
    SupportsAbroadDivisor = _uni[int, float]
    # since 0.3.25; removed in 0.3.26b3, use FloatOrInteger instead
    ShuffleType = _uni[str, list[_T], _collections_abc.MutableSequence[_T]]
    # since 0.3.26rc1
    TypeOrFinalVarType = _uni[_T, _FinalVar[_T]]
    # since 0.3.26rc1
    
    __author__ = "Aveyzan <aveyzan@gmail.com>"
    "\\@since 0.3.26rc3"
    __license__ = "MIT"
    "\\@since 0.3.26rc3"
    __version__ = VERSION
    "\\@since 0.3.26rc3"

TenseVersionType = tuple[_T, _T, _T]
# since 0.3.25, renamed from SupportsTenseVersion (0.3.26b3)

FloatOrInteger = _uni[int, float]
# since 0.3.25

ProbabilityType = _uni[_T, list[_opt[_T]], tuple[_T, _opt[_T]], dict[_T, _opt[_T]], _collections.deque[_opt[_T]], set[_opt[_T]], frozenset[_opt[_T]]]
# since 0.3.25, expected integer; renamed from SupportsProbabilityValuesAndFrequencies (0.3.26b3)

_IntegerConvertible = _uni[str, Buffer, IntegerConvertible, Indexable, Truncable] # since 0.3.26rc1
_FloatConvertible = _uni[str, Buffer, FloatConvertible, Indexable] # since 0.3.26rc1
_ComplexConvertible = _uni[complex, FloatConvertible, Indexable] # since 0.3.26rc1

@deprecated("Deprecated since 0.3.41, will be removed on 0.3.48. Migrate to 'int' builtin instead")
class Integer:
    """
    \\@since 0.3.26b3
    
    Equivalent to `int`. Once instantiated, it returns \\
    integer of type `int`. (0.3.26c1)
    """
    def __new__(cls, x: _IntegerConvertible = ..., /):
        """
        \\@since 0.3.26b3
        
        Equivalent to `int`. Once instantiated, it returns \\
        integer of type `int`. (0.3.26c1)
        """
        return int(x)
    
    def __instancecheck__(self, obj: object, /) -> TypeIs[int]:
        return isinstance(obj, int)

@deprecated("Deprecated since 0.3.41, will be removed on 0.3.48. Migrate to 'float' builtin instead")
class Float:
    """
    \\@since 0.3.26b3
    
    Equivalent to `float`. Once instantiated, it returns \\
    number of type `float`. (0.3.26c1)
    """
    def __new__(cls, x: _FloatConvertible = ..., /):
        """
        \\@since 0.3.26b3
        
        Equivalent to `float`. Once instantiated, it returns \\
        number of type `float`. (0.3.26c1)
        """
        return float(x)
    
    def __instancecheck__(self, obj: object, /) -> TypeIs[float]:
        return isinstance(obj, float)

@deprecated("Deprecated since 0.3.41, will be removed on 0.3.48. Migrate to 'complex' builtin instead")
class Complex:
    """
    \\@since 0.3.26b3
    
    Equivalent to `complex`. Once instantiated, it returns \\
    number of type `complex`. (0.3.26c1)
    """
    def __new__(cls, r: _uni[ComplexConvertible, _ComplexConvertible] = ..., i: _ComplexConvertible = ..., /):
        """
        \\@since 0.3.26b3
        
        Equivalent to `complex`. Once instantiated, it returns \\
        number of type `complex`. (0.3.26c1)
        """
        return complex(r, i)
    
    def __instancecheck__(self, obj: object, /) -> TypeIs[complex]:
        return isinstance(obj, complex)

@deprecated("Deprecated since 0.3.41, will be removed on 0.3.48. Migrate to 'str' builtin instead")
class String:
    """
    \\@since 0.3.26b3
    
    Equivalent to `str`. Once instantiated, it returns \\
    string of type `str`. (0.3.26c1)
    """
    def __new__(cls, x: object = ..., /):
        """
        \\@since 0.3.26b3
        
        Equivalent to `str`. Once instantiated, it returns \\
        string of type `str`. (0.3.26c1)
        """
        return str(x)
    
    def __instancecheck__(self, obj: object, /) -> TypeIs[str]:
        return isinstance(obj, str)

@deprecated("Deprecated since 0.3.41, will be removed on 0.3.48. Migrate to 'bool' builtin instead")
class Boolean:
    """
    \\@since 0.3.26b3
    
    Equivalent to `bool`. Once instantiated, it returns \\
    boolean of type `bool`. (0.3.26c1)
    """
    def __new__(cls, x: object = ..., /):
        """
        \\@since 0.3.26b3
        
        Equivalent to `bool`. Once instantiated, it returns \\
        boolean of type `bool`. (0.3.26c1)
        """
        return bool(x)
    
    def __instancecheck__(self, obj: object, /) -> TypeIs[bool]:
        return obj is True or obj is False

def _isAbstract(o: object):
    "\\@since 0.3.26rc3"
    
    from inspect import isabstract
    
    return isabstract(o)

################ TypeScript References ################
false = False
"\\@since 0.3.26rc3"
true = True
"\\@since 0.3.26rc3"
never = Never
"\\@since 0.3.26rc3"
number = Union[int, str] # on JavaScript there is no 'complex' number type
"\\@since 0.3.26rc3"
void = type(None)
"\\@since 0.3.26rc3"

__all__ = sorted([n for n in globals() if n[:1] != "_"])
"\\@since 0.3.26rc1? Whole gamut of declarations written in `aveytense.types_collection` module"

__all_deprecated__ = sorted([n for n in globals() if hasattr(globals()[n], "__deprecated__")])
"""
@since 0.3.41

Returns all deprecated declarations within this module.
"""

__constants__ = sorted([n for n in globals() if n[:1] != "_" and n.isupper()])
"\\@since 0.3.26c3. All constants in `tense.types_collection` module"

__non_constants__ = sorted([n for n in globals() if n[:1] != "_" and not n.isupper()])
"\\@since 0.3.26c3. All non-constants (functions, classes, type aliases) in `aveytense.types_collection` module"

__typing_util__ = sorted([
    # let me know if I missed some types from typing module!
    Optional.__name__,
    Union.__name__,
    Callable.__name__,
    Concatenate.__name__,
    Pack.__name__ + " (alias to 'Concatenate')",
    Annotated.__name__,
    TypeAlias.__name__,
    "TypeAliasType", # its __name__ is instance of 'property' built-in
    TypeGuard.__name__,
    TypeIs.__name__,
    Unpack.__name__,
    "Any",
    Final.__name__,
    Literal.__name__,
    LiteralString.__name__,
    ClassVar.__name__,
    Generic.__name__,
    Protocol.__name__,
    "NoDefault", # its __name__ is Any
    NotRequired.__name__,
    Required.__name__,
    Self.__name__,
    "SpecVar (known as ParamSpec)", # its __name__ is instance of 'property' built-in
    SpecVarArgs.__name__ + " (known as ParamSpecArgs)",
    SpecVarKwargs.__name__ + " (known as ParamSpecKwargs)",
    NamedTuple.__name__,
    NewType.__name__,
    NoReturn.__name__,
    ForwardRef.__name__,
])
"\\@since 0.3.26c3. Utility types from `typing` module in `aveytense.tcs` module"

__abc__ = sorted([n for n in globals() if n[:1] != "_" and ((_isAbstract(globals()[n]) or n.startswith((
    "Async", "Bitwise"
)) and not n.endswith(("Provider", "Abc"))) or n.endswith((
    "Operable",
    "Reassignable",
    "Comparable",
    "Collection",
    "Convertible",
    "Representable"
)) or n in (
    "Invocable",
    "Absolute",
    "Negative",
    "Positive",
    "Iterable",
    "Reversible",
    "Formattable",
    "Ceilable",
    "Floorable",
    "Truncable",
    "Awaitable",
    "Containable",
    "Indexed",
    "Indexable",
    "Hashable"
    )
)])
"\\@since 0.3.26c3. ABCs (Abstract Base Classes) in `tense.tcs` module"

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error
