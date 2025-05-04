"""
**AveyTense ABC** \n
\\@since 0.3.26rc3 \\
© 2024-Present Aveyzan // License: MIT
```
module aveytense._abc
```
Abstract base classes (ABC) located in `aveytense.types_collection` module. This module \\
also includes `Final`, `Abstract` and `Frozen` classes, along with their decorator
equivalents.
"""

from __future__ import annotations
import sys as _sys

### commented unused imports

import abc as _abc
# import enum as _enum
# import inspect as _inspect
# import os as _os
# import tkinter as _tkinter
# import typing as _typing
# import typing_extensions as _typing_ext
# import subprocess as _subprocess
# import sys as _sys
# import zipfile as _zipfile

from . import _init_types as _types
from ._exceptions import *

# subscripting check (0.3.42)
if _sys.version_info >= (3, 9):

    from collections.abc import (
        AsyncGenerator as AsyncGenerator,
        AsyncIterable as AsyncIterable,
        AsyncIterator as AsyncIterator,
        Awaitable as Awaitable,
        Collection as Collection,
        Container as Container,
        Coroutine as Coroutine,
        Generator as Generator,
        Hashable as Hashable,
        ItemsView as ItemsView,
        Iterable as Iterable,
        Iterator as Iterator,
        KeysView as KeysView,
        Mapping as Mapping,
        MappingView as MappingView,
        MutableMapping as MutableMapping,
        MutableSequence as MutableSequence,
        MutableSet as MutableUniqual,
        Reversible as Reversible,
        Sequence as Sequence,
        Set as Uniqual,
        Sized as Sized,
        ValuesView as ValuesView
    )

else:
    
    from typing import (
        AsyncGenerator as AsyncGenerator,
        AsyncIterable as AsyncIterable,
        AsyncIterator as AsyncIterator,
        Awaitable as Awaitable,
        Collection as Collection,
        Container as Container,
        Coroutine as Coroutine,
        Generator as Generator,
        Hashable as Hashable,
        ItemsView as ItemsView,
        Iterable as Iterable,
        Iterator as Iterator,
        KeysView as KeysView,
        Mapping as Mapping,
        MappingView as MappingView,
        MutableMapping as MutableMapping,
        MutableSequence as MutableSequence,
        MutableSet as MutableUniqual,
        Reversible as Reversible,
        Sequence as Sequence,
        Set as Uniqual,
        Sized as Sized,
        ValuesView as ValuesView
    )

from os import PathLike as PathLike

del ErrorHandler # not for export

_pro = _types.Protocol
_var = _types.TypeVar
_opt = _types.Optional

_T_sb_cov = _var("_T_sb_cov", str, bytes, covariant = True) # sb = str, bytes
_T_con = _var("_T_con", contravariant = True)
_T_cov = _var("_T_cov", covariant = True)
_KT_cov = _var("_KT_cov", covariant = True)
_KT_con = _var("_KT_con", contravariant = True)
_VT_cov = _var("_VT_cov", covariant = True)
# _T_yield_cov = _var("_T_yield_cov", covariant = True)
# _T_send_con = _var("_T_send_con", contravariant = True, default = None) # default None since 0.3.27a5
# _T_return_cov = _var("_T_return_cov", covariant = True, default = None) # default None since 0.3.27a5
# _T_send_con_nd = _var("_T_send_con_nd", contravariant = True) # since 0.3.27a5
# _T_return_cov_nd = _var("_T_return_cov_nd", covariant = True) # since 0.3.27a5

###### ABCs REFERRED FROM collections.abc ######
# in order as in https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes


### Aliases ###
Containable = Container
InComparable = Container
Invocable = _types.Callable
LenOperable = Sized
Sizeable = Sized
    
if _sys.version_info < (0, 3, 43):
    
    # all below: >= 0.3.32; < 0.3.34
    AnySequence = Sequence
    AnyMutableSequence = MutableSequence
    AnyMapping = Mapping
    AnyMutableMapping = MutableMapping
    AnyUniqual = Uniqual
    AnyMutableUniqual = MutableUniqual
    
    ContainerAbc = _Container
    "\\@since 0.3.26rc3"
    IterableAbc = _Iterable
    "\\@since 0.3.26rc3"
    IteratorAbc = _Iterator
    "\\@since 0.3.26rc3"

    @_types.runtime
    class Containable(_pro[_T_con]):
        
        """
        \\@since 0.3.26rc1. [`collections.abc.Container`](https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes)

        An ABC with one method `__contains__`, which equals invoking `value in self`. \\
        Type parameter there is contravariant, and equals type for `value` parameter.
        """
        
        def __contains__(self, value: _T_con) -> bool: ...

    class InComparable(Containable[_T_cov]):
        """
        \\@since 0.3.26rc1. [`collections.abc.Container`](https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes)

        Alias to `Containable`

        An ABC with one method `__contains__`, which equals invoking `value in self`. \\
        Type parameter there is contravariant, and equals type for `value` parameter.
        """
        ...

    Container = InComparable
    "\\@since 0.3.26rc3. *aveytense._abc.Container*"


    @_types.runtime
    class Hashable(_pro):
        """
        \\@since 0.3.26rc1. [`collections.abc.Hashable`](https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes)

        An ABC with one method `__hash__`, which equals invoking `hash(self)`.
        """
        @_abc.abstractmethod
        def __hash__(self) -> int: ...

    @_types.runtime
    class Iterable(_pro[_T_cov]): # type: ignore
        """
        \\@since 0.3.26b3. [`collections.abc.Iterable`](https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes)

        An ABC with one method `__iter__`, which equals invoking `for x in self: ...`. \\
        Returned iterator type is addicted to covariant type parameter.
        """
        @_abc.abstractmethod
        def __iter__(self) -> Iterator[_T_cov]: ...

    @_types.runtime
    class Iterator(Iterable[_T_cov], _pro[_T_cov]):
        """
        \\@since 0.3.26b3. [`collections.abc.Iterator`](https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes)

        An ABC with methods `__next__` and `__iter__`: \\
        `next(self)` + `for x in self`
        """
        @_abc.abstractmethod
        def __next__(self) -> _T_cov: ...

    @_types.runtime
    class Reversible(Iterable[_T_cov], _pro[_T_cov]):
        """
        \\@since 0.3.26rc2. [`collections.abc.Reversible`](https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes)

        An ABC with one method `__reversed__`, which equals invoking `reversed(self)`. \\
        Returned type is addicted to covariant type parameter (iterator of type parameter). \\
        This ABC also inherits from `Iterable` class.
        """
        def __reversed__(self) -> Iterator[_T_cov]: ...

    @_types.runtime
    class Awaitable(_pro[_T_cov]):
        """
        \\@since 0.3.26rc1. See [`collections.abc.Awaitable`](https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes)

        An ABC with one method `__await__`, which equals invoking `await self`. \\
        Returned type is addicted to covariant type parameter.
        """
        def __await__(self) -> Generator[_types.Any, _types.Any, _T_cov]: ...

    @_types.runtime
    class Sizeable(_pro):
        """
        \\@since 0.3.26rc3. [`collections.abc.Sized`](https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes)

        An ABC with one method `__len__`, which equals invoking `len(self)`.
        """
        # as in typing.pyi -> Sized
        @_abc.abstractmethod
        def __len__(self) -> int: ...

    Sized = Sizeable
    "\\@since 0.3.26rc3. *tense.types_collection.Sizeable*"

    @_types.runtime
    class Invocable(_pro[_T_cov]): # self() (to prevent name conflict with typing.Callable)
        """
        \\@since 0.3.26rc1. [`collections.abc.Callable`](https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes)

        An ABC with one method `__call__`, which equals invoking `self(...)`. \\
        Returned type is addicted to covariant type parameter.
        """
        def __call__(self, *args, **kwds) -> _T_cov: ...

    class LenOperable(Sizeable):
        """
        \\@since 0.3.26rc1. [`collections.abc.Sized`](https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes)

        An ABC with one method `__len__`, which equals invoking `len(self)`.
        """
        ...
        
    @_types.runtime
    class Hashable(_pro):
        """
        \\@since 0.3.26rc1

        An ABC with one method `__hash__`, which equals invoking `hash(self)`.
        """
        def __hash__(self) -> int: ...

# these are here to faciliate type inspection
# all removed on 0.3.34
if False:
    class AnySequence(_collections_abc.Sequence[_types.Any]): ... # since 0.3.32
    class AnyMutableSequence(_collections_abc.MutableSequence[_types.Any]): ... # since 0.3.32
    class AnyMapping(_collections_abc.Mapping[_types.Any, _types.Any]): ... # since 0.3.32
    class AnyMutableMapping(_collections_abc.MutableMapping[_types.Any, _types.Any]): ... # since 0.3.32
    class AnyUniqual(_collections_abc.Set[_types.Any]): ... # since 0.3.32
    class AnyMutableUniqual(_collections_abc.MutableSet[_types.Any]): ... # since 0.3.32

###### ABCs OUTSIDE collections.abc ######
# Most of them are also undefined in _typeshed module, which is uncertain module to import at all.

@_types.runtime
class ItemGetter(_pro[_T_con, _T_cov]): # v = self[key] (type determined by _T_cov)
    """
    \\@since 0.3.26rc3

    An ABC with one method `__getitem__`. Type parameters:
    - first equals type for `key`
    - second equals returned type

    This method is invoked whether we want to get value \\
    via index notation `self[key]`, as instance of the class.
    """
    def __getitem__(self, key: _T_con, /) -> _T_cov: ...

@_types.runtime
class ClassItemGetter(_pro): # v = self[key] (not instance)
    """
    \\@since 0.3.26rc3

    An ABC with one method `__class_getitem__`. No type parameters.

    This method is invoked whether we want to get value \\
    via index notation `self[key]`, as reference to the class.
    """
    def __class_getitem__(cls, item: _types.Any, /) -> _types.GenericAlias: ...

class SizeableItemGetter(Sizeable, ItemGetter[int, _T_cov]):
    """
    \\@since 0.3.27a3

    An ABC with methods `__len__` and `__getitem__`. Type parameters:
    - first equals returned type for `__getitem__`
    """
    ...

@_types.runtime
class ItemSetter(_pro[_T_con, _T_cov]): # self[key] = value
    """
    \\@since 0.3.26rc3

    An ABC with one method `__setitem__`. Type parameters:
    - first equals type for `key`
    - second equals type for `value`

    This method is invoked whether we want to set a new value for \\
    specific item accessed by `key`, as `self[key] = value`.
    """
    def __setitem__(self, key: _T_con, value: _T_cov) -> None: ...

@_types.runtime
class ItemDeleter(_pro[_T_con]): # del self[key]
    """
    \\@since 0.3.26rc3

    An ABC with one method `__delitem__`. Type parameters:
    - first equals type for `key`

    This method is invoked whether we want to delete specific item \\
    using `del` keyword as `del self[key]`.
    """
    def __delitem__(self, key: _T_con, /) -> None: ...

@_types.runtime
class Getter(_pro[_T_cov]):
    """
    \\@since 0.3.26

    An ABC with one method `__get__`. Type parameters:
    - first equals returned type
    """
    def __get__(self, instance: object, owner: _opt[type] = None, /) -> _T_cov: ...

@_types.runtime
class Setter(_pro[_T_con]):
    """
    \\@since 0.3.27a3

    An ABC with one method `__set__`. Type parameters:
    - first equals type for `value`
    """
    def __set__(self, instance: object, value: _T_con, /) -> None: ...

class KeysProvider(ItemGetter[_KT_con, _VT_cov]):
    """
    \\@since 0.3.26

    An ABC with one method `keys`. Type parameters:
    - first equals key
    - second equals value
    """
    def keys(self) -> Iterable[_KT_con]: ...

@_types.runtime
class ItemsProvider(_pro[_KT_cov, _VT_cov]):
    """
    \\@since 0.3.26

    An ABC with one method `items`. Type parameters:
    - first equals key
    - second equals value
    """
    def items(self) -> Uniqual[tuple[_KT_cov, _VT_cov]]: ...

@_types.runtime
class BufferReleaser(_pro):
    """
    \\@since 0.3.26

    An ABC with one method `__release_buffer__`. No type parameters
    """
    def __release_buffer__(self, buffer: memoryview, /) -> None: ...

@_types.runtime
class NewArgumentsGetter(_pro[_T_cov]):
    """
    \\@since 0.3.26

    An ABC with one method `__getnewargs__`. Type parameters:
    - first equals type for returned tuple
    """
    def __getnewargs__(self) -> tuple[_T_cov]: ...

class ItemManager(
    ItemGetter[_T_con, _T_cov],
    ItemSetter[_T_con, _T_cov],
    ItemDeleter[_T_con]
):
    """
    \\@since 0.3.26rc3

    An ABC with following methods:
    - `__getitem__` - two type parameters (key type, return type)
    - `__setitem__` - two type parameters (key type, return type)
    - `__delitem__` - one type parameter (key type)
    """
    ...

@_types.runtime
class SubclassHooker(_pro):
    """
    \\@since 0.3.26

    An ABC with one method `__subclasshook__`. No type parameters.

    Description: \\
    "Abstract classes can override this to customize `issubclass()`. \\
    This is invoked early on by `abc.ABCMeta.__subclasscheck__()`. \\
    It should return True, False or NotImplemented. If it returns \\
    NotImplemented, the normal algorithm is used. Otherwise, it \\
    overrides the normal algorithm (and the outcome is cached)."
    """
    def __subclasshook__(cls, subclass: type, /) -> bool: ...

@_types.runtime
class LengthHintProvider(_pro):
    """
    \\@since 0.3.26rc3

    An ABC with one method `__length_hint__`. No type parameters.

    This method is invoked like in case of `list` built-in, just on behalf of specific class. \\
    It should equal invoking `len(self())`, as seen for `list`: "Private method returning \\
    an estimate of `len(list(it))`". Hard to explain this method, still, this class will be kept. 
    """
    def __length_hint__(self) -> int: ...

@_types.runtime
class FSPathProvider(_pro[_T_sb_cov]):
    """
    \\@since 0.3.27a3. See also [`os.PathLike`](https://docs.python.org/3/library/os.html#os.PathLike)

    An ABC with one method `__fspath__`. Type parameter \\
    needs to be either `str` or `bytes` unrelated to both. \\
    That type is returned via this method.
    """
    def __fspath__(self) -> _T_sb_cov: ...

@_types.runtime
class BytearrayConvertible(_pro):
    """
    \\@since 0.3.26rc3

    An unofficial ABC with one method `__bytearray__`, which *has* to equal invoking `bytearray(self)`.

    In reality there is no such magic method as `__bytearray__`, but I encourage \\
    Python working team to think about it.
    """
    def __bytearray__(self) -> bytearray: ...

@_types.runtime
class ListConvertible(_pro[_T_cov]):
    """
    \\@since 0.3.26rc3

    An unofficial ABC with one method `__list__`, which *has* to equal invoking `list(self)`. \\
    Returned list type is addicted to covariant type parameter.

    In reality there is no such magic method as `__list__`, but I encourage \\
    Python working team to think about it. Equivalent for this class will be \\
    generic ABC `SupportsList`. Since 0.3.27a3 this method is called `__tlist__`
    """
    def __tlist__(self) -> list[_T_cov]:
        "\\@since 0.3.26rc3. Return `list(self)`"
        ...

@_types.runtime
class TupleConvertible(_pro[_T_cov]):
    """
    \\@since 0.3.26rc3

    An unofficial ABC with one method `__tuple__`, which *has* to equal invoking `tuple(self)`. \\
    Returned tuple type is addicted to covariant type parameter.

    In reality there is no such magic method as `__tuple__`, but I encourage \\
    Python working team to think about it. Equivalent for this class will be \\
    generic ABC `SupportsTuple`. Since 0.3.27a3 this method is called `__ttuple__`
    """
    def __ttuple__(self) -> tuple[_T_cov, ...]:
        "\\@since 0.3.26rc3. Return `tuple(self)`"
        ...

@_types.runtime
class SetConvertible(_pro[_T_cov]):
    """
    \\@since 0.3.26rc3

    An unofficial ABC with one method `__set_init__`, which *has* to equal invoking `set(self)`. \\
    Returned set type is addicted to covariant type parameter.

    In reality there is no such magic method as `__set_init__`, but I encourage \\
    Python working team to think about it. Other suggested idea: `__se__`, since \\
    `__set__` is already in use. Since 0.3.27a3 this method is called `__tset__`
    """
    def __tset__(self) -> set[_T_cov]:
        "\\@since 0.3.26rc3. Return `set(self)`"
        ...

@_types.runtime
class ReckonOperable(_pro):
    """
    \\@since 0.3.26rc1

    An unofficial ABC with one method `__reckon__`, which equals `aveytense.reckon(self)`. \\
    Returned type is always an integer.
    """
    def __reckon__(self) -> int:
        """
        \\@since 0.3.26rc1

        Return `reckon(self)`.
        """
        ...

@_types.runtime
class Absolute(_pro[_T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__abs__`, which equals invoking `abs(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __abs__(self) -> _T_cov: ...

@_types.runtime
class Truncable(_pro[_T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__trunc__`, which equals invoking `math.trunc(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __trunc__(self) -> _T_cov: ...

@_types.runtime
class BooleanConvertible(_pro):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__bool__` which equals invoking `bool(self)`. \\
    To keep accordance with Python 2, there is also method `__nonzero__`, \\
    which you are encouraged to use the same way as `__bool__`. Preferred use::

        def __bool__(self): ... # some code
        def __nonzero__(self): return self.__bool__()
    """
    def __bool__(self) -> bool: ...
    def __nonzero__(self) -> bool: ...

@_types.runtime
class IntegerConvertible(_pro):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__int__`, which equals invoking `int(self)`
    """
    def __int__(self) -> int: ...

@_types.runtime
class FloatConvertible(_pro):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__float__`, which equals invoking `float(self)`
    """
    def __float__(self) -> float: ...

@_types.runtime
class ComplexConvertible(_pro):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__complex__`, which equals invoking `complex(self)`
    """
    def __complex__(self) -> complex: ...

@_types.runtime
class BytesConvertible(_pro):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__bytes__`, which equals invoking `bytes(self)`
    """
    def __bytes__(self) ->  bytes: ...

if True:
    
    @_types.deprecated("Deprecated since unicode() function doesn't exist. Deprecated since 0.3.41, and will be removed on 0.3.48")
    @_types.runtime
    class UnicodeRepresentable(_pro):
        """
        \\@since 0.3.26rc3

        An ABC with one method `__unicode__`, which equals invoking `unicode(self)`
        """
        def __unicode__(self) -> str: ...

@_types.runtime
class BinaryRepresentable(_pro):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__bin__`, which equals invoking `bin(self)`.

    In reality there is no such magic method as `__bin__`, but I encourage \\
    Python working team to think about it.
    """
    def __bin__(self) -> str: ...

@_types.runtime
class OctalRepresentable(_pro):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__oct__`, which equals invoking `oct(self)`
    """
    def __oct__(self) -> str: ...

@_types.runtime
class HexadecimalRepresentable(_pro):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__hex__`, which equals invoking `hex(self)`
    """
    def __hex__(self) -> str: ...

@_types.runtime
class StringConvertible(_pro):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__str__`, which equals invoking `str(self)`
    """
    def __str__(self) -> str: ...

@_types.runtime
class Representable(_pro):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__repr__`, which equals invoking `repr(self)`
    """
    def __repr__(self) -> str: ...

@_types.runtime
class Indexable(_pro):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__index__`. This allows to use self inside slice expressions, \\
    those are: `slice(self, ..., ...)` and `iterable[self: ... : ...]` (`self` can be \\
    placed anywhere)
    """
    def __index__(self) -> int: ...

@_types.runtime
class Positive(_pro[_T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__pos__`, which equals `+self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __pos__(self) -> _T_cov: ...

@_types.runtime
class Negative(_pro[_T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__neg__`, which equals `-self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __neg__(self) -> _T_cov: ...

@_types.runtime
class Invertible(_pro[_T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__invert__`, which equals `~self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __invert__(self) -> _T_cov: ...

BufferOperable = _types.Buffer
"\\@since 0.3.26rc1. *aveytense._abc.Buffer*"

@_types.runtime
class LeastComparable(_pro[_T_con]):
    """
    \\@since 0.3.26b3

    Can be compared with `<`
    """
    def __lt__(self, other: _T_con) -> bool: ...

@_types.runtime
class GreaterComparable(_pro[_T_con]):
    """
    \\@since 0.3.26b3

    Can be compared with `>`
    """
    def __gt__(self, other: _T_con) -> bool: ...

@_types.runtime
class LeastEqualComparable(_pro[_T_con]):
    """
    \\@since 0.3.26b3

    Can be compared with `<=`
    """
    def __le__(self, other: _T_con) -> bool: ...

@_types.runtime
class GreaterEqualComparable(_pro[_T_con]):
    """
    \\@since 0.3.26b3

    Can be compared with `>=`
    """
    def __ge__(self, other: _T_con) -> bool: ...

@_types.runtime
class EqualComparable(_pro[_T_con]):
    """
    \\@since 0.3.26rc1

    Can be compared with `==`
    """
    def __eq__(self, other: _T_con) -> bool: ...

@_types.runtime
class InequalComparable(_pro[_T_con]):
    """
    \\@since 0.3.26rc1

    Can be compared with `!=`
    """
    def __ne__(self, other: _T_con) -> bool: ...


class Comparable(
    LeastComparable[_types.Any],
    GreaterComparable[_types.Any],
    LeastEqualComparable[_types.Any],
    GreaterEqualComparable[_types.Any],
    EqualComparable[_types.Any],
    InequalComparable[_types.Any],
    InComparable[_types.Any]
):
    """
    \\@since 0.3.26b3

    An ABC supporting any form of comparison with operators \\
    `>`, `<`, `>=`, `<=`, `==`, `!=`, `in` (last 3 missing before 0.3.26rc1)
    """
    ...

class ComparableWithoutIn(
    LeastComparable[_types.Any],
    GreaterComparable[_types.Any],
    LeastEqualComparable[_types.Any],
    GreaterEqualComparable[_types.Any],
    EqualComparable[_types.Any]
):
    """
    \\@since 0.3.27a2

    An ABC same as `Comparable`, but without the `in` keyword support
    """
    ...

@_types.runtime
class BitwiseAndOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `_And__`, which equals `self & other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __and__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class BitwiseOrOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__or__`, which equals `self | other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __or__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class BitwiseXorOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__xor__`, which equals `self ^ other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __xor__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class BitwiseLeftOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__lshift__`, which equals `self << other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __lshift__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class BitwiseRightOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__rshift__`, which equals `self >> other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __lshift__(self, other: _T_con) -> _T_cov: ...

class BitwiseOperable(
    BitwiseAndOperable[_types.Any, _types.Any],
    BitwiseOrOperable[_types.Any, _types.Any],
    BitwiseXorOperable[_types.Any, _types.Any],
    BitwiseLeftOperable[_types.Any, _types.Any],
    BitwiseRightOperable[_types.Any, _types.Any]
):
    """
    \\@since 0.3.26rc1

    Can be used with `&`, `|`, `^`, `<<` and `>>` operators
    """
    ...

@_types.runtime
class BitwiseAndReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__iand__`, which equals `self &= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __iand__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class BitwiseOrReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__ior__`, which equals `self |= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ior__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class BitwiseXorReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__ixor__`, which equals `self ^= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ixor__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class BitwiseLeftReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__ilshift__`, which equals `self <<= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ilshift__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class BitwiseRightReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__irshift__`, which equals `self >>= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __irshift__(self, other: _T_con) -> _T_cov: ...

class BitwiseReassignable(
    BitwiseAndOperable[_types.Any, _types.Any],
    BitwiseOrOperable[_types.Any, _types.Any],
    BitwiseXorOperable[_types.Any, _types.Any],
    BitwiseLeftReassignable[_types.Any, _types.Any],
    BitwiseRightReassignable[_types.Any, _types.Any]):
    """
    \\@since 0.3.26rc1

    Can be used with `&=`, `|=`, `^=`, `<<=` and `>>=` operators
    """
    ...

class BitwiseCollection(
    BitwiseReassignable,
    BitwiseOperable
):
    """
    \\@since 0.3.26rc1

    Can be used with `&`, `|` and `^` operators, including their \\
    augmented forms: `&=`, `|=` and `^=`, with `~` use following::

        class Example(BitwiseCollection, Invertible[_T]): ...
    """
    ...

class UnaryOperable(Positive[_types.Any], Negative[_types.Any], Invertible[_types.Any]):
    """
    \\@since 0.3.26rc1

    Can be used with `+`, `-` and `~` operators preceding the type
    """
    ...

class Indexed(ItemGetter[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc2
    
    An ABC with one method `__getitem__`, which equals `self[key]`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `key` parameter.
    """
    ...
    
"""
@_pt.runtime
class AsyncIterable(_pro[_T_cov]):
    
    \\@since 0.3.26b3

    An ABC with magic method `__aiter__`. Returned type is addicted to covariant type parameter.
    
    def __aiter__(self) -> AsyncIterator[_T_cov]: ...
"""

@_types.runtime
class AsyncNextOperable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__anext__`. Returned type must be an awaitable \\
    of type represented by covariant type parameter.
    """
    async def __anext__(self) -> Awaitable[_T_cov]: ...

@_types.runtime
class AsyncExitOperable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__aexit__`. Returned type must be an awaitable \\
    of type represented by covariant type parameter.
    """
    async def __aexit__(self, exc_type: _opt[type[Exception]] = None, exc_value: _opt[Exception] = None, traceback: _opt[_types.TracebackType] = None) -> Awaitable[_T_cov]: ...

@_types.runtime
class AsyncEnterOperable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__aenter__`. Returned type must be an awaitable \\
    of type represented by covariant type parameter.
    """
    async def __aenter__(self) -> Awaitable[_T_cov]: ...

@_types.runtime
class ExitOperable(_pro):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__exit__`. Returned type is addicted to covariant type parameter.
    """
    def __exit__(self, exc_type: _opt[type[Exception]] = None, exc_value: _opt[Exception] = None, traceback: _opt[_types.TracebackType] = None) -> bool: ...

@_types.runtime
class EnterOperable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__enter__`. Returned type is addicted to covariant type parameter.
    """
    def __enter__(self) -> _T_cov: ...

@_types.runtime
class Ceilable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__ceil__`, which equals `ceil(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __ceil__(self) -> _T_cov: ...

@_types.runtime
class Floorable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__floor__`, which equals `floor(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __floor__(self) -> _T_cov: ...

@_types.runtime
class Roundable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__round__`, which equals `round(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __round__(self, ndigits: _types.Optional[int] = None) -> _T_cov: ...

@_types.runtime
class NextOperable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__next__`, which equals `next(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __next__(self) -> _T_cov: ...

CeilOperable = Ceilable
FloorOperable = Floorable
RoundOperable = Roundable

@_types.runtime
class AdditionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__add__`, which equals `self + other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __add__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class SubtractionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__sub__`, which equals `self - other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __sub__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class MultiplicationOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__mul__`, which equals `self * other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __mul__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class MatrixMultiplicationOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__matmul__`, which equals `self @ other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __matmul__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class TrueDivisionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__truediv__`, which equals `self / other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __truediv__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class FloorDivisionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__floordiv__`, which equals `self // other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __floordiv__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class DivmodOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__divmod__`, which equals `divmod(self, other)`. \\
    Returned type is addicted to covariant type parameter as the second type parameter \\
    first is type for `other` parameter.
    """
    def __divmod__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ModuloOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__mod__`, which equals `self % other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __mod__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ExponentiationOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__pow__`, which equals `self ** other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __pow__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ReflectedAdditionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__radd__`, which equals `other + self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __radd__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ReflectedSubtractionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__rsub__`, which equals `other - self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rsub__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ReflectedMultiplicationOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__rmul__`, which equals `other * self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rmul__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ReflectedMatrixMultiplicationOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__rmatmul__`, which equals `other @ self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rmatmul__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ReflectedTrueDivisionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__rtruediv__`, which equals `other / self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rtruediv__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ReflectedFloorDivisionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__rfloordiv__`, which equals `other // self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rfloordiv__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ReflectedDivmodOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__rdivmod__`, which equals `divmod(other, self)`. \\
    Returned type is addicted to covariant type parameter as the second type parameter; \\
    first is type for `other` parameter.
    """
    def __rdivmod__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ReflectedModuloOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__rmod__`, which equals `other % self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rmod__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ReflectedExponentiationOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__rpow__`, which equals `other ** self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rpow__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class AdditionReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__iadd__`, which equals `self += other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __iadd__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class SubtractionReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__isub__`, which equals `self -= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __isub__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class MultiplicationReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__imul__`, which equals `self *= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __imul__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class MatrixMultiplicationReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__imatmul__`, which equals `self @= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __imatmul__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class TrueDivisionReassingable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__itruediv__`, which equals `self /= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __itruediv__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class FloorDivisionReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__ifloordiv__`, which equals `self //= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ifloordiv__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ModuloReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__imod__`, which equals `self %= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __imod__(self, other: _T_con) -> _T_cov: ...

@_types.runtime
class ExponentiationReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26rc1
    
    An ABC with magic method `__ipow__`, which equals `self **= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ipow__(self, other: _T_con) -> _T_cov: ...

class ReflectedArithmeticOperable(
    ReflectedAdditionOperable[_types.Any, _types.Any],
    ReflectedSubtractionOperable[_types.Any, _types.Any],
    ReflectedMultiplicationOperable[_types.Any, _types.Any],
    ReflectedMatrixMultiplicationOperable[_types.Any, _types.Any],
    ReflectedTrueDivisionOperable[_types.Any, _types.Any],
    ReflectedFloorDivisionOperable[_types.Any, _types.Any],
    ReflectedDivmodOperable[_types.Any, _types.Any],
    ReflectedModuloOperable[_types.Any, _types.Any]
):
    """
    \\@since 0.3.26rc1

    An ABC supporting every kind (except bitwise) of reflected arithmetic operations with following operators:
    ```
        + - * @ / // % ** divmod
    ```
    where left operand is `other` and right is `self`
    """
    ...

class ArithmeticOperable(
    AdditionOperable[_types.Any, _types.Any],
    SubtractionOperable[_types.Any, _types.Any],
    MultiplicationOperable[_types.Any, _types.Any],
    MatrixMultiplicationOperable[_types.Any, _types.Any],
    TrueDivisionOperable[_types.Any, _types.Any],
    FloorDivisionOperable[_types.Any, _types.Any],
    DivmodOperable[_types.Any, _types.Any],
    ModuloOperable[_types.Any, _types.Any],
    ExponentiationOperable[_types.Any, _types.Any],
    ReflectedArithmeticOperable
):
    """
    \\@since 0.3.26rc1

    An ABC supporting every kind (except bitwise) of arithmetic operations, including their \\
    reflected equivalents, with following operators:
    ```
        + - * @ / // % ** divmod
    ```
    Both `self` and `other` can be either left or right operands.
    """
    ...

class ArithmeticReassignable(
    AdditionReassignable[_types.Any, _types.Any],
    SubtractionReassignable[_types.Any, _types.Any],
    MultiplicationReassignable[_types.Any, _types.Any],
    MatrixMultiplicationReassignable[_types.Any, _types.Any],
    TrueDivisionReassingable[_types.Any, _types.Any],
    FloorDivisionReassignable[_types.Any, _types.Any],
    ModuloReassignable[_types.Any, _types.Any],
    ExponentiationReassignable[_types.Any, _types.Any]
):
    """
    \\@since 0.3.26rc1

    An ABC supporting every kind (except bitwise) of augmented/re-assigned arithmetic operations \\
    with following operators:
    ```
        += -= *= @= /= //= %= **=
    ```
    """
    ...

class ArithmeticCollection(
    ArithmeticOperable,
    ArithmeticReassignable
):
    """
    \\@since 0.3.26rc1

    An ABC supporting every kind (except bitwise) of augmented/re-assigned and normal arithmetic operations \\
    with following operators:
    ```
        + - * @ / // % ** divmod += -= *= @= /= //= %= **=
    ```
    """
    ...

class OperatorCollection(
    ArithmeticCollection,
    BitwiseCollection,
    UnaryOperable,
    Comparable
):
    """
    \\@since 0.3.26rc1

    An ABC supporting every kind of augmented/re-assigned, reflected and normal arithmetic operations \\
    with following operators:
    ```
        + - * @ / // % ** divmod & | ^ += -= *= @= /= //= %= **= &= |= ^=
    ```
    unary assignment with `+`, `-` and `~`, and comparison with following operators:
    ```
        > < >= <= == != in
    ```
    """
    ...

if SizeableItemGetter is None:
    try:
        import _typeshed as shed
        class LenGetItemOperable(shed.SupportsLenAndGetItem[_T_cov]):
            """
            \\@since 0.3.26rc2
            
            An ABC with `__getitem__` and `__len__` methods. Those are typical in sequences.
            """
            ...
    except:
        class LenGetItemOperable(LenOperable, ItemGetter[int, _T_cov]):
            """
            \\@since 0.3.26rc2
            
            An ABC with `__getitem__` and `__len__` methods. Those are typical in sequences.
            """
            ...

@_types.runtime
class Formattable(_pro):
    """
    \\@since 0.3.26rc1

    An ABC with one method `__format__`, which equals invoking `format(self)`.
    """
    def __format__(self, format_spec: str = "") -> str: ...

@_types.runtime
class Flushable(_pro):
    """
    \\@since 0.3.27b1

    An ABC with one method `flush()`.
    """
    def flush(self) -> object: ...

@_types.runtime
class Writable(_pro[_T_con]):
    """
    \\@since 0.3.27b1

    An ABC with one method `write()`.
    """
    def write(self, s: _T_con, /) -> object: ...
    

@_types.runtime
class Copyable(_pro):
    """
    \\@since 0.3.34
    
    An ABC with one method `__copy__`.
    """
    if _sys.version_info >= (0, 3, 43):
        def __copy__(self) -> _types.Self: ...
    
    else:
        def copy(self) -> _types.Self: ... 

@_types.runtime
class DeepCopyable(_pro):
    """
    \\@since 0.3.43
    
    An ABC with one method `__deepcopy__`.
    """
    def __deepcopy__(self, memo: _types.Optional[dict[int, _types.Any]] = None) -> _types.Self: ...