"""
**Tense Primal Types** \n
\\@since 0.3.26rc3 \\
© 2024-Present Aveyzan // License: MIT
```
module tense._primal_types
```
Components from `typing` and `typing_extensions` modules mainly. \\
If you see (≥ PY_VERSION) on documented strings, which feature solutions \\
from `typing` module, that is since when that solution is in `typing`. Excluded \\
mean that version since a solution is in `typing` module is nondescript.
"""

from __future__ import annotations
import sys as _sys
import subprocess as _subprocess

try:
    import typing_extensions as _typing_ext
    
except (ModuleNotFoundError, ImportError, NameError):
    _subprocess.run([_sys.executable, "-m", "pip", "install", "typing_extensions"])

import abc as _abc
import collections.abc as _collections_abc
import dis as _dis
import enum as _enum
import functools as _functools
import inspect as _inspect
import re as _re
import string as _string
import timeit as _timeit
import tkinter as _tkinter
import types as _types
import typing as _typing
import typing_extensions as _typing_ext
import unittest as _unittest
import uuid as _uuid
import warnings as _warnings
import zipfile as _zipfile

###### UTILITY TYPES ######

# 'default' parameter inspection (available since 3.13)
# see PEP 696 for details. status: accepted (and used in memoryview class, default type 'int')
if _sys.version_info < (3, 13):
    _TypeVar = _typing_ext.TypeVar
else:
    _TypeVar = _typing.TypeVar

# using hasattr() instead of sys.version_info due to unknown version which provides
# all of these below
if hasattr(_typing, "Union"):
    _Union = _typing.Union
else:
    _Union = _typing_ext.Union

if hasattr(_typing, "Optional"):
    _Optional = _typing.Optional
else:
    _Optional = _typing_ext.Optional

if hasattr(_typing, "Callable"):
    _Callable = _typing.Callable
else:
    _Callable = _typing_ext.Callable

if hasattr(_typing, "Generic"):
    _Generic = _typing.Generic
else:
    _Generic = _typing_ext.Generic

TypeVar = _TypeVar
"\\@since 0.3.26b3. [`typing.TypeVar`](https://docs.python.org/3/library/typing.html#typing.TypeVar)"
Union = _Union
"\\@since 0.3.26rc1. [`typing.Union`](https://docs.python.org/3/library/typing.html#typing.Union)"
Optional = _Optional
"\\@since 0.3.26b3. [`typing.Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)"
Callable = _Callable
"\\@since 0.3.26b3. [`typing.Callable`](https://docs.python.org/3/library/typing.html#typing.Callable)"
Generic = _Generic
"\\@since 0.3.26b3. [`typing.Generic`](https://docs.python.org/3/library/typing.html#typing.Generic)"
Callback = Callable
"\\@since 0.3.26rc3. [`typing.Callable`](https://docs.python.org/3/library/typing.html#typing.Callable)"

_T = TypeVar("_T")
_T_sb = TypeVar("_T_sb", str, bytes)
_T_class = TypeVar("_T_class", bound = type)
_T_cov = TypeVar("_T_cov", covariant = True)
# _T_con = TypeVar("_T_con", contravariant = True)
# _KT = TypeVar("_KT")
# _KT_cov = TypeVar("_KT_cov", covariant = True)
# _KT_con = TypeVar("_KT_con", contravariant = True)
# _VT = TypeVar("_VT")
# _VT_cov = TypeVar("_VT_cov", covariant = True)

###### VERSION ASCENDING ######

# since Python 3.5.2
if _sys.version_info >= (3, 5, 2):
    _NamedTuple = _typing.NamedTuple
    _NewType = _typing.NewType
else:
    _NamedTuple = _typing_ext.NamedTuple
    _NewType = _typing_ext.NewType

# since Python 3.5.3
if _sys.version_info >= (3, 5, 3):
    # questionable: does this type have to be wrapped into string?
    _ClassVar = _typing.ClassVar[_T]
else:
    _ClassVar = _typing_ext.ClassVar[_T]

# since Python 3.6.2
if _sys.version_info >= (3, 6, 2):
    _NoReturn = _typing.NoReturn
else:
    _NoReturn = _typing_ext.NoReturn

# since Python 3.7.4
if _sys.version_info >= (3, 7, 4):
    _ForwardRef = _typing.ForwardRef
else:
    _ForwardRef = _typing_ext.ForwardRef

# since Python 3.8
if _sys.version_info >= (3, 8):
    from typing import get_args as get_args # 0.3.26rc1 (renamed 0.3.34 from `getArgs`)
    _Literal = _typing.Literal
    _Final = _typing.Final
    _Protocol = _typing.Protocol
    
else:
    from typing_extensions import get_args as get_args # 0.3.26rc1 (renamed 0.3.34 from `getArgs`)
    _Literal = _typing_ext.Literal
    _Final = _typing_ext.Final
    _Protocol = _typing_ext.Protocol
    

# since Python 3.5.2
NamedTuple = _NamedTuple
"\\@since 0.3.26rc1. [`typing.NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple) (≥ 3.5.2)"
NewType = _NewType
"\\@since 0.3.26rc1. [`typing.NewType`](https://docs.python.org/3/library/typing.html#typing.NewType) (≥ 3.5.2)"

# since Python 3.5.3
ClassVar = _ClassVar[_T]
"\\@since 0.3.26b3. [`typing.ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar) (≥ 3.5.3)"

# since Python 3.6.2 (older doc, of version 3.6, says 3.6.5)
NoReturn = _NoReturn
"\\@since 0.3.26b3. [`typing.NoReturn`](https://docs.python.org/3/library/typing.html#typing.NoReturn) (≥ 3.6.2)"

# since Python 3.7.4
ForwardRef = _ForwardRef
"\\@since 0.3.26rc3. [`typing.ForwardRef`](https://docs.python.org/3/library/typing.html#typing.ForwardRef) (≥ 3.7.4)"

# since Python 3.8
Literal = _Literal
"\\@since 0.3.26rc1. [`typing.Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) (≥ 3.8)"
Final = _Final
"\\@since 0.3.26rc1. [`typing.Final`](https://docs.python.org/3/library/typing.html#typing.Final) (≥ 3.8)"
Protocol = _Protocol
"\\@since 0.3.26rc1. [`typing.Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol) (≥ 3.8)"

# since Python 3.9
if _sys.version_info >= (3, 9):
    from typing import IO as IO
    _Annotated = _typing.Annotated
    _BinaryIO = _typing.BinaryIO
    _TextIO = _typing.TextIO
else:
    from typing_extensions import IO as IO
    _Annotated = _typing_ext.Annotated
    _BinaryIO = _typing_ext.BinaryIO
    _TextIO = _typing_ext.TextIO

Annotated = _Annotated
"\\@since 0.3.26rc1. [`typing.Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated) (≥ 3.9)"
BinaryIO = _BinaryIO
"\\@since 0.3.26rc3. [`typing.BinaryIO`](https://docs.python.org/3/library/typing.html#abcs-for-working-with-io) (≥ 3.9)"
TextIO = _TextIO
"\\@since 0.3.26rc3. [`typing.TextIO`](https://docs.python.org/3/library/typing.html#abcs-for-working-with-io) (≥ 3.9)"

# since Python 3.10
if _sys.version_info >= (3, 10):
    _SpecVar = _typing.ParamSpec
    _SpecVarArgs = _typing.ParamSpecArgs
    _SpecVarKwargs = _typing.ParamSpecKwargs
    _TypeGuard = _typing.TypeGuard[_T]
    _TypeAlias = _typing.TypeAlias # not recommended to use it (deprecated feature)
    _Concatenate = _typing.Concatenate
    ellipsis = _types.EllipsisType
    _Ellipsis = _types.EllipsisType
else:
    _SpecVar = _typing_ext.ParamSpec
    _SpecVarArgs = _typing_ext.ParamSpecArgs
    _SpecVarKwargs = _typing_ext.ParamSpecKwargs
    _TypeGuard = _typing_ext.TypeGuard[_T]
    _TypeAlias = _typing_ext.TypeAlias
    _Concatenate = _typing_ext.Concatenate
    @tp.final
    class ellipsis: ...
    _Ellipsis = ellipsis()

SpecVar = _SpecVar
"\\@since 0.3.26rc1. [`typing.ParamSpec`](https://docs.python.org/3/library/typing.html#typing.ParamSpec) (≥ 3.10)"
SpecVarArgs = _SpecVarArgs
"\\@since 0.3.26rc1. [`typing.ParamSpecArgs`](https://docs.python.org/3/library/typing.html#typing.ParamSpecArgs) (≥ 3.10)"
SpecVarKwargs = _SpecVarKwargs
"\\@since 0.3.26rc1. [`typing.ParamSpecKwargs`](https://docs.python.org/3/library/typing.html#typing.ParamSpecKwargs) (≥ 3.10)"
TypeAlias = _TypeAlias
"\\@since 0.3.26rc1. [`typing.TypeAlias`](https://docs.python.org/3/library/typing.html#typing.TypeAlias) (≥ 3.10)"
TypeGuard = _TypeGuard[_T]
"\\@since 0.3.26rc1. [`typing.TypeGuard`](https://docs.python.org/3/library/typing.html#typing.TypeGuard) (≥ 3.10)"
Concatenate = _Concatenate
"\\@since 0.3.26rc1. [`typing.Concatenate`](https://docs.python.org/3/library/typing.html#typing.Concatenate) (≥ 3.10)"
Pack = _Concatenate
"\\@since 0.3.26rc1. [`typing.Concatenate`](https://docs.python.org/3/library/typing.html#typing.Concatenate) (≥ 3.10)"
Ellipsis = _Ellipsis
"\\@since 0.3.26rc1. [`Ellipsis`](https://docs.python.org/dev/library/constants.html#Ellipsis)"
ParamSpec = SpecVar
"\\@since 0.3.26rc3. [`typing.ParamSpec`](https://docs.python.org/3/library/typing.html#typing.ParamSpec) (≥ 3.10)"
ParamSpecArgs = SpecVarArgs
"\\@since 0.3.26rc3. [`typing.ParamSpecArgs`](https://docs.python.org/3/library/typing.html#typing.ParamSpecArgs) (≥ 3.10)"
ParamSpecKwargs = SpecVarKwargs
"\\@since 0.3.26rc3. [`typing.ParamSpecKwargs`](https://docs.python.org/3/library/typing.html#typing.ParamSpecKwargs) (≥ 3.10)"

# since Python 3.11
if _sys.version_info >= (3, 11):
    _TypeTupleVar = _typing.TypeVarTuple
    _NotRequired = _typing.NotRequired
    _Required = _typing.Required
    _Unpack = _typing.Unpack
    _Never = _typing.Never
    _Any = _typing.Any
    _LiteralString = _typing.LiteralString
    _Self = _typing.Self
    
else:
    _TypeTupleVar = _typing_ext.TypeVarTuple
    _NotRequired = _typing_ext.NotRequired
    _Required = _typing_ext.Required
    _Unpack = _typing_ext.Unpack
    _Never = _typing_ext.Never
    _Any = _typing_ext.Any
    _LiteralString = _typing_ext.LiteralString
    _Self = _typing_ext.Self

Any = _Any
"\\@since 0.3.26rc1. [`typing.Any`](https://docs.python.org/3/library/typing.html#typing.Any)"
TypeTupleVar = _TypeTupleVar
"\\@since 0.3.26rc1. [`typing.TypeVarTuple`](https://docs.python.org/3/library/typing.html#typing.TypeVarTuple) (≥ 3.11)"
NotRequired = _NotRequired
"\\@since 0.3.26rc1. [`typing.NotRequired`](https://docs.python.org/3/library/typing.html#typing.NotRequired) (≥ 3.11)"
Required = _Required
"\\@since 0.3.26rc1. [`typing.Required`](https://docs.python.org/3/library/typing.html#typing.Required) (≥ 3.11)"
Unpack = _Unpack
"\\@since 0.3.26rc1. [`typing.Unpack`](https://docs.python.org/3/library/typing.html#typing.Unpack) (≥ 3.11)"
Never = _Never
"\\@since 0.3.26rc1. [`typing.Never`](https://docs.python.org/3/library/typing.html#typing.Never) (≥ 3.11)"
LiteralString = _LiteralString
"\\@since 0.3.26rc1. [`typing.LiteralString`](https://docs.python.org/3/library/typing.html#typing.LiteralString) (≥ 3.11)"
Self = _Self
"\\@since 0.3.26rc1. [`typing.Self`](https://docs.python.org/3/library/typing.html#typing.Self) (≥ 3.11)"
TypeVarTuple = TypeTupleVar
"\\@since 0.3.26rc3. [`typing.TypeVarTuple`](https://docs.python.org/3/library/typing.html#typing.TypeVarTuple) (≥ 3.11)"

# since Python 3.12
if _sys.version_info >= (3, 12):
    _TypeAliasType = _typing.TypeAliasType
else:
    _TypeAliasType = _typing_ext.TypeAliasType

TypeAliasType = _TypeAliasType
"\\@since 0.3.26rc1. [`typing.TypeAliasType`](https://docs.python.org/3/library/typing.html#typing.TypeAliasType) (≥ 3.12)"

# since Python 3.13
if _sys.version_info >= (3, 13):
    _NoDefault = _typing.NoDefault
    _TypeIs = _typing.TypeIs[_T]
    _ReadOnly = _typing.ReadOnly[_T]
else:
    _NoDefault = _typing_ext.NoDefault
    _TypeIs = _typing_ext.TypeIs[_T]
    _ReadOnly = _typing_ext.ReadOnly[_T] # type: ignore

NoDefault = _NoDefault
"\\@since 0.3.26rc1. [`typing.NoDefault`](https://docs.python.org/3/library/typing.html#typing.NoDefault) (≥ 3.13)"
TypeIs = _TypeIs[_T]
"\\@since 0.3.26rc1. [`typing.TypeIs`](https://docs.python.org/3/library/typing.html#typing.TypeIs) (≥ 3.13)"
ReadOnly = _ReadOnly[_T]
"\\@since 0.3.26rc1. [`typing.ReadOnly`](https://docs.python.org/3/library/typing.html#typing.ReadOnly) (≥ 3.13)"

_T_func = TypeVar("_T_func", bound = Callable[..., Any])
_P = SpecVar("_P")
_CoroutineLike = Callable[_P, _collections_abc.Generator[Any, Any, _T]]
_DecoratorLike = Callable[_P, _T]

def runtime(c: _T_class):
    """
    \\@since 0.3.26rc1. See [`typing.runtime_checkable`](https://docs.python.org/3/library/typing.html#typing.runtime_checkable)

    A decorator which formalizes protocol class to a protocol runtime. \\
    Protocol class injected with this decorator can be used in `isinstance()` \\
    and `issubclass()` type checking functions.
    """
    if _sys.version_info >= (3, 8):
        return _typing.runtime_checkable(c)
    
    else:
        return _typing_ext.runtime_checkable(c)
    
class Auto(_enum.auto):
    "\\@since 0.3.26rc1. See [`enum.auto`](https://docs.python.org/3/library/enum.html#enum.auto)"
    ...

auto = _enum.auto
"\\@since 0.3.26. See [`enum.auto`](https://docs.python.org/3/library/enum.html#enum.auto)"

if _sys.version_info >= (3, 11):
    class verify(_enum.verify):
        "\\@since 0.3.26rc2. See [`enum.verify`](https://docs.python.org/3/library/enum.html#enum.verify)"
        ...
    EnumCheck = _enum.EnumCheck
    "\\@since 0.3.26rc1. Various conditions to check an enumeration for. [`enum.EnumCheck`](https://docs.python.org/3/library/enum.html#enum.EnumCheck)"
    ReprEnum = _enum.ReprEnum
    "\\@since 0.3.26rc1"
    FlagBoundary = _enum.FlagBoundary
    "\\@since 0.3.26rc1"

class IntegerFlag(_enum.IntFlag):
    "\\@since 0.3.26rc1. Support for integer-based flags. See [`enum.IntFlag`](https://docs.python.org/3/library/enum.html#enum.IntFlag)"
    ...

class IntegerEnum(_enum.IntEnum):
    "\\@since 0.3.26rc1. Enum where members are also (and must be) integers. See [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)"
    ...

class Enum(_enum.Enum):
    "\\@since 0.3.26rc1. Create a collection of name/value pairs. See [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)"
    ...

EnumType = _enum.EnumType
"\\@since 0.3.26rc2. See [`enum.EnumType`](https://docs.python.org/3/library/enum.html#enum.EnumType)"

class StringEnum(_enum.StrEnum):
    "\\@since 0.3.26rc1. Enum where members are also (and must be) strings. See [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)"
    ...

class Flag(_enum.Flag):
    "\\@since 0.3.26rc1. Support for flags. See [`enum.Flag`](https://docs.python.org/3/library/enum.html#enum.Flag)"
    ...

if _sys.version_info >= (3, 13):
    _deprecated = _warnings.deprecated
    
else:
    _deprecated = _typing_ext.deprecated

@_deprecated("Deprecated since 0.3.31, will be removed on 0.3.36. Deviating from Tkinter technology.")
class IntegerVar(_tkinter.IntVar):
    "\\@since 0.3.26rc1. Value holder for integer variables. See `tkinter.IntVar` (doc not available)"
    ...

@_deprecated("Deprecated since 0.3.31, will be removed on 0.3.36. Deviating from Tkinter technology.")
class StringVar(_tkinter.StringVar):
    "\\@since 0.3.26rc1. Value holder for string variables. See `tkinter.StringVar` (doc not available)"
    ...

@_deprecated("Deprecated since 0.3.31, will be removed on 0.3.36. Deviating from Tkinter technology.")
class BooleanVar(_tkinter.BooleanVar):
    "\\@since 0.3.26rc1. Value holder for boolean variables. See `tkinter.BooleanVar` (doc not available)"
    ...

@_deprecated("Deprecated since 0.3.31, will be removed on 0.3.36. Deviating from Tkinter technology.")
class Variable(_tkinter.Variable):
    "\\@since 0.3.26rc1. See `tkinter.Variable` (doc not available)"
    ...

@_deprecated("Deprecated since 0.3.31, will be removed on 0.3.36. Deviating from Tkinter technology.")
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

# worth noticing: these don't need type annotation with Literal
_true = True
_false = False

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

ArgInfo = _inspect.ArgInfo
"\\@since 0.3.26rc3. See `inspect.ArgInfo` (no doc available)"

Arguments = _inspect.Arguments
"\\@since 0.3.26rc3. See `inspect.Arguments` (no doc available)"

Attribute = _inspect.Attribute
"\\@since 0.3.26rc3. See `inspect.Attribute` (no doc available)"

class BlockFinder(_inspect.BlockFinder):
    """
    \\@since 0.3.26rc3. See `inspect.BlockFinder` (no doc available)
    
    Provide a `tokeneater()` method to detect the end of a code block
    """
    ...

class BoundArguments(_inspect.BoundArguments):
    """
    \\@since 0.3.26rc3. See [`inspect.BoundArguments`](https://docs.python.org/3/library/inspect.html#inspect.BoundArguments)
    
    Result of `Signature.bind()` call. Holds the mapping of arguments \\
    to the function's parameters
    """
    ...

if _sys.version_info >= (3, 12):
    # BufferFlags enum class was introduced for 3.12
    # see https://docs.python.org/3/library/inspect.html#inspect.BufferFlags
    _BufferFlags = _inspect.BufferFlags
else:
    class _BufferFlags(IntegerFlag):
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

BufferFlags = _BufferFlags
"\\@since 0.3.26rc2. See [`inspect.BufferFlags`](https://docs.python.org/3/library/inspect.html#inspect.BufferFlags)"

ByteCode = _dis.Bytecode
"\\@since 0.3.26rc3. See [`dis.Bytecode`](https://docs.python.org/3/library/dis.html#dis.Bytecode)"

CodeType = _types.CodeType
"\\@since 0.3.26rc3. See [`types.CodeType`](https://docs.python.org/3/library/types.html#types.CodeType)"

ClosureVar = _inspect.ClosureVars
"\\@since 0.3.26rc3. See `inspect.ClosureVars` (no doc available)"

class CompletedProcess(_subprocess.CompletedProcess):
    """
    \\@since 0.3.26rc3. See [`subprocess.CompletedProcess`](https://docs.python.org/3/library/subprocess.html#subprocess.CompletedProcess)

    Returned by `subprocess.run()` function
    """
    ...

EOBError = _inspect.EndOfBlock
"\\@since 0.3.26rc3. See `inspect.EndOfBlock` (no doc available)"

FrameInfo = _inspect.FrameInfo
"\\@since 0.3.26rc3. See [`inspect.FrameInfo`](https://docs.python.org/3/library/inspect.html#inspect.FrameInfo)"

FullArgSpec = _inspect.FullArgSpec
"\\@since 0.3.26rc3. See `inspect.FullArgSpec` (no doc available)"

GenericAlias = _types.GenericAlias # not really a class
"""\\@since 0.3.26rc3. See [`types.GenericAlias`](https://docs.python.org/3/library/types.html#types.GenericAlias) \n
Type for parameterized generics
"""

Instruction = _dis.Instruction
"\\@since 0.3.26rc3. See [`dis.Instruction`](https://docs.python.org/3/library/dis.html#dis.Instruction)"

from re import Match as Match
"\\@since 0.3.26. See [`re.Match`](https://docs.python.org/3/library/re.html#re.Match)"

ModuleType = _types.ModuleType
"\\@since 0.3.26rc3. See [`types.ModuleType`](https://docs.python.org/3/library/types.html#types.ModuleType)"

class Parameter(_inspect.Parameter):
    """\\@since 0.3.26rc3. See [`inspect.Parameter`](https://docs.python.org/3/library/inspect.html#inspect.Parameter) \n
    Represent a parameter in a function signature"""
    ...

class Partial(_functools.partial):
    "\\@since 0.3.26rc3. See [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial)"
    ...

partial = _functools.partial
"\\@since 0.3.26. See [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial)"

from re import Pattern as Pattern
"\\@since 0.3.26. See [`re.Pattern`](https://docs.python.org/3/library/re.html#re.Pattern)"

class Positions(_dis.Positions):
    "\\@since 0.3.26rc3. See [`dis.Positions`](https://docs.python.org/3/library/dis.html#dis.Positions)"
    ...

if _sys.version_info >= (3, 7):
    _SafeUUID = _uuid.SafeUUID
    
else:
    class _SafeUUID(Enum):
        safe = 0
        unsafe = -1
        unknown = None

SafeUUID = _SafeUUID
"""\\@since 0.3.26rc3. An enumerator class for `is_safe` parameter in `uuid.UUID` constructor \n
See [`uuid.SafeUUID`](https://docs.python.org/3/library/uuid.html#uuid.SafeUUID)"""

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

class Signature(_inspect.Signature):
    """
    \\@since 0.3.26rc2. See [`inspect.Signature`](https://docs.python.org/3/library/inspect.html#inspect.Signature)
    
    A `Signature` object represents the overall signature of a function. It stores a `Parameter` object for each \\
    parameter accepted by the function, as well as information specific to the function itself.
    """
    ...

class Timer(_timeit.Timer):
    "\\@since 0.3.26rc3. See [`timeit.Timer`](https://docs.python.org/3/library/timeit.html#timeit.Timer)"
    ...

class Traceback(_inspect.Traceback):
    "\\@since 0.3.26rc3. See [`inspect.Traceback`](https://docs.python.org/3/library/inspect.html#inspect.Traceback)"
    ...

from types import TracebackType as TracebackType
"\\@since 0.3.26rc3"

from uuid import UUID as UUID
"\\@since 0.3.26rc3. See [`uuid.UUID`](https://docs.python.org/3/library/uuid.html#uuid.UUID)"

from typing import (
    override as override,
    no_type_check as no_type_check
)

if _sys.version_info >= (3, 11): # 0.3.26rc1
    from typing import overload as overload
    
else:
    from typing_extensions import overload as overload

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
        def __init__(self, f: Callable[_P, _T_cov]):
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
        def __init__(self, f: Callable[Concatenate[type[_T], _P], _T_cov]):
            f.__isabstractmethod__ = True
            super().__init__(f)
            
noTypeCheck = no_type_check # 0.3.26rc1

# pending removal
if _sys.version_info < (3, 15):
    from typing import no_type_check_decorator as no_type_check_decorator
    noTypeCheckDecorator = no_type_check_decorator # 0.3.26rc1

from types import (
    coroutine as coroutine,
    new_class as new_class
) # 0.3.34
newClass = new_class # 0.3.26rc3
