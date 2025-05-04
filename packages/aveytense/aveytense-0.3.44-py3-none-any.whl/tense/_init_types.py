"""
**Tense Initial Types** \n
\\@since 0.3.26rc3 \\
© 2024-Present Aveyzan // License: MIT
```ts
module tense._init_types
```
Renamed from `_primal_types` on 0.3.35.
Renamed from `_types_first` on 0.3.37.

Components from `typing` and `typing_extensions` modules mainly. \\
If you see (≥ PY_VERSION) on documented strings, which feature solutions \\
from `typing` module, that is since when that solution is in `typing`. Excluded \\
mean that version since a solution is in `typing` module is nondescript.
"""

from __future__ import annotations
import sys as _sys
import subprocess as _subprocess

try:
    import typing_extensions as _typing_ext # pyright: ignore[reportUnusedImport]
    
except (ModuleNotFoundError, ImportError, NameError):
    _subprocess.run([_sys.executable, "-m", "pip", "install", "typing_extensions"])

import collections.abc as _collections_abc
import dis as _dis
import enum as _enum
import inspect as _inspect
import string as _string
import timeit as _timeit
import tkinter as _tkinter
import typing as _typing
import typing_extensions as _typing_ext
import unittest as _unittest
import zipfile as _zipfile

from array import (
    array as array, # 0.3.37
    ArrayType as ArrayType # 0.3.37
)

from collections import (
    ChainMap as ChainMap, # 0.3.37
    Counter as Counter, # 0.3.37
    defaultdict as defaultdict, # 0.3.37 
    deque as deque, # 0.3.37
)

from dataclasses import (
    dataclass as dataclass # 0.3.37
)

from enum import (
    auto as auto, # 0.3.26
    EnumMeta as EnumMeta, # 0.3.26rc1
    EnumType as EnumType # 0.3.26rc1
)

from functools import (
    cached_property as cachedproperty, # 0.3.37
    partial as partial, # 0.3.26
    partialmethod as partialmethod, # 0.3.37
    singledispatchmethod as singledispatchmethod, # 0.3.37
    lru_cache as lru_cache, # 0.3.37
    singledispatch as singledispatch, # 0.3.37
)

from inspect import (
    ArgInfo as ArgInfo, # 0.3.26rc3
    Arguments as Arguments, # 0.3.26rc3
    Attribute as Attribute, # 0.3.26rc3
    BlockFinder as BlockFinder, # 0.3.26rc3
    BoundArguments as BoundArguments, # 0.3.26rc3
    ClosureVars as ClosureVars, # 0.3.26rc3
    FrameInfo as FrameInfo, # 0.3.26rc3
    FullArgSpec as FullArgSpec, # 0.3.26rc3
    Parameter as Parameter, # 0.3.26rc3
    Signature as Signature, # 0.3.26rc3
    Traceback as Traceback, # 0.3.26rc3
    get_annotations as get_annotations, # 0.3.37
)

from re import (
    Match as Match, # 0.3.26
    Pattern as Pattern # 0.3.26
)

from types import (
    CodeType as CodeType, # 0.3.26rc3
    FrameType as FrameType, # 0.3.37
    FunctionType as FunctionType, # 0.3.37
    MethodType as MethodType, # 0.3.37
    ModuleType as ModuleType, # 0.3.26rc3
    TracebackType as TracebackType, # 0.3.26rc3
    coroutine as coroutine, # 0.3.26rc1/0.3.34?
    new_class as new_class # 0.3.26rc1/0.3.34?
)

from typing import (
    get_type_hints as get_type_hints, # 0.3.37
    no_type_check as no_type_check, # 0.3.37?
)

from unittest import (
    TestCase as TestCase, # 0.3.26rc3
    TestLoader as TestLoader, # 0.3.26rc3
)

from uuid import UUID as UUID # 0.3.26rc3


### ENUMS & FLAGS ###
class IntegerFlag(_enum.IntFlag):
    "\\@since 0.3.26rc1. Support for integer-based flags. See [`enum.IntFlag`](https://docs.python.org/3/library/enum.html#enum.IntFlag)"
    ...

class IntegerEnum(_enum.IntEnum):
    "\\@since 0.3.26rc1. Enum where members are also (and must be) integers. See [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)"
    ...

class Enum(_enum.Enum):
    "\\@since 0.3.26rc1. Create a collection of name/value pairs. See [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)"
    ...

class StringEnum(_enum.StrEnum):
    "\\@since 0.3.26rc1. Enum where members are also (and must be) strings. See [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)"
    ...

class Flag(_enum.Flag):
    "\\@since 0.3.26rc1. Support for flags. See [`enum.Flag`](https://docs.python.org/3/library/enum.html#enum.Flag)"
    ...

###### UTILITY TYPES ######

# using hasattr() instead of sys.version_info due to unknown version which provides
# all of these below
if hasattr(_typing, "Union"):
    from typing import Union as Union # 0.3.26rc1
    
else:
    from typing_extensions import Union as Union # 0.3.26rc1

if hasattr(_typing, "Optional"):
    from typing import Optional as Optional # 0.3.26b3
    
else:
    from typing_extensions import Optional as Optional # 0.3.26b3

if hasattr(_typing, "Callable"):
    from typing import Callable as Callable # 0.3.26b3
    
elif hasattr(_collections_abc, "Callable"):
    from collections.abc import Callable as Callable # 0.3.26b3
    
else:
    from typing_extensions import Callable as Callable # 0.3.26b3

if hasattr(_typing, "Generic"):
    from typing import Generic as Generic # 0.3.26b3
    
else:
    from typing_extensions import Generic as Generic # 0.3.26b3

Callback = Callable
"""
\\@since 0.3.26rc3

Reference from JavaScript
https://docs.python.org/3/library/typing.html#typing.Callable
"""

###### VERSION ASCENDING ######

if _sys.version_info >= (3, 5, 2):
    from typing import (
        NamedTuple as NamedTuple, # 0.3.26rc1
        NewType as NewType, # 0.3.26rc1
        TYPE_CHECKING as TYPE_CHECKING # 0.3.37
    )
else:
    from typing_extensions import (
        NamedTuple as NamedTuple, # 0.3.26rc1
        NewType as NewType, # 0.3.26rc1
        TYPE_CHECKING as TYPE_CHECKING # 0.3.37
    )


if _sys.version_info >= (3, 5, 3):
    from typing import ClassVar as ClassVar # 0.3.26b3
else:
    from typing_extensions import ClassVar as ClassVar # 0.3.26b3


if _sys.version_info >= (3, 6, 2):
    from typing import NoReturn as NoReturn # 0.3.26b3
else:
    from typing_extensions import NoReturn as NoReturn # 0.3.26b3

if _sys.version_info >= (3, 7):
    from uuid import SafeUUID as SafeUUID
    
else:
    class SafeUUID(_enum.Enum):
        safe = 0
        unsafe = -1
        unknown = None


if _sys.version_info >= (3, 7, 4):
    from typing import ForwardRef as ForwardRef # 0.3.26rc3
else:
    from typing_extensions import ForwardRef as ForwardRef # 0.3.26rc3


if _sys.version_info >= (3, 8):
    
    from typing import (
        Final as Final, # 0.3.26rc1
        Literal as Literal, # 0.3.26rc1
        Protocol as Protocol, # 0.3.26rc1
        TypedDict as TypedDict, # 0.3.37
        final as final, # 0.3.37
        get_args as get_args, # 0.3.26rc1 (renamed 0.3.34 from `getArgs`)
        get_origin as get_origin, # 0.3.37
        runtime_checkable as runtime, # 0.3.26rc1
    )
    
    from types import CellType as CellType # 0.3.37
    
else:
    from typing_extensions import (
        Final as Final, # 0.3.26rc1
        Literal as Literal, # 0.3.26rc1
        Protocol as Protocol, # 0.3.26rc1
        TypedDict as TypedDict, # 0.3.37
        final as final, # 0.3.37
        get_args as get_args, # 0.3.26rc1 (renamed 0.3.34 from `getArgs`)
        get_origin as get_origin, # 0.3.37
        runtime_checkable as runtime, # 0.3.26rc1
    )


if _sys.version_info >= (3, 9):
    
    from typing import (
        IO as IO,
        Annotated as Annotated, # 0.3.26rc1
        BinaryIO as BinaryIO, # 0.3.26rc3
        TextIO as TextIO # 0.3.26rc3
    )
    
    from types import GenericAlias as GenericAlias # 0.3.37
    
else:
    from typing_extensions import (
        IO as IO,
        Annotated as _Annotated, # 0.3.26rc1
        BinaryIO as _BinaryIO, # 0.3.26rc3
        TextIO as _TextIO # 0.3.26rc3
    )


if _sys.version_info >= (3, 10):
    
    from typing import (
        ParamSpec as ParamSpec, # 0.3.26rc1
        ParamSpecArgs as ParamSpecArgs, # 0.3.26rc1
        ParamSpecKwargs as ParamSpecKwargs, # 0.3.26rc1
        TypeGuard as TypeGuard, # 0.3.26rc1
        TypeAlias as TypeAlias, # 0.3.26rc1
        Concatenate as Concatenate, # 0.3.26rc1
        is_typeddict as is_typeddict, # 0.3.37
    )
    
    from types import (
        UnionType as UnionType, # 0.3.37
        EllipsisType as EllipsisType,
        NotImplementedType as NotImplementedType # 0.3.37
    )
    
    Ellipsis = ...

else:
    
    from typing_extensions import (
        ParamSpec as ParamSpec, # 0.3.26rc1
        ParamSpecArgs as ParamSpecArgs, # 0.3.26rc1
        ParamSpecKwargs as ParamSpecKwargs, # 0.3.26rc1
        TypeGuard as TypeGuard, # 0.3.26rc1
        TypeAlias as TypeAlias, # 0.3.26rc1
        Concatenate as Concatenate, # 0.3.26rc1
        is_typeddict as is_typeddict, # 0.3.37
    )
    
    @final
    @_typing.type_check_only
    class ellipsis: ...
    Ellipsis = ellipsis()

if _sys.version_info >= (3, 11):
    
    from enum import (
        verify as verify, # 0.3.26rc1
        EnumCheck as EnumCheck, # 0.3.26rc1
        ReprEnum as ReprEnum, # 0.3.26rc1
        FlagBoundary as FlagBoundary # 0.3.26rc1
    )
    
    from typing import (
        TypeVarTuple as TypeVarTuple, # 0.3.26rc3
        Unpack as Unpack, # 0.3.26rc1
        Never as Never, # 0.3.26rc1
        LiteralString as LiteralString, # 0.3.26rc1
        Self as Self, # 0.3.26rc1
        Any as Any, # 0.3.26rc1
        NotRequired as NotRequired, # 0.3.26rc1
        Required as Required, # 0.3.26rc1
        assert_never as assert_never, # 0.3.37
        assert_type as assert_type, # 0.3.37
        clear_overloads as clear_overloads, # 0.3.37
        dataclass_transform as dataclass_transform, # 0.3.37
        get_overloads as get_overloads, # 0.3.37
        overload as overload, # 0.3.26rc1
        reveal_type as reveal_type # 0.3.37
    )
    
else:
    
    from typing_extensions import (
        TypeVarTuple as TypeVarTuple, # 0.3.26rc3
        Unpack as Unpack, # 0.3.26rc1
        Never as Never, # 0.3.26rc1
        LiteralString as LiteralString, # 0.3.26rc1
        Self as Self, # 0.3.26rc1
        Any as Any, # 0.3.26rc1
        NotRequired as NotRequired, # 0.3.26rc1
        Required as Required, # 0.3.26rc1
        assert_never as assert_never, # 0.3.37
        assert_type as assert_type, # 0.3.37
        clear_overloads as clear_overloads, # 0.3.37
        dataclass_transform as dataclass_transform, # 0.3.37
        get_overloads as get_overloads, # 0.3.37
        overload as overload, # 0.3.26rc1
        reveal_type as reveal_type # 0.3.37
    )


if _sys.version_info >= (3, 12):
    
    from typing import (
        TypeAliasType as TypeAliasType, # 0.3.26rc1
        override as override # 0.3.37
    ) 
    
    from collections.abc import Buffer as Buffer # 0.3.37
    from inspect import BufferFlags as BufferFlags # 0.3.26rc2
    
else:
    from typing_extensions import (
        TypeAliasType as TypeAliasType, # 0.3.26rc1
        override as override # 0.3.37
    ) 
    
    Buffer = Union[bytes, bytearray, array, memoryview]
    
    class BufferFlags(_enum.IntFlag): # 0.3.26rc2
        SIMPLE = 0x0
        WRITABLE = 0x1
        FORMAT = 0x4
        ND = 0x8
        STRIDES = 0x10 | ND
        C_CONTIGUOUS = 0x20 | STRIDES
        F_CONTIGUOUS = 0x40 | STRIDES
        ANY_CONTIGUOUS = 0x80 | STRIDES
        INDIRECT = 0x100 | STRIDES
        CONTIG = ND | WRITABLE
        CONTIG_RO = ND
        STRIDED = STRIDES | WRITABLE
        STRIDED_RO = STRIDES
        RECORDS = STRIDES | WRITABLE | FORMAT
        RECORDS_RO = STRIDES | FORMAT
        FULL = INDIRECT | WRITABLE | FORMAT
        FULL_RO = INDIRECT | FORMAT
        READ = 0x100
        WRITE = 0x200


if _sys.version_info >= (3, 13):
    
    from warnings import deprecated as deprecated # 0.3.37
    
    # about TypeVar: 'default' parameter inspection (available since 3.13)
    # see PEP 696 for details. status: accepted
    
    from typing import (
        TypeIs as TypeIs, # 0.3.26rc1
        TypeVar as TypeVar, # 0.3.26b3
        NoDefault as NoDefault, # 0.3.26rc1
        ReadOnly as ReadOnly, # 0.3.26rc1
        get_protocol_members as get_protocol_members, # 0.3.37
        is_protocol as is_protocol, # 0.3.37
    )
    
else:
    from typing_extensions import (
        deprecated as deprecated, # 0.3.37
        TypeIs as TypeIs, # 0.3.26rc1
        TypeVar as TypeVar, # 0.3.26b3
        NoDefault as NoDefault, # 0.3.26rc1
        ReadOnly as ReadOnly, # 0.3.26rc1
        get_protocol_members as get_protocol_members, # 0.3.37
        is_protocol as is_protocol, # 0.3.37
    )
    
# pending removals    
if _sys.version_info < (3, 14):
    
    from collections.abc import ByteString as ByteString # 0.3.37
    
else:
    
    ByteString = Union[bytes, bytearray, memoryview] # 0.3.37
    
if _sys.version_info < (3, 15):
    
    from typing import no_type_check_decorator as no_type_check_decorator
    noTypeCheckDecorator = no_type_check_decorator # 0.3.26rc1    
    
if _sys.version_info < (3, 18):
    
    from typing import AnyStr as AnyStr
    
else:
    
    AnyStr = TypeVar("AnyStr", bytes, str)
    


if _sys.version_info < (0, 3, 37):
    
    @deprecated("Deprecated since 0.3.31, will be removed on 0.3.36. Deviating from Tkinter technology.")
    class IntegerVar(_tkinter.IntVar):
        "\\@since 0.3.26rc1. Value holder for integer variables. See `tkinter.IntVar` (doc not available)"
        ...

    @deprecated("Deprecated since 0.3.31, will be removed on 0.3.36. Deviating from Tkinter technology.")
    class StringVar(_tkinter.StringVar):
        "\\@since 0.3.26rc1. Value holder for string variables. See `tkinter.StringVar` (doc not available)"
        ...

    @deprecated("Deprecated since 0.3.31, will be removed on 0.3.36. Deviating from Tkinter technology.")
    class BooleanVar(_tkinter.BooleanVar):
        "\\@since 0.3.26rc1. Value holder for boolean variables. See `tkinter.BooleanVar` (doc not available)"
        ...

    @deprecated("Deprecated since 0.3.31, will be removed on 0.3.36. Deviating from Tkinter technology.")
    class Variable(_tkinter.Variable):
        "\\@since 0.3.26rc1. See `tkinter.Variable` (doc not available)"
        ...

    @deprecated("Deprecated since 0.3.31, will be removed on 0.3.36. Deviating from Tkinter technology.")
    class FloatVar(_tkinter.DoubleVar):
        "\\@since 0.3.26rc1. Value holder for float variables. See `tkinter.DoubleVar` (doc not available)"
        ...

class ZipFile(_zipfile.ZipFile):
    "\\@since 0.3.26rc2. Class with methods to open, read, write, close, list zip files. See [`zipfile.ZipFile`](https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile)"
    ...

class ZipExtFile(_zipfile.ZipExtFile):
    "\\@since 0.3.26rc2. File-like object for reading an archive member. Returned by `ZipFile.open()`. See [`zipfile.ZipExtFile`](https://docs.python.org/3/library/zipfile.html#zipfile.ZipExtFile)"
    ...

class ZipPath(_zipfile.Path):
    "\\@since 0.3.26rc2. A pathlib-compatible interface for zip files. See [`zipfile.Path`](https://docs.python.org/3/library/zipfile.html#zipfile.Path)"
    ...

_T = TypeVar("_T")
_P = ParamSpec("_P")

# worth noticing: these don't need type annotation with Literal
_true = True
_false = False

cached_property = cachedproperty
runtime_checkable = runtime

Pack = Concatenate
SpecVar = ParamSpec
SpecVarArgs = ParamSpecArgs
SpecVarKwargs = ParamSpecKwargs
TypeTupleVar = TypeVarTuple

noTypeCheck = no_type_check # 0.3.26rc1
newClass = new_class # 0.3.26rc3

StringUnion = Union[_T, str]
"\\@since 0.3.26rc3"
IntegerUnion = Union[_T, int]
"\\@since 0.3.26rc3"
FloatUnion = Union[_T, float]
"\\@since 0.3.26rc3"
ComplexUnion = Union[_T, complex]
"\\@since 0.3.26rc3"
IntegerFloatUnion = Union[_T, int, float]
"\\@since 0.3.26rc3"
IntegerStringUnion = Union[_T, int, str]
"\\@since 0.3.26rc3"
BooleanUnion = Union[_T, bool]
"\\@since 0.3.26rc3"
TrueUnion = Union[_T, _true]
"\\@since 0.3.26rc3"
FalseUnion = Union[_T, _false]
"\\@since 0.3.26rc3"
OptionalCallable = Optional[Callable[_P, _T]]
"\\@since 0.3.26rc3. `typing.Optional[typing.Callable[**P, T]]` = `((**P) -> T) | None`"
AnyCallable = Callable[..., Any]
"\\@since 0.3.26rc3. `typing.Callable[..., typing.Any]` = `(...) -> Any`"
OptionalUnion = Optional[Union[_T]]
"\\@since 0.3.26rc3. `typing.Optional[typing.Union[T]]`"

ByteCode = _dis.Bytecode
"\\@since 0.3.26rc3. See [`dis.Bytecode`](https://docs.python.org/3/library/dis.html#dis.Bytecode)"

if _sys.version_info < (0, 3, 37):
    EOBError = _inspect.EndOfBlock
    "\\@since 0.3.26rc3. See `inspect.EndOfBlock` (no doc available)"

Instruction = _dis.Instruction
"\\@since 0.3.26rc3. See [`dis.Instruction`](https://docs.python.org/3/library/dis.html#dis.Instruction)"

class CompletedProcess(_subprocess.CompletedProcess):
    """
    \\@since 0.3.26rc3. See [`subprocess.CompletedProcess`](https://docs.python.org/3/library/subprocess.html#subprocess.CompletedProcess)

    Returned by `subprocess.run()` function
    """
    ...

class Positions(_dis.Positions):
    "\\@since 0.3.26rc3. See [`dis.Positions`](https://docs.python.org/3/library/dis.html#dis.Positions)"
    ...

class StringFormatter(_string.Formatter):
    "\\@since 0.3.26rc3. See [`string.Formatter`](https://docs.python.org/3/library/string.html#string.Formatter)"
    ...

class StringTemplate(_string.Template):
    "\\@since 0.3.26rc3. See [`string.Template`](https://docs.python.org/3/library/string.html#string.Template)"
    ...

class TestCase(_unittest.TestCase):
    "\\@since 0.3.26rc3. See [`unittest.TestCase`](https://docs.python.org/3/library/unittest.html#unittest.TestCase)"
    ...

class TestLoader(_unittest.TestLoader):
    "\\@since 0.3.26rc3. See [`unittest.TestLoader`](https://docs.python.org/3/library/unittest.html#unittest.TestLoader)"
    ...

class Timer(_timeit.Timer):
    "\\@since 0.3.26rc3. See [`timeit.Timer`](https://docs.python.org/3/library/timeit.html#timeit.Timer)"
    ...

__all__ = [k for k in globals() if k[:1] != "_"]