"""
# Tense (`AveyTense` on PyPi)

\\@since 0.3.24 \\
© 2023-Present Aveyzan // License: MIT
```ts
module tense
```
Multipurpose library with several extensions, including for built-ins.

Documentation: https://aveyzan.glitch.me/tense

Submodules:
- `tense.types_collection` - types collection
- `tense.constants` - constants collection
- `tense.fencord` - connection with discord
- `tense.operators` (since 0.3.27a3) - extension of `operator` library
- `tense.databases` (since 0.3.27a4) - connection with SQL. *Experimental*
"""

from __future__ import annotations
import sys as _sys

if _sys.version_info < (3, 9):
    error = (RuntimeError, "To use AveyTense library, consider having Python 3.9 or newer")
    raise error

if _sys.version_info >= (3, 11):
    _sys.set_int_max_str_digits(0)
    
# 0.3.34: Prevent internal imports and prevent these imported subsequently
import ast as _ast
import bisect as _bisect
import builtins as _builtins
import collections as _collections
import copy as _copy
import dis as _dis
import inspect as _inspect
import io as _io
import itertools as _itertools
import math as _math
import os as _os
import pickle as _pickle
import platform as _platform
import random as _random
import re as _re
import secrets as _secrets
import socket as _socket
import subprocess as _subprocess
import time as _time
import timeit as _timeit
import types as _types
import uuid as _uuid
import warnings as _warnings

from . import _abroad as _ab_mod
from . import _constants as _cl
from . import constants as _cp
from . import util as _util
from . import types_collection as _tc
from ._primal import *
from .types_collection import Any as _Any

# between @since and @author there is unnecessarily long line spacing
# hence this warning is being thrown; it is being disabled.
_warnings.filterwarnings("ignore")

_E = {
    "string_op_right": "expected a string as a right operand",
    "ls_error": "expected a list or a string",
    "to_list_error": "expected an iterable object or instance of '{}' or '{}'".format(_tc.ListConvertible.__name__, _tc.TupleConvertible.__name__)
}

def _purify(s: type, /):
    """Sanitize the string from `<class ...>` notation"""
    return _re.sub(r"^<class '|'>$", "", str(s))

_var = _tc.TypeVar
_par = _tc.ParamSpec
_uni = _tc.Union
_lit = _tc.Literal
_opt = _tc.Optional
_cal = _tc.Callable

# local variables (0.3.39)
_MODE_AND = _cp.MODE_AND
_MODE_OR = _cp.MODE_OR
_PROBABILITY_COMPUTE = _cp.PROBABILITY_COMPUTE
_BISECT_LEFT = _cp.BISECT_LEFT
_BISECT_RIGHT = _cp.BISECT_RIGHT
_INSORT_LEFT = _cp.INSORT_LEFT
_INSORT_RIGHT = _cp.INSORT_RIGHT


# public type aliases
NULL = _tc.NULL # 0.3.34

# gimmick from enum standard module
Color = RGB = None

# TypeVars, TypeVarTuples, ParamSpecs
_S = _var("_S")
_T = _var("_T")
_T1 = _var("_T1")
_T2 = _var("_T2")
_T3 = _var("_T3")
_KT = _var("_KT")
_KT1 = _var("_KT1")
_KT2 = _var("_KT2")
_VT = _var("_VT")
_VT1 = _var("_VT1")
_VT2 = _var("_VT2")
_V1 = _var("_V1")
_V2 = _var("_V2")
_M = _var("_M")
_P = _par("_P")
_Ts = _tc.TypeVarTuple("_Ts")
_T_richComparable = _var("_T_richComparable", bound = _tc.RichComparable)
_T_func = _var("_T_func", bound = _tc.Callable[..., _tc.Any])

if _sys.version_info >= (3, 10):
    
    _U = _var("_U", bound = _types.UnionType)
    _UKT = _var("_UKT", bound = _types.UnionType)
    _UVT = _var("_UVT", bound = _types.UnionType)

else:
    
    _recreate = eval(_purify(type(_tc.Union[int, str])))
        
    _U = _var("_U", bound = _recreate) # type: ignore
    _UKT = _var("_UKT", bound = _recreate) # type: ignore
    _UVT = _var("_UVT", bound = _recreate) # type: ignore

# local enums

# class _ColorStyling(_tc.IntegerFlag): ### to 0.3.27
class _ColorStyling(_tc.Enum):
    """\\@since 0.3.26rc1. Internal class for `%` operator in class `tense.Color`."""
    NORMAL = 0
    BOLD = 1
    FAINT = 2
    ITALIC = 3
    UNDERLINE = 4
    SLOW_BLINK = 5
    RAPID_BLINK = 6
    REVERSE = 7
    HIDE = 8
    STRIKE = 9
    # PRIMARY_FONT = 10
    ## 11-19 alternative font
    # GOTHIC = 20
    DOUBLE_UNDERLINE = 21
    # NORMAL_INTENSITY = 22
    # NO_ITALIC = 23
    # NO_UNDERLINE = 24
    # NO_BLINK = 25
    # PROPORTIONAL = 26 # corrected mistake! 0.3.26rc2
    # NO_REVERSE = 27
    # UNHIDE = 28
    # NO_STRIKE = 29
    ## 30-37 foreground color, 3-bit
    # 38 foreground color, 3 4 8 24-bit
    # FOREGROUND_DEFAULT = 39
    ## 40-47 background color, 3-bit
    ## 48 background color, 3 4 8 24-bit
    # BACKGROUND_DEFAULT = 49
    # NO_PROPORTIONAL = 50
    FRAME = 51
    ENCIRCLE = 52
    OVERLINE = 53
    # NO_FRAME = 54 # including "no encircle"
    # NO_OVERLINE = 55
    ## 56 and 57 undefined
    ## 58 underline color, 3 4 8 24-bit
    # UNDERLINE_DEFAULT = 59
    # IDEOGRAM_UNDERLINE = 60
    # IDEOGRAM_DOUBLE_UNDERLINE = 61
    # IDEOGRAM_OVERLINE = 62
    # IDEOGRAM_DOUBLE_OVERLINE = 63
    # IDEOGRAM_STRESS = 64
    # NO_IDEOGRAM = 65
    ## 66-72 undefined
    SUPERSCRIPT = 73
    SUBSCRIPT = 74
    # NO_SUPERSCRIPT = 75 # also counts as no subscript
    ## 76 undefined but recommended value: no subscript
    ## 77-89 undefined
    ## 90-97 bright foreground color, 4-bit
    ## 100-107 bright background color, 4-bit

# class _ColorAdvancedStyling(_tc.IntegerFlag): ### to 0.3.27
class _ColorAdvancedStyling(_tc.Enum):
    """\\@since 0.3.26rc2. Internal class for `%` operator in class `tense.Color`."""
    
    # 2x
    BOLD_ITALIC = 1000
    BOLD_UNDERLINE = 1001
    BOLD_STRIKE = 1002
    BOLD_OVERLINE = 1003
    ITALIC_UNDERLINE = 1004
    ITALIC_STRIKE = 1005
    ITALIC_OVERLINE = 1006
    UNDERLINE_STRIKE = 1007
    UOLINE = 1008
    STRIKE_OVERLINE = 1009
    
    # 3x
    BOLD_ITALIC_UNDERLINE = 1100
    BOLD_ITALIC_STRIKE = 1101
    BOLD_ITALIC_OVERLINE = 1102
    BOLD_UNDERLINE_STRIKE = 1103
    BOLD_UOLINE = 1104
    ITALIC_UNDERLINE_STRIKE = 1105
    ITALIC_UOLINE = 1106
    ITALIC_STRIKE_OVERLINE = 1107
    STRIKE_UOLINE = 1108


# local type aliases
_Bits = _lit[3, 4, 8, 24]
_Color = _uni[_tc.ColorType, RGB]
_Mode = _uni[_cl.ModeSelection, _lit["and", "or"]] # 0.3.36
_Statement = _uni[_cal[[], object], str]
_Timer = _cal[[], float]

_AbroadValue1 = _ab_mod.AbroadValue1[_T]
_AbroadValue2 = _ab_mod.AbroadValue2[_T]
_AbroadModifier = _ab_mod.AbroadModifier[_T]
_AbroadPackType = _ab_mod.AbroadPackType[_T]
_AbroadConvectType = _ab_mod.AbroadConvectType[_T]
_AbroadLiveType = _ab_mod.AbroadLiveType[_T]
_AbroadVividType = _ab_mod.AbroadVividType[_V1, _V2, _M]
_AbroadStringInitializer = _ab_mod.AbroadStringInitializer
_AbroadFloatyInitializer = _ab_mod.AbroadFloatyInitializer
_AbroadMultiInitializer = list[list[int]]
_AbroadEachInitializer = list[_T]
_ColorStylingType = _uni[_ColorStyling, _ColorAdvancedStyling, _lit["normal", "bold", "faint", "italic", "underline", "slow_blink", "rapid_blink", "reverse", "hide", "strike", "double_underline", "frame", "encircle", "overline", "superscript", "subscript"]]
_GroupMode = _lit["and-or", "or-and", "and-nor", "nor-and", "nand-or", "or-nand", "nand-nor", "nor-nand", "and-and", "or-or", "nand-nand", "nor-nor"] # 0.3.34
_HaveCodeType = _uni[str, bytes, bytearray, _tc.MethodType, _tc.FunctionType, _tc.CodeType, type, _tc.AnyCallable, None] # from dis.dis()
_ProbabilityLengthType = _uni[int, _lit[_cp.PROBABILITY_COMPUTE]]
_ProbabilityType = _uni[_tc.Sequence[_T], _tc.Uniqual[_T], _tc.Mapping[_T, _uni[int, _tc.EllipsisType, None]]] # change 0.3.36
_ProbabilityTypeTmp = _tc.ProbabilityType[_T] # < 0.3.37
_ProbabilitySeqNoDict = _uni[list, _collections.deque, set, frozenset, tuple] # to be replaced with Sequence | AbstractSet on 0.3.42
_ProbabilitySeq = _uni[_ProbabilitySeqNoDict, dict] # 0.3.33
_ReckonNGT = _ab_mod.ReckonNGT

_builtins_type = type # note for this alias (>= 0.3.35): must be used since it obscures with parameter with exact 'type' built-in name

# removed local type aliases
# _AbroadImmutableInitializer = tuple[int, ...] ### < 0.3.36
# _FileType = _tc.FileType ### < 0.3.36
# _FileMode = _tc.FileMode ### < 0.3.36
# _FileOpener = _tc.FileOpener ### < 0.3.36


def _architecture(executable = _sys.executable, bits = "", linkage = ""):
    "\\@since 0.3.26rc2"
    
    return _platform.architecture(executable, bits, linkage)[0]

def _is_hexadecimal(target: str, /):
    _t = target
    
    if target.lower().startswith(("0x", "#")):
        _t = _re.sub(r"^(0[xX]|#)", "", _t)
    
    for c in _t:
        
        if c not in _cp.STRING_HEXADECIMAL:
            return False
        
    return True

def _is_decimal(target: str, /):
    
    for c in target:
        
        if c not in _cp.STRING_DIGITS:
            return False
        
    return True

def _is_octal(target: str, /):
    _t = target
    
    if target.lower().startswith("0o"):
        _t = _re.sub(r"^0[oO]", "", _t)
    
    for c in _t:
        
        if c not in _cp.STRING_OCTAL:
            return False
        
    return True

def _is_binary(target: str, /):
    _t = target
    
    if target.lower().startswith("0b"):
        _t = _re.sub(r"^0[bB]", "", _t)
    
    for c in _t:
        
        if c not in _cp.STRING_BINARY:
            return False
        
    return True

def _is_condition_callback(v: _Any, /) -> _tc.TypeIs[_cal[[_Any], bool]]:
    
    # Unfortunately, it may not be possible to check if specific function has desired amount of parameters of correct types.
    # Best practice would be checking function annotation and passed types to parameters, so it will work correctly.
    # 02.02.2025
    
    return (_inspect.isfunction(v) or callable(v)) and (
        reckon(_inspect.getfullargspec(v).args) == 1 and
        _inspect.getfullargspec(v).varargs is None and
        _inspect.getfullargspec(v).varkw is None and
        reckon(_inspect.getfullargspec(v).kwonlyargs) == 0 and
        _inspect.getfullargspec(v).kwonlydefaults is None and
        reckon(_inspect.getfullargspec(v).annotations) == 0
    )

def _int_conversion(target: str, /):
        
    if _is_hexadecimal(target):
        return int(target, 16)
    
    elif _is_decimal(target):
        return int(target, 10)
    
    elif _is_octal(target):
        return int(target, 8)
    
    elif _is_binary(target):
        return int(target, 2)
    
    else:
        return int(target)
    
def _colorize(text: str, bits: _Bits, fg: _tc.Union[int, None], bg: _tc.Union[int, None], /): # 0.3.37 (0.3.37a1)
        
    _s = "\033["
    # for e in (self.__fg, self.__bg, self.__un): ### removed 0.3.27
    _msg = {
        3: "for 3-bit colors, expected integer or string value in range 0-7. One of foreground or background values doesn't match this requirement",
        4: "for 4-bit colors, expected integer or string value in range 0-15. One of foreground or background values doesn't match this requirement",
        8: "for 8-bit colors, expected integer or string value in range 0-255. One of foreground or background values doesn't match this requirement",
        24: "for 2-bit colors, expected integer, string, or RGB/CMYK tuple value in range 0-16777215. One of foreground or background values doesn't match this requirement"
    }
    
    for e in (fg, bg):
        
        if e is not None:
            if bits == 3 and e not in abroad(0x8):
                error = ValueError(_msg[3])
                raise error
            
            elif bits == 4 and e not in abroad(0x10):
                error = ValueError(_msg[4])
                raise error
            
            elif bits == 8 and e not in abroad(0x100):
                error = ValueError(_msg[8])
                raise error
        
            elif bits == 24 and e not in abroad(0x1000000):
                error = ValueError(_msg[24])
                raise error
    
    if bits == 3:
        # 2 ** 3 = 8 (0x8 in hex)
        _s += str(30 + fg) + ";" if fg is not None else ""
        _s += str(40 + bg) + ";" if bg is not None else ""
        # _s += "58;5;" + str(un) + ";" if self.__un is not None else "" ### removed 0.3.27
    
    elif bits == 4:
        # 2 ** 4 = 16 (0x10 in hex); WARNING: bright colors notation isn't official
        _s += str(30 + fg) + ";" if fg is not None and fg in abroad(0x8) else ""
        _s += str(40 + bg) + ";" if bg is not None and bg in abroad(0x8) else ""
        _s += str(90 + fg) + ";" if fg is not None and fg in abroad(0x8, 0x10) else ""
        _s += str(100 + bg) + ";" if bg is not None and bg in abroad(0x8, 0x10) else ""
        # _s += "58;5;" + str(un) + ";" if un is not None else "" ### removed 0.3.27
    
    elif bits == 8:
        # 2 ** 8 = 256 (0x100 in hex)
        _s += "38;5;" + str(fg) + ";" if fg is not None else ""
        _s += "48;5;" + str(bg) + ";" if bg is not None else ""
        # _s += "58;5;" + str(self.__un) + ";" if self.__un is not None else "" ### removed 0.3.27
    
    elif bits == 24:
        # 2 ** 24 = 16777216 (0x1000000 in hex)
        # code reconstructed on 0.3.26rc2
        # acknowledgements: equivalent to rgb
        _f = hex(fg) if fg is not None else ""
        _b = hex(bg) if bg is not None else ""
        # _u = hex(self.__un) if self.__un is not None else "" ### removed 0.3.27
        _f = _re.sub(r"^(0x|#)", "", _f) if reckon(_f) > 0 else ""
        _b = _re.sub(r"^(0x|#)", "", _b) if reckon(_b) > 0 else ""
        # _u = _re.sub(r"^(0x|#)", "", _u) if reckon(_u) > 0 else "" ### removed 0.3.27
        # _hf, _hb, _hu = [None for _ in abroad(3)] ### removed 0.3.27
        _hf, _hb = [None, None]
        # for s in (_f, _b, _u): ### removed 0.3.27
        for s in (_f, _b):
            
            if reckon(s) == 6:
                if s == _f:
                    _hf = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                else:
                    _hb = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                # else:
                #    _hu = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2)) ### removed 0.3.27
                
            elif reckon(s) == 5:
                s = "0" + s
                if s == "0" + _f:
                    _hf = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                else:
                    _hb = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                # else:
                #    _hu = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                
            elif reckon(s) == 4:
                s = "00" + s
                if s == "00" + _f:
                    _hf = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                else:
                    _hb = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                # else:
                #    _hu = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2)) ### removed 0.3.27
                
            elif reckon(s) == 3:
                _tmp = "".join(s[i] * 2 for i in abroad(s)) # aliased according to css hex fff notation
                if s == _f:
                    s = _tmp
                    _hf = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                else:
                    s = _tmp
                    _hb = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                # else:
                #    s = _tmp
                #    _hu = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2)) ### removed 0.3.27
                
            elif reckon(s) == 2:
                s = "0000" + s
                if s == "0000" + _f:
                    _hf = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                else:
                    _hb = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                # else:
                #    _hu = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2)) ### removed 0.3.27
                
            elif reckon(s) == 1:
                s = "00000" + s
                if s == "00000" + _f:
                    _hf = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                else:
                    _hb = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                # else:
                #    _hu = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2)) ### removed 0.3.27
        
        _s += "38;2;" + str(_hf[0]) + ";" + str(_hf[1]) + ";" + str(_hf[2]) + ";" if _hf is not None else ""
        _s += "48;2;" + str(_hb[0]) + ";" + str(_hb[1]) + ";" + str(_hb[2]) + ";" if _hb is not None else ""
        # _s += "58;2;" + str(_hu[0]) + ";" + str(_hu[1]) + ";" + str(_hu[2]) + ";" if _hu is not None else "" ### removed 0.3.27
    else:
        error = ValueError("internal 'bits' variable value is not one from following: 3, 4, 8, 24")
        raise error
    
    if _s != "\033[":
        _s = _re.sub(r";$", "m", _s)
        _s += text + "\033[0m"
    else:
        _s = text
    return _s

def _get_all_params(f: _T_func, /):
    
    if hasattr(f, "__annotations__"):
        return [k for k in f.__annotations__ if k not in ("self", "return")]
    
    else:
        return [k for k in _inspect.get_annotations(f) if k not in ("self", "return")]
    
def _is_sequence_helper(v, /, type: type[_T] = _Any): # 0.3.36
    
    # START 0.3.35
    
    _v = [e for e in v] if not isinstance(v, list) else v
    
    if reckon(_v) == 0:
                    
        if type is _Any:
            return True
        
        return False
    
    if type is _Any or (isinstance(type, tuple) and reckon(type) == 0):
        return True
    
    # END 0.3.35
    
    # Below: If these imports weren't included, eval() invocation would throw an error.
    # in reality eval() invocation is provided, because typing.Union[X, Y, ...] is instance of a local
    # class from 'typing' module (called '_UnionGenericAlias')
    
    # In order to return '_UnionGenericAlias', we need to invoke __class_getitem__ of typing.Union[X, Y, ...]
    # but it doesn't end here. Once converted to string, <class ...> notation will be provided, so we need
    # to clean it before invocation of eval()
    
    # For now eval() invocations in code are necessary until a better solution is found.
    # 28.01.2025
    
    import types, typing
    
    if _sys.version_info >= (3, 10):
        
        if not isinstance(type,
            (
                _builtins_type, # 0.3.35
                _types.UnionType, # 0.3.36
                eval(_purify(_builtins_type(_tc.Union[int, str])), locals()), # 0.3.36; see note above
                _tc.GenericAlias, # 0.3.36
                tuple # 0.3.35
            )
        ):
            error = TypeError("passed value to parameter '{}' must be a type, not an object".format("type"))
            raise error
        
    else:
        
        if not isinstance(type,
            (
                _builtins_type, # 0.3.35
                eval(_purify(_builtins_type(_tc.Union[int, str])), locals()), # 0.3.36; see note above
                _tc.GenericAlias, # 0.3.36
                tuple # 0.3.35
            )
        ):
            error = TypeError("passed value to parameter '{}' must be a type, not an object".format("type"))
            raise error
    
    # We can remove these imports now
    del types, typing
    
    _placeholder = True
    
    if isinstance(type, _tc.GenericAlias):
                
        try:
            _placeholder = isinstance(_v, eval(_purify(type)))
            
        except:
            
            # Notice the complexity in code in case of generic types passed:
            # we expect '_v' to be a list, which can have type variable (T)
            # extracted as from 'list[T]'. Please consider singular types put
            # in a generic type, this thing isn't finished yet, and there is
            # much struggle to complete it utterly, especially many 'for' loops.
            # 27.01.2025
            
            _all_types = [""]
            _stringify = [_purify(e) for e in _tc.get_args(_tc.GenericAlias(list, type))]
            
            _all_types.clear()
            
            for e in _v:
                
                # This range of classes may be extended in the future.
                # 28.01.2025
                
                if _builtins_type(e) is _tc.Sequence and not _builtins_type(e) is tuple:
                    
                    if _sys.version_info >= (3, 10):
                        
                        _all_types.append("{}[{}]".format(_builtins_type(e).__name__, " | ".join([_purify(_builtins_type(e2)) for e2 in e])))
                    
                    else:
                        
                        # Please check this, so it can be corrected; types.UnionType exists since Python 3.10, hence this statement.
                        # 01.02.2025
                        
                        _all_types.append("{}[_tc.Union[{}]]".format(_builtins_type(e).__name__, ", ".join([_purify(_builtins_type(e2)) for e2 in e])))
                
                elif _builtins_type(e) is tuple:
                    
                    _all_types.append("{}[{}]".format(_builtins_type(e).__name__, ", ".join([_purify(_builtins_type(e2)) for e2 in e])))
                    
                else:
                    
                    _all_types.append(_purify(_builtins_type(e)))
            
            # If we kept these string values as-is, it will not work, as expected in definition
            # of generic types, that's why we use eval() there as well. Every eval() invocation
            # should return types.GenericAlias.
            # 27.01.2025
            
            return [eval(e) for e in _all_types] == [eval(e) for e in _stringify]
        
    else:
        
        for e in _v:
            
            try:
                _placeholder = _placeholder and isinstance(e, type)
                
            except:
                
                if isinstance(type, tuple):
                    
                    _subplaceholder = True
                    
                    for _type in type:
                        
                        if _type is not _builtins_type:
                            
                            # Not generic nor union, may work on it in further versions.
                            # 28.01.2025
                            
                            error = TypeError("passed items to tuple in parameter '{}' must be types, not objects".format("type"))
                            raise error
                        
                        _subplaceholder = _subplaceholder or _builtins_type(e) is _type 
                        
                    _placeholder = _placeholder and _subplaceholder
        
    return _placeholder

def _inspect_many(*v, type = _Any, mode = _MODE_AND): # 0.3.36
    
    if reckon(v) == 0:
        return False
    
    else:
        
        _placeholder = True
        
        for e in v:
            
            try:
                
                if mode in (_MODE_AND, "and"):
                    _placeholder = _placeholder and isinstance(e, type)
                    
                elif mode in (_MODE_OR, "or"):
                    _placeholder = _placeholder or isinstance(e, type)
                    
                else:
                    return False
            
            except:
                
                if mode in (_MODE_AND, "and"):
                    _placeholder = _placeholder and _builtins_type(e) is type
                    
                elif mode in (_MODE_OR, "or"):
                    _placeholder = _placeholder or _builtins_type(e) is type
                    
                else:
                    return False
                    
        return _placeholder
    
    
def _inspect_numerics(*v, mode = "b", lmode: _Mode = _MODE_AND): # 0.3.38
    
    if reckon(v) == 0:
        return False
    
    else:
        
        _placeholder = True
        
        for e in v:
            
            if lmode in (_MODE_AND, "and"):
                
                if mode == "b":
                    _placeholder = _placeholder and (type(e) is str and _is_binary(e))
                    
                elif mode == "o":
                    _placeholder = _placeholder and (type(e) is str and _is_octal(e))
                    
                elif mode == "d":
                    _placeholder = _placeholder and (type(e) is str and _is_decimal(e))
                    
                elif mode == "h":
                    _placeholder = _placeholder and (type(e) is str and _is_hexadecimal(e))
                    
                else:
                    return False
                
            elif lmode in (_MODE_OR, "or"):
                
                if mode == "b":
                    _placeholder = _placeholder or (type(e) is str and _is_binary(e))
                    
                elif mode == "o":
                    _placeholder = _placeholder or (type(e) is str and _is_octal(e))
                    
                elif mode == "d":
                    _placeholder = _placeholder or (type(e) is str and _is_decimal(e))
                    
                elif mode == "h":
                    _placeholder = _placeholder or (type(e) is str and _is_hexadecimal(e))
                    
                else:
                    return False
                
            else:
                return False
            
        return _placeholder
            
if False:
    class ParamVar:
        
        def __new__(cls, f: _cal[_P, _T], /):
            """
            \\@since 0.3.? (in code since 0.3.33)
            
            Returned dictionary with following keywords:
            - `p_k` - positional or keyword arguments
            - `p_only` - positional only arguments
            - `k_only` - keyword only arguments
            - `p_var` - variable positional argument (preceded with `*`)
            - `k_var` - variable keyword argument (preceded with `**`)
            """
            
            # temporary to deduce type Any
            _a = []
            _a.append("")
            
            _internal = {
                "tmp": [("", ("", _a[0]), _a[0])]
            }
            
            del _a, _internal["tmp"]
            
            _LACK_DEFAULT = "<lack>"
            _sig = _inspect.signature(f)
            
            _internal["p_k"] = [
                (_sig.parameters[k].name,
                (str(type(_sig.parameters[k].annotation)), _sig.parameters[k].annotation),
                _sig.parameters[k].default if _sig.parameters[k].default is _sig.parameters[k].empty else _LACK_DEFAULT) for k in _sig.parameters if _sig.parameters[k].kind == _sig.parameters[k].POSITIONAL_OR_KEYWORD
            ]
            
            _internal["p_only"] = [
                (_sig.parameters[k].name,
                (str(type(_sig.parameters[k].annotation)), _sig.parameters[k].annotation),
                _sig.parameters[k].default if _sig.parameters[k].default is _sig.parameters[k].empty else _LACK_DEFAULT) for k in _sig.parameters if _sig.parameters[k].kind == _sig.parameters[k].POSITIONAL_ONLY
            ]
            
            _internal["k_only"] = [
                (_sig.parameters[k].name,
                (str(type(_sig.parameters[k].annotation)), _sig.parameters[k].annotation),
                _sig.parameters[k].default if _sig.parameters[k].default is _sig.parameters[k].empty else _LACK_DEFAULT) for k in _sig.parameters if _sig.parameters[k].kind == _sig.parameters[k].KEYWORD_ONLY
            ]
            
            _internal["p_var"] = [
                (_sig.parameters[k].name,
                (str(type(_sig.parameters[k].annotation)), _sig.parameters[k].annotation),
                _LACK_DEFAULT) for k in _sig.parameters if _sig.parameters[k].kind == _sig.parameters[k].VAR_POSITIONAL
            ]
            
            _internal["k_var"] = [
                (_sig.parameters[k].name,
                (str(type(_sig.parameters[k].annotation)), _sig.parameters[k].annotation),
                _LACK_DEFAULT) for k in _sig.parameters if _sig.parameters[k].kind == _sig.parameters[k].VAR_KEYWORD
            ]
            
            return _internal


class TenseOptions(_util.AbstractFinal): # 0.3.27a5
    """
    \\@since 0.3.27a5
    ```ts
    in module tense
    ```
    Several settings holder class. Cannot be initialized nor subclassed.
    """
    initializationMessage = False
    """
    \\@since 0.3.27a5
    
    Toggle on/off initialization message in the terminal
    """
    
    insertionMessage = False
    """
    \\@since 0.3.27b1
    
    Toggle on/off insertion messages (these displayed by `Tense.print()`). \\
    If this option was `False`, invoked is mere `print()` method. This option \\
    has also influence on `Fencord` solutions.
    """
    if False: # to be toggled on on version 0.3.27 or later
        probabilityExtendedLength = False
        """
        \\@since 0.3.27rc1. Toggle on/off extended length via 2d list technique. Once it is toggled off, \\
        error will be thrown if going above `sys.maxsize`, `(sys.maxsize + 1) ** 2 - 1` otherwise.
        """
    
    disableProbability2LengthLimit = False
    """
    \\@since 0.3.31
    
    Switch on/off length limit, which bases on `sys.maxsize`. If that option was enabled, length passed \\
    to `Tense.probability2()` class method will no longer throw an error whether length is greater than \\
    `sys.maxsize`. This also prevents creating a temporary list to generate the result via this method. It will \\
    not work on extended variation of this method, `Tense.probability()`, unless there were exactly 2 \\
    integer values passed. Its default value is `False`
    """


class FencordOptions(_util.AbstractFinal): # 0.3.27b1
    """
    \\@since 0.3.27b1
    ```py
    from tense import FencordOptions
    ```
    Several settings holder class. Cannot be initialized nor subclassed.
    """
    
    initializationMessage = False
    "\\@since 0.3.27b1. Toggle on/off initialization message in the terminal"


class Tense( # 0.3.24
    
    # NennaiAbroads, ### < 0.3.34
    # NennaiStringz, ### < 0.3.27
    # NennaiRandomize, ### < 0.3.34
    Time,
    Math,
    # _tc.Positive[str], ### < 0.3.34
    # _tc.Negative[str], ### < 0.3.34
    # _tc.Invertible[str], ### < 0.3.34
    _tc.BitwiseLeftOperable,
    _tc.BitwiseRightOperable
    
):
    """
    \\@since 0.3.24 (standard since 0.3.24)
    ```py
    class Tense(Math, Time): ...
    from tense import Tense
    ```
    Root of TensePy. Subclassing since 0.3.26b3
    """
    from . import constants # 0.3.39
    
    from .constants import (
        VERSION as version,
        VERSION_INFO as versionInfo
    ) # last 2 = since 0.3.27a2
    
    AND = _MODE_AND
    "\\@since 0.3.36"
    
    OR = _MODE_OR
    "\\@since 0.3.36"
    
    PROBABILITY_COMPUTE = _PROBABILITY_COMPUTE
    "\\@since 0.3.26rc2"
    
    BISECT_LEFT = _BISECT_LEFT
    "\\@since 0.3.26rc2"
    
    BISECT_RIGHT = _BISECT_RIGHT
    "\\@since 0.3.26rc2"
    
    INSORT_LEFT = _INSORT_LEFT
    "\\@since 0.3.26rc2"
    
    INSORT_RIGHT = _INSORT_RIGHT
    "\\@since 0.3.26rc2"
    
    TIMEIT_TIMER_DEFAULT = _time.perf_counter
    "\\@since 0.3.26rc3"
    
    TIMEIT_NUMBER_DEFAULT = _cp.MATH_MILLION
    "\\@since 0.3.26rc3"
    
    streamLikeC = False
    "\\@since 0.3.27a5. If set to `True`, output becomes `<<` and input - `>>`, vice versa otherwise"
    
    streamInputPrompt = ""
    "\\@since 0.3.27a5. Prompt for `input()` via `>>` and `<<` operators, depending on value of setting `streamLikeC`"
    
    streamInputResult = ""
    "\\@since 0.3.27b1. Result from `>>` or `<<`, depending on which one of them is for input"
    
    
    def __init__(self):
        
        if TenseOptions.initializationMessage:
            print("\33[1;90m{}\33[1;36m INITIALIZATION\33[0m Class '{}' was successfully initalized. Line {}".format(
                super().fencordFormat(), type(self).__name__, _inspect.currentframe().f_back.f_lineno
            ))
            
    if _cl.VERSION_INFO < (0, 3, 34) and False:
        __formername__ = "Tense08"
        
        def __str__(self):
            e = super().fencordFormat()
            
            if self.__formername__ != "Tense08":
                error = ValueError(f"when invoking string constructor of '{__class__.__name__}', do not rename variable '__formername__'")
                raise error
            
            try:
                subcl = f"'{__class__.__subclasses__()[0]}', "
                for i in abroad(1, __class__.__subclasses__()):
                    subcl += f"'{__class__.__subclasses__()[i]}', "
                subcl = _re.sub(r", $", "", subcl)
                
            except IndexError(AttributeError):
                subcl = f"'{NennaiAbroads.__name__}', '{NennaiRandomize.__name__}', '{Math.__name__}', '{Time.__name__}'"
                
            return f"""
                \33[1;90m{e}\33[1;38;5;51m INFORMATION\33[0m Basic '{__class__.__name__}' class information (in module 'tense')

                Created by Aveyzan for version 0.3.24 as a deputy of cancelled class '{__class__.__formername__}'. The '{__class__.__name__}' class is a subclass of various classes located inside other
                Tense files: {subcl}. Class itself wasn't able to be subclassed (until 0.3.26b3). Generally speaking, the '{__class__.__name__}' class is a collection of many various methods inherited
                from all of these classes, but also has some defined within its body itself, like methods: probability(), random(), pick() etc.
            """
    
        def __pos__(self):
            "Return information about this class. Since 0.3.26rc1"
            return self.__str__()
        
        def __neg__(self):
            "Return information about this class. Since 0.3.26rc1"
            return self.__str__()
        
        def __invert__(self):
            "Return information about this class. Since 0.3.26rc1"
            return self.__str__()
    
    def __lshift__(self, other: object):
        "\\@since 0.3.27a5. A C-like I/O printing"
        
        if self.streamLikeC:
            self.print(other)
            
        else:
            if self.isString(other):
                self.streamInputResult = input(self.streamInputPrompt)
            else:
                error = TypeError(_E["string_op_right"])
                raise error
            
        return self
    
    def __rshift__(self, other: object):
        "\\@since 0.3.27a5. A C-like I/O printing"
        
        if not self.streamLikeC:
            self.print(other)
            
        else:
            if self.isString(other):
                self.streamInputResult = input(self.streamInputPrompt)
            else:
                error = TypeError(_E["string_op_right"])
                raise error
            
        return self
    
    @property
    def none(self):
        """
        \\@since 0.3.32
        
        This property is console-specific, and simply returns `None`.
        """
        return None
    
    ABROAD_HEX_INCLUDE = _cp.ABROAD_HEX_INCLUDE
    "\\@since 0.3.26rc2"
    
    ABROAD_HEX_HASH = _cp.ABROAD_HEX_HASH
    "\\@since 0.3.26rc2"
    
    ABROAD_HEX_EXCLUDE = _cp.ABROAD_HEX_EXCLUDE
    "\\@since 0.3.26rc2"
    
    @classmethod
    def toList(self, v: _tc.Union[_tc.Iterable[_T], _tc.ListConvertible[_T], _tc.TupleConvertible[_T]], /):
        """
        \\@since 0.3.26rc3
        ```ts
        "class method" in class Tense
        ```
        Converts a value to a `list` built-in.
        """
        
        if isinstance(v, _tc.ListConvertible):
            return v.__tlist__()
        
        elif isinstance(v, _tc.TupleConvertible):
            return list(v.__ttuple__())
        
        elif isinstance(v, _tc.Iterable):
            return list(v)
        
        else:
            error = TypeError(_E["to_list_error"])
            raise error
    
    @classmethod
    def toString(self, v: _Any = ..., /):
        """
        \\@since 0.3.26rc3
        ```ts
        "class method" in class Tense
        ```
        Alias to `Tense.toStr()`, `str()`

        Converts a value to a `str` built-in.
        """
        return str(v)
    
    @classmethod
    def toStr(self, v: _Any = ..., /):
        """
        \\@since 0.3.26rc3
        ```ts
        "class method" in class Tense
        ```
        Converts a value to a `str` built-in.
        """
        return str(v)
    
    @classmethod
    @_tc.overload
    def isNone(self, v: _Any, /) -> _tc.TypeIs[None]: ...
    
    @classmethod
    @_tc.overload
    def isNone(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isNone(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.26b3
        ```ts
        "class method" in class Tense
        ```
        Determine whether a value is `None`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = None, mode = mode)
    
    @classmethod
    @_tc.overload
    def isEllipsis(self, v: _Any, /) -> _tc.TypeIs[_tc.EllipsisType]: ...
    
    @classmethod
    @_tc.overload
    def isEllipsis(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isEllipsis(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.26
        ```ts
        "class method" in class Tense
        ```
        Determine whether a value is `...`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = _tc.EllipsisType, mode = mode)
    
    @classmethod
    @_tc.overload
    def isBool(self, v: _Any, /) -> _tc.TypeIs[bool]: ...
    
    @classmethod
    @_tc.overload
    def isBool(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isBool(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.26b3
        ```ts
        "class method" in class Tense
        ```
        Determine whether a value is of type `bool`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = bool, mode = mode)
    
    @classmethod
    @_tc.overload
    def isBoolean(self, v: _Any, /) -> _tc.TypeIs[bool]: ...
    
    @classmethod
    @_tc.overload
    def isBoolean(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isBoolean(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.26rc1
        ```ts
        "class method" in class Tense
        ```
        Alias to `Tense.isBool()`

        Determine whether a value is of type `bool`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = bool, mode = mode)
    
    @classmethod
    @_tc.overload
    def isInt(self, v: _Any, /) -> _tc.TypeIs[int]: ...
    
    @classmethod
    @_tc.overload
    def isInt(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isInt(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.26b3
        ```ts
        "class method" in class Tense
        ```
        Determine whether a value is of type `int`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = int, mode = mode)
    
    @classmethod
    @_tc.overload
    def isInteger(self, v: _Any, /) -> _tc.TypeIs[int]: ...
    
    @classmethod
    @_tc.overload
    def isInteger(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isInteger(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.26rc1
        ```ts
        "class method" in class Tense
        ```
        Alias to `Tense.isInt()`

        Determine whether a value is of type `int`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = int, mode = mode)
    
    @classmethod
    @_tc.overload
    def isFloat(self, v: _Any, /) -> _tc.TypeIs[float]: ...
    
    @classmethod
    @_tc.overload
    def isFloat(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isFloat(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.26b3
        ```ts
        "class method" in class Tense
        ```
        Determine whether a value is of type `float`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = float, mode = mode)
    
    @classmethod
    @_tc.overload
    def isComplex(self, v: _Any, /) -> _tc.TypeIs[complex]: ...
    
    @classmethod
    @_tc.overload
    def isComplex(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isComplex(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.26b3
        ```ts
        "class method" in class Tense
        ```
        Determine whether a value is of type `complex`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = complex, mode = mode)
    
    @classmethod
    @_tc.overload
    def isStr(self, v: _Any, /) -> _tc.TypeIs[str]: ...
    
    @classmethod
    @_tc.overload
    def isStr(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isStr(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.26b3
        ```ts
        "class method" in class Tense
        ```
        Determine whether a value is of type `str`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = str, mode = mode)
    
    @classmethod
    @_tc.overload
    def isString(self, v: _Any, /) -> _tc.TypeIs[str]: ...
    
    @classmethod
    @_tc.overload
    def isString(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isString(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.26rc1
        ```ts
        "class method" in class Tense
        ```
        Alias to `Tense.isStr()`

        Determine whether a value is of type `str`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = str, mode = mode)
    
    # CHANGEOVER 0.3.34
    if _cl.VERSION_INFO < (0, 3, 34) and False:
        
        @classmethod
        @_tc.overload
        def isTuple(self, v: _Any, type: type[_T] = _Any, /) -> _tc.TypeIs[tuple[_T, ...]]:
            """
            \\@since 0.3.26rc1
            
            Determine whether a value is a tuple.
            
            - 0.3.34: Added new parameters `type` and `types`
            """
            ...
        
        # this overload is experimental to be finished
        @classmethod
        @_tc.overload
        @_tc.deprecated("The overload is experimental, use the other overload, without 'types' parameter (the overload is not actually deprecated)")
        def isTuple(self, v: _Any, type: type[_T], /, *types: _tc.Unpack[_Ts]) -> _tc.TypeIs[tuple[_T, _tc.Unpack[_Ts]]]:
            """
            \\@since 0.3.26rc1
            
            Determine whether a value is a tuple. Experimental due to unexpected `False` when passing more than \\
            one type.
            
            - 0.3.34: Added new parameters `type` and `types`
            """
            ...
    
        @classmethod
        def isTuple(self, v, type = _Any, /, *types):
            """
            \\@since 0.3.26rc1
            ```ts
            "class method" in class Tense
            ```
            Determine whether a value is of type `tuple`
            """
            
            if _builtins_type(v) is tuple:
                
                _placeholder = True
                
                if reckon(types) == 0:
                    
                    if reckon(v) == 0:
                        
                        if type is _Any:
                            return True
                        
                        return False
                    
                    if not isinstance(type, _builtins_type):
                        error = TypeError("passed value to parameter '{}' must be a type, not an object".format("type"))
                        raise error
                    
                    if type is _Any:
                        return True
                    
                    for e in v:
                        
                        try:
                            _placeholder = _placeholder and isinstance(e, type)
                            
                        except:
                            _placeholder = _placeholder and _builtins_type(e) is type
                
                    return _placeholder
                
                if reckon(v) != reckon(types) - 1: # minus one due to 'type' parameter
                    return False
                
                if type is _Any:
                    pass
                
                else:
                    
                    try:
                        _placeholder = _placeholder and isinstance(v[0], type)
                        
                    except:
                        _placeholder = _placeholder and _builtins_type(v[0]) is type
                
                _types_any_check = True
                
                for i in abroad(types):
                    _types_any_check = _types_any_check and types[i] is _Any
                    
                if _types_any_check and type is _Any:
                    return True
                
                for i in abroad(1, types):
                    
                    try:
                        _placeholder = _placeholder and isinstance(v[i], types[i - 1])
                        
                    except:
                        _placeholder = _placeholder and _builtins_type(v[i]) is types[i - 1]
                    
                return _placeholder
                
            else:
                return False
            
    else:
        
        @classmethod
        @_tc.overload
        def isTuple(self, v: _Any, /, type: type[_T] = _Any) -> _tc.TypeIs[tuple[_T, ...]]: ...
        
        @classmethod
        @_tc.overload
        def isTuple(self, v: _Any, /, type: tuple[type[_T], ...]) -> _tc.TypeIs[tuple[_T, ...]]: ...
        
        if _sys.version_info >= (3, 10):
            
            @classmethod
            @_tc.overload
            def isTuple(self, v: _Any, /, type: _U) -> _tc.TypeIs[tuple[_U, ...]]: ...
        
        @classmethod
        def isTuple(self, v, /, type = _Any):
            """
            \\@since 0.3.26rc1
            ```ts
            "class method" in class Tense
            ```
            Determine whether a value is a tuple built-in.
            
            - 0.3.34: Added new parameter `type`, allowing to restrict the tuple type. Default value is `Any`. \\
            WARNING: Update appending `types` parameter is currently during experiments and may be \\
            featured later. The `types` parameter has to restrict tuple more - its content basically.
            - 0.3.35: Overload; `type` now can be a tuple of types, code will count them as union type to match against. \\
            Hence the experiments concerning `types` parameter are over (parameter isn't included).
            - 0.3.36: Generic types are now allowed. Warning: this feature is experimental
            """
            if _builtins_type(v) is tuple:
                return _is_sequence_helper(v, type = type)
            
            else:
                return False
            
    @classmethod
    @_tc.overload
    def isList(self, v: _Any, /, type: type[_T] = _Any) -> _tc.TypeIs[list[_T]]: ...
    
    @classmethod
    @_tc.overload
    def isList(self, v: _Any, /, type: tuple[type[_T], ...]) -> _tc.TypeIs[list[_T]]: ...
    
    if _sys.version_info >= (3, 10):
        
        @classmethod
        @_tc.overload
        def isList(self, v: _Any, /, type: _U) -> _tc.TypeIs[list[_U]]: ...
                    
    @classmethod
    def isList(self, v, /, type = _Any) -> _tc.TypeIs[list[_T]]:
        """
        \\@since 0.3.26rc1
        ```ts
        "class method" in class Tense
        ```
        Determine whether a value is a list built-in.
        
        - 0.3.34: Added new parameter `type`, allowing to restrict the list type. Default value is `Any`
        - 0.3.35: Overload; `type` now can be a tuple of types, code will count them as union type to match against
        - 0.3.36: Generic types are now allowed. Warning: this feature is experimental
        """
        if _builtins_type(v) is list:
            return _is_sequence_helper(v, type = type)
        
        else:
            return False
        
    @classmethod
    @_tc.overload
    def isDict(self, v: _Any, /, ktype: type[_KT] = _Any, vtype: type[_VT] = _Any) -> _tc.TypeIs[dict[_KT, _VT]]: ...
    
    @classmethod
    @_tc.overload
    def isDict(self, v: _Any, /, ktype: type[_KT], vtype: tuple[type[_VT], ...]) -> _tc.TypeIs[dict[_KT, _VT]]: ...
    
    @classmethod
    @_tc.overload
    def isDict(self, v: _Any, /, ktype: tuple[type[_KT], ...], vtype: type[_VT] = _Any) -> _tc.TypeIs[dict[_KT, _VT]]: ...
    
    @classmethod
    @_tc.overload
    def isDict(self, v: _Any, /, ktype: tuple[type[_KT], ...], vtype: tuple[type[_VT], ...]) -> _tc.TypeIs[dict[_KT, _VT]]: ...

    if _sys.version_info >= (3, 10):
        
        @classmethod
        @_tc.overload
        def isDict(self, v: _Any, /, ktype: type[_KT], vtype: _UVT) -> _tc.TypeIs[dict[_KT, _UVT]]: ...
        
        @classmethod
        @_tc.overload
        def isDict(self, v: _Any, /, ktype: _UKT, vtype: type[_VT] = _Any) -> _tc.TypeIs[dict[_UKT, _VT]]: ...
        
        @classmethod
        @_tc.overload
        def isDict(self, v: _Any, /, ktype: _UKT, vtype: tuple[type[_VT], ...]) -> _tc.TypeIs[dict[_UKT, _VT]]: ...
        
        @classmethod
        @_tc.overload
        def isDict(self, v: _Any, /, ktype: _UKT, vtype: _UVT) -> _tc.TypeIs[dict[_UKT, _UVT]]: ...
        
        @classmethod
        @_tc.overload
        def isDict(self, v: _Any, /, ktype: tuple[type[_KT], ...], vtype: _UVT) -> _tc.TypeIs[dict[_KT, _UVT]]: ...
    
    @classmethod
    def isDict(self, v, /, ktype = _Any, vtype = _Any):
        """
        \\@since 0.3.31
        ```ts
        "class method" in class Tense
        ```
        Determine whether a value is a dictionary built-in.
        
        - 0.3.34: Added 2 parameters `ktype` and `vtype`, restricting types for, respectively, keys and values. \\
            Both have default values `Any`.
        - 0.3.35: Overload; `ktype` and `vtype` now can be tuples of types, code will count them as union type to match against, \\
            respectively, keys and values.
        - 0.3.36: Generic types are now allowed. Warning: this feature is experimental
        """
        
        if type(v) is dict:
            
            vk, vv = (list(v.keys()), list(v.values()))
            return _is_sequence_helper(vk, type = ktype) and _is_sequence_helper(vv, type = vtype)
            
        else:
            return False
    
    @classmethod
    @_tc.overload
    def isSet(self, v: _Any, /, type: type[_T] = _Any) -> _tc.TypeIs[set[_T]]: ...
    
    @classmethod
    @_tc.overload
    def isSet(self, v: _Any, /, type: tuple[type[_T], ...]) -> _tc.TypeIs[set[_T]]: ...
    
    if _sys.version_info >= (3, 10):
        
        @classmethod
        @_tc.overload
        def isSet(self, v: _Any, /, type: _U) -> _tc.TypeIs[set[_U]]: ...
            
    @classmethod
    def isSet(self, v, /, type = _Any):
        """
        \\@since 0.3.35
        
        Determine whether a value is a set built-in.
        
        Parameter `type` allows to restrict the set type.
        
        - 0.3.36: Generic types are now allowed. Warning: this feature is experimental
        """
        
        if _builtins_type(v) is set:
            
            return _is_sequence_helper(v, type = type)
        
        else:
            
            return False
    
    @classmethod
    @_tc.overload
    def isFrozenSet(self, v: _Any, /, type: type[_T] = _Any) -> _tc.TypeIs[frozenset[_T]]: ...
    
    @classmethod
    @_tc.overload
    def isFrozenSet(self, v: _Any, /, type: tuple[type[_T], ...]) -> _tc.TypeIs[frozenset[_T]]: ...
    
    if _sys.version_info >= (3, 10):
        
        @classmethod
        @_tc.overload
        def isFrozenSet(self, v: _Any, /, type: _U) -> _tc.TypeIs[frozenset[_U]]: ...
        
    @classmethod
    def isFrozenSet(self, v, /, type = _Any):
        """
        \\@since 0.3.35
        
        Determine whether a value is a frozenset built-in.
        
        Parameter `type` allows to restrict the frozenset type.
        
        - 0.3.36: Generic types are now allowed. Warning: this feature is experimental
        """
        if _builtins_type(v) is frozenset:
            
            return _is_sequence_helper(v, type = type)
        
        else:
            
            return False
        
    
    @classmethod
    @_tc.overload
    def isDeque(self, v: _Any, /, type: type[_T] = _Any) -> _tc.TypeIs[_collections.deque[_T]]: ...
    
    @classmethod
    @_tc.overload
    def isDeque(self, v: _Any, /, type: tuple[type[_T], ...]) -> _tc.TypeIs[_collections.deque[_T]]: ...
    
    if _sys.version_info >= (3, 10):
        
        @classmethod
        @_tc.overload
        def isDeque(self, v: _Any, /, type: _U) -> _tc.TypeIs[_collections.deque[_U]]: ...
    
    @classmethod
    def isDeque(self, v, /, type = _Any):
        """
        \\@since 0.3.37 (added on 0.3.37a1)
        
        Determine whether a value is a deque.
        
        Parameter `type` allows to restrict the deque type.
        """
        if _builtins_type(v) is _collections.deque:
            
            return _is_sequence_helper(v, type = type)
        
        else:
            
            return False
    
    @classmethod
    @_tc.overload
    def isBytes(self, v: _Any, /) -> _tc.TypeIs[bytes]: ...
    
    @classmethod
    @_tc.overload
    def isBytes(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
        
    @classmethod
    def isBytes(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.35
        
        Determine whether a value is a bytes built-in.
        
        - 0.3.37 (0.3.37a1): many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = bytes, mode = mode)
    
    @classmethod
    @_tc.overload
    def isArray(self, v: _Any, /) -> _tc.TypeIs[_tc.array]: ... # not generic to comply with versions before Python 3.13
    
    @classmethod
    @_tc.overload
    def isArray(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
        
    @classmethod
    def isArray(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.37
        
        Determine whether a value is an array. 
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = _tc.array, mode = mode)
        
    
    @classmethod
    @_tc.overload
    def isByteArray(self, v: _Any, /) -> _tc.TypeIs[bytearray]: ...
    
    @classmethod
    @_tc.overload
    def isByteArray(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isByteArray(self, v, /, *_, mode = _MODE_AND): # not generic
        """
        \\@since 0.3.35
        
        Determine whether a value is a bytearray built-in.
        
        - 0.3.37 (0.3.37a1): many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = bytearray, mode = mode)
    
    
    @classmethod
    @_tc.overload
    def isMemoryView(self, v: _Any, /) -> _tc.TypeIs[memoryview]: ...
    
    @classmethod
    @_tc.overload
    def isMemoryView(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
        
    @classmethod
    def isMemoryView(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.35
        
        Determine whether a value is a memoryview built-in.
        
        - 0.3.37 (0.3.37a1): many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = memoryview, mode = mode)
    
    @classmethod
    def isClass(self, v: _Any, /) -> _tc.TypeIs[type[_Any]]:
        """
        \\@since 0.3.35
        
        Equivalent to `inspect.isclass()`. \\
        Determine whether a value is a class.
        """
        return isinstance(v, type)
    
    @classmethod
    def isFunction(self, v: _Any, /) -> _tc.TypeIs[_types.FunctionType]: # not generic
        """
        \\@since 0.3.35
        
        Equivalent to `inspect.isfunction()`. \\
        Determine whether a value is a function.
        """
        return isinstance(v, _types.FunctionType)
    
    
    @classmethod
    @_tc.overload
    def isBinary(self, v: _Any, /) -> bool: ...
    
    @classmethod
    @_tc.overload
    def isBinary(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isBinary(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.38
        
        Returns `True`, if value is a number in binary notation in a string. \\
        Many values can be inspected at once as well. Prefix `0b` is ignored.
        """
        _many = (v,) + _
        return _inspect_numerics(*_many, mode = "b", lmode = mode)
    
    
    @classmethod
    @_tc.overload
    def isOctal(self, v: _Any, /) -> bool: ...
    
    @classmethod
    @_tc.overload
    def isOctal(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isOctal(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.38
        
        Returns `True`, if value is a number in octal notation in a string. \\
        Many values can be inspected at once as well. Prefix `0o` is ignored.
        """
        _many = (v,) + _
        return _inspect_numerics(*_many, mode = "o", lmode = mode)
    
    
    @classmethod
    @_tc.overload
    def isDecimal(self, v: _Any, /) -> bool: ...
    
    @classmethod
    @_tc.overload
    def isDecimal(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isDecimal(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.38
        
        Returns `True`, if value is a number in decimal notation in a string. \\
        Many values can be inspected at once as well.
        
        In reality returned is `True` when `re.match(r"\\d", value)` is satisfied.
        """
        _many = (v,) + _
        return _inspect_numerics(*_many, mode = "d", lmode = mode)
    
    
    @classmethod
    @_tc.overload
    def isHexadecimal(self, v: _Any, /) -> bool: ...
    
    @classmethod
    @_tc.overload
    def isHexadecimal(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isHexadecimal(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.38
        
        Returns `True`, if value is a number in hexadecimal notation in a string. \\
        Many values can be inspected at once as well. Prefix `0x` is ignored.
        """
        _many = (v,) + _
        return _inspect_numerics(*_many, mode = "h", lmode = mode)
    
    
    @classmethod
    @_tc.overload
    def isFinalVar(self, v: _Any, /) -> _tc.TypeIs[_util.FinalVarType]: ...
    
    @classmethod
    @_tc.overload
    def isFinalVar(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isFinalVar(self, v, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.38
        
        Returns `True`, if value is a final variable (instance of `tense.util.FinalVar`).
        
        Restricting final variable type is currently rethought, for now use:
        `self.isFinalVar(v) and type(v.x) is int`
        """
        
        _many = (v,) + _
        return _inspect_many(*_many, type = _util.FinalVarType, mode = mode)
    
            
    @classmethod
    @_tc.overload
    def hasattr(self, o: object, attr: str, /) -> bool: ...
    
    @classmethod
    @_tc.overload
    def hasattr(self, o: object, attr: tuple[str, ...], /, mode: _Mode = _MODE_OR) -> bool: ...
            
    @classmethod
    def hasattr(self, o, attr, /, mode = _MODE_OR):
        """
        \\@since 0.3.34
        
        Returns `True` if object has specific attribute. Same as built-in function `hasattr()`, only 2 additional things are provided:
        - If `attr` is a string tuple, then it is deduced as `hasattr(o, attr[0]) or hasattr(o, attr[1]) or ...` \\
        Reference to how `isinstance()` works in case if types tuple is included instead of single type.
        - If `mode` is set to `"and"`, then it will occur as `hasattr(o, attr[0]) and hasattr(o, attr[1]) and ...` \\
        By default has value `"or"`. Note it works only for `attr` being a string tuple.
        """
        
        if self.isString(attr):
            
            return hasattr(o, attr)
        
        elif self.isTuple(attr, str):
            
            _r = True
            
            for many in attr:
                
                # 0.3.36: ModeSelection
                
                if mode in (_MODE_AND, "and"):
                    _r = _r or hasattr(o, many)
                    
                elif mode in (_MODE_OR, "or"): 
                    _r = _r and hasattr(o, many)
                    
                else:
                    error = ValueError("unknown mode provided, expected \"and\" or \"or\"")
                    raise error
                
            return _r
        
        error = TypeError("expected a string tuple or a string in parameter 'attr'")
        raise error
                
            
    @classmethod
    def group(self, *statements: _uni[_tc.Sequence[bool], _tc.Uniqual[bool]], mode: _GroupMode = "and-or"):
        """
        \\@since 0.3.34
        
        Returns one boolean value combining all statements into one boolean value. \\
        Parameter `mode` determines about used logical operators inside and outside \\
        provided sequences. Possible values (with `and`, `or`, `nand` = `and not`, `nor` = `or not`):
        
        - `"and-or"` = `(a1 and a2 and ... and aN) or (b1 and b2 and ... and bN) or ...`
        - `"or-and"` = `(a1 or a2 or ... or aN) and (b1 or b2 or ... or bN) and ...`
        - `"and-nor"` = `not (a1 and a2 and ... and aN) or not (b1 and b2 and ... and bN) or not ...`
        - `"nor-and"` = `(not a1 or not a2 or not ... or not aN) and (not b1 or not b2 or not ... or not bN) and ...`
        - `"nand-or"` = `(not a1 and not a2 and not ... and not aN) or (b1 and not b2 and not ... and not bN) or ...`
        - `"or-nand"` = `not (a1 or a2 or ... or aN) and not (b1 or b2 or ... or bN) and not ...`
        - `"nand-nor"` = `not (not a1 and not a2 and not ... and not aN) or not (b1 and not b2 and not ... and not bN) or not ...`
        - `"nor-nand"` = `not (not a1 or not a2 or not ... or not aN) and not (not b1 or not b2 or not ... or not bN) and not ...`
        
        Note: using modes `"and-and"`, `"or-or"`, `"nand-nand"` and `"nor-nor"` is discouraged, \\
        but will be kept to save some time writing `and`, `or` and `not` operators
        """
        
        _modes = ("and-or", "or-and", "and-nor", "nor-and", "nand-or", "or-nand", "nand-nor", "nor-nand", "and-and", "or-or", "nand-nand", "nor-nor")
        
        if mode not in _modes:
            
            error = ValueError("expected a valid mode from following: {}".format(", ".join(_modes)))
            raise error
        
        for statement in statements:
            
            if not isinstance(statement, (_tc.Sequence, _tc.Uniqual)) or (isinstance(statement, (_tc.Sequence, _tc.Uniqual)) and not self.isList(list(statement), bool)):
                
                error = ValueError("expected non-empty sequence(s) with single boolean values, like list, tuple, set or frozenset")
                raise error
            
            
        _result = _subresult = True
        
        for statement in statements:
            
            if mode == "and-and":
                
                for s in statement:
                    _subresult = _subresult and s
                    
                _result = _result and _subresult
                
            elif mode == "and-nor":
                
                for s in statement:
                    _subresult = _subresult or not s
                    
                _result = _result and _subresult
                
            elif mode == "and-or":
                
                for s in statement:
                    _subresult = _subresult or s
                    
                _result = _result and _subresult
                
            elif mode == "nand-nand":
                
                for s in statement:
                    _subresult = _subresult and not s
                    
                _result = _result and not _subresult
                
            elif mode == "nand-nor":
                
                for s in statement:
                    _subresult = _subresult or not s
                    
                _result = _result and not _subresult
                
            elif mode == "nand-or":
                
                for s in statement:
                    _subresult = _subresult or s
                    
                _result = _result and not _subresult
                
            elif mode == "nor-and":
                
                for s in statement:
                    _subresult = _subresult and s
                    
                _result = _result or not _subresult
                
            elif mode == "nor-nand":
                
                for s in statement:
                    _subresult = _subresult and not s
                    
                _result = _result or not _subresult
                
            elif mode == "nor-nor":
                
                for s in statement:
                    _subresult = _subresult or not s
                    
                _result = _result or not _subresult
                
            elif mode == "or-and":
                
                for s in statement:
                    _subresult = _subresult and s
                    
                _result = _result or _subresult
                
            elif mode == "or-nand":
                
                for s in statement:
                    _subresult = _subresult and not s
                    
                _result = _result or _subresult
                
            else:
                
                for s in statement:
                    _subresult = _subresult or s
                    
                _result = _result or _subresult
                
            _subresult = True
            
        return _result
    
    @classmethod
    def abroadPositive(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None):
        """
        \\@since 0.3.24 \\
        \\@modified 0.3.25 (moved slash to between `value1` and `value2`), 0.3.29
        ```ts
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        Every negative integer is coerced to positive.
        """
        ab = abroad(value1, value2, modifier)
        return type(ab)([abs(e) for e in ab], ab.params[0], ab.params[1], ab.params[2])
    
    @classmethod
    def abroadNegative(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None):
        """
        \\@since 0.3.24 \\
        \\@modified 0.3.25 (moved slash to between `value1` and `value2`), 0.3.29
        ```ts
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        Every positive integer is coerced to negative.
        """
        ab = abroad(value1, value2, modifier)
        return type(ab)([-abs(e) for e in ab], ab.params[0], ab.params[1], ab.params[2])
    
    @classmethod
    def abroadPositiveFlip(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None):
        """
        \\@since 0.3.24 \\
        \\@modified 0.3.25 (moved slash to between `value1` and `value2`), 0.3.29
        ```ts
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        Every negative integer is coerced to positive, then sequence is reversed.
        """
        ab = abroad(value1, value2, modifier)
        return type(ab)([abs(e) for e in ab][::-1], ab.params[0], ab.params[1], ab.params[2])
    
    @classmethod
    def abroadNegativeFlip(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None):
        """
        \\@since 0.3.24 \\
        \\@modified 0.3.25 (moved slash to between `value1` and `value2`), 0.3.29
        ```ts
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        Every positive integer is coerced to negative, then sequence is reversed.
        """
        ab = abroad(value1, value2, modifier)
        return type(ab)([-abs(e) for e in ab][::-1], ab.params[0], ab.params[1], ab.params[2])
    
    @classmethod
    def abroadPack(self, *values: _AbroadPackType[_T]):
        """
        \\@since 0.3.25 \\
        \\@modified 0.3.29
        ```ts
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        This variation of `abroad()` function bases on `zip()` Python function.
        """
        ab = abroad(reckonLeast(*values))
        return type(ab)([e for e in ab], ab.params[0], ab.params[1], ab.params[2])
    
    @classmethod
    def abroadExclude(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, *excludedIntegers: int):
        """
        \\@since 0.3.25 \\
        \\@modified 0.3.29
        ```ts
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        This variation of `abroad()` function is the same as `abroad()` function, \\
        but it also allows to exclude specific integers from the returned list. \\
        If all are excluded, returned is empty integer list. If integers excluded \\
        do not exist in returned sequence normally, this issue is omitted.
        """
        for e in excludedIntegers:
            if not isinstance(e, int):
                error = TypeError("every item in parameter 'excludedIntegers' must be an integer")
                raise error
        
        ab = abroad(value1, value2, modifier)
        return type(ab)([e for e in ab if e not in excludedIntegers], ab.params[0], ab.params[1], ab.params[2])
    
    @classmethod
    def abroadPrecede(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, prefix: _opt[str] = None):
        """
        \\@since 0.3.25 \\
        \\@modified 0.3.29
        ```ts
        // created 09.07.2024
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        This variation of `abroad()` function returns strings in a list. If `prefix` is `None`, \\
        returned are integers in strings, otherwise added is special string prefix before integers.
        """
        if prefix is not None and not isinstance(prefix, str):
            error = TypeError("expected parameter '{}' have string value".format(_get_all_params(self.abroadPrecede)[-1]))
            raise error

        ab = abroad(value1, value2, modifier)
        return _AbroadStringInitializer([str(e) for e in ab] if prefix is None else [prefix + str(e) for e in ab], ab.params[0], ab.params[1], ab.params[2])
            
    @classmethod
    def abroadSufcede(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, suffix: _opt[str] = None):
        """
        \\@since 0.3.25 \\
        \\@modified 0.3.29
        ```ts
        // created 09.07.2024
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        This variation of `abroad()` function returns strings in a list. If `prefix` is `None`, \\
        returned are integers in strings, otherwise added is special string suffix after integers.
        """
        if suffix is not None and not isinstance(suffix, str):
            error = TypeError("expected parameter '{}' have string value".format(_get_all_params(self.abroadSufcede)[-1]))
            raise error

        ab = abroad(value1, value2, modifier)
        return _AbroadStringInitializer([str(e) for e in ab] if suffix is None else [str(e) + suffix for e in ab], ab.params[0], ab.params[1], ab.params[2])
    
    @classmethod
    def abroadInside(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, string: _opt[str] = None):
        """
        \\@since 0.3.25 \\
        \\@modified 0.3.29
        ```ts
        // created 09.07.2024
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        This variation of `abroad()` function returns strings in a list. If `string` is `None`, \\
        returned are integers in strings, otherwise integers are placed inside `{}` of the string.
        """
        if string is not None and not isinstance(string, str):
            error = TypeError("expected parameter '{}' have string value".format(_get_all_params(self.abroadInside)[-1]))
            raise error

        ab = abroad(value1, value2, modifier)
        return _AbroadStringInitializer([str(e) for e in ab] if string is None else [string.format(str(e)) for e in ab], ab.params[0], ab.params[1], ab.params[2])
    
    if _cl.VERSION_INFO < (0, 3, 34) and False: # due to use of -abroad()
        @classmethod
        @_tc.deprecated("Pending removal on 0.3.30 due to reorganization of sequences returned by abroad() function and many of its variations (retrieve tuple via -abroad(...)) during 0.3.28 - 0.3.29")
        def abroadImmutable(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None) -> _AbroadImmutableInitializer:
            """
            \\@since 0.3.25
            ```ts
            // created 09.07.2024
            // to 0.3.34 in class NennaiAbroads
            "class method" in class Tense
            ```
            Immutable variation of `abroad()` function - instead of list returned is tuple. \\
            Equals `tuple(abroad(...))`.
            """
            return tuple(abroad(value1, value2, modifier))
    
    @classmethod
    def abroadConvect(self, *values: _AbroadConvectType[_T]):
        """
        \\@since 0.3.25
        ```ts
        // created 09.07.2024
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        Typical math sum operation before returned is list from `abroad()` function. \\
        If from values a value is:
        - an integer - added is this integer
        - a float - added is this number, without fraction
        - a complex - added are both real and imaginary parts
        - sizeable object - added is its length

        Notice: you can also provide negative entities! If resulted number is negative, \\
        up to `abroad()` function, sequence will go in range `[values_sum, -1]`. \\
        Otherwise, it will take this form: `[0, values_sum - 1]`.
        """
        i = 0
        _params = _get_all_params(self.abroadConvect)
        
        if reckon(values) == 0:
            error = _tc.MissingValueError("expected at least one item in parameter '{}'".format(_params[-1]))
            raise error
        
        for e in values:
            
            if not isinstance(e, (_ReckonNGT, int, float, complex)):
                error = TypeError("from gamut of supported types, parameter '{}' has at least one unsupported type".format(_params[-1]))
                raise error
            
            elif isinstance(e, int):
                i += e
                
            elif isinstance(e, float):
                i += _math.trunc(e)
                
            elif isinstance(e, complex):
                i += _math.trunc(e.real) + _math.trunc(e.imag)
                
            else:
                i += reckon(e)
        return abroad(i)
    
    @classmethod
    def abroadLive(self, *values: _AbroadLiveType[_T]):
        """
        \\@since 0.3.25
        ```ts
        // created 09.07.2024ts
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        Concept from non-monotonous sequences from math. Like graph, \\
        which changes per time. If from values a value is:
        - an integer - this is next point
        - a float - next point doesn't have fraction
        - a complex - next point is sum of real and imaginary parts
        - sizeable object - its length is next point
        """
        a, ret = [[0] for _ in abroad(2)]
        for e in (a, ret): e.clear()
        
        if reckon(values) == 0:
            error = _tc.MissingValueError("expected at least one item in parameter 'values'.")
            raise error
        
        for e in values:
            
            if not isinstance(e, (_ReckonNGT, int, float, complex)):
                error = TypeError(f"from gamut of supported types, parameter 'values' has at least one unsupported type: '{type(e).__name__}'")
                raise error
            
            elif isinstance(e, int):
                a.append(e)
                
            elif isinstance(e, float):
                a.append(_math.trunc(e))
                
            elif isinstance(e, complex):
                a.append(_math.trunc(e.real) + _math.trunc(e.imag))
                
            else:
                a.append(reckon(e))
                
        for i1 in abroad(1, a):
            tmp = a[i1]
            
            if tmp < 0:
                tmp -= 1
                
            else:
                tmp += 1
            
            for i2 in abroad(a[i1 - 1], tmp): 
                ret.append(i2)
                
        return ret
    
    @classmethod
    def abroadFloaty(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, div: _tc.FloatOrInteger = 10):
        """
        \\@since 0.3.25 \\
        \\@modified 0.3.29
        ```ts
        // created 09.07.2024
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        Every item from `abroad()` function will be divided by parameter `div`. \\
        It's default value is `10`.
        """
        if not isinstance(div, (int, float)):
            error = TypeError(f"parameter 'div' is not an integer nor floating-point number. Ensure argument got value of type 'int' or 'float'. Received type: {type(div).__name__}")
            raise error
        
        elif isinstance(div, float) and div in (_math.nan, _math.inf):
            error = ValueError("parameter 'div' may not be infinity or not a number.")
            raise error
        
        elif (isinstance(div, int) and div == 0) or (isinstance(div, float) and div == .0):
            error = ZeroDivisionError("parameter 'div' may not be equal zero. This is attempt to divide by zero")
            raise error
        
        ab = abroad(value1, value2, modifier)
        return _AbroadFloatyInitializer([e / div for e in ab], ab.params[0], ab.params[1], ab.params[2])
    
    @classmethod
    def abroadSplit(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, limit = 2) -> _AbroadMultiInitializer:
        """
        \\@since 0.3.25
        ```ts
        // created 09.07.2024
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        Reference to string slicing. Limit is amount of items, \\
        which can be in one sub-list. May not be equal or below 1.
        """
        lim = 0
        tmp, a = ([0], [[0]])
        self.clear(a, tmp)
        
        if not isinstance(limit, int):
            error = TypeError(f"parameter 'limit' is not an integer. Ensure argument got integer value. Received type: {type(limit).__name__}")
            raise error
        
        elif limit < 1:
            error = ValueError("parameter 'limit' may not be negative, or have value 0 or 1. Start from 2.")
            raise error
        
        for i in abroad(value1, value2, modifier):
            
            if lim % limit == 0:
                a.append(tmp)
                tmp.clear()
                
            else:
                tmp.append(i)
                
            lim += 1
            
        return a
    
    @classmethod
    def abroadVivid(self, *values: _AbroadVividType[_V1, _V2, _M]) -> _AbroadMultiInitializer:
        """
        \\@since 0.3.25
        ```ts
        // created 09.07.2024
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        For every value in `values` returned is list `[abroad(V1_1, V2_1?, M_1?), abroad(V1_2, V2_2?, M_2?), ...]`. \\
        Question marks are here to indicate optional values.
        """
        a = [[0]]
        a.clear()
        
        if reckon(values) < 2:
            error = ValueError("expected at least 2 items in parameter 'values'.")
            raise error
        
        for e in values:
            
            if not isinstance(e, tuple):
                error = TypeError(f"parameter 'values' has an item, which isn't a tuple. Ensure every item is a tuple. Received type: {type(e).__name__}")
                raise error
            
            if reckon(e) == 1:
                a.append(+abroad(e[0]))
                
            elif reckon(e) == 2:
                a.append(+abroad(e[0], e[1]))
                
            elif reckon(e) == 3:
                a.append(+abroad(e[0], e[1], e[2]))
                
            else:
                error = ValueError("parameter 'values' may not have empty tuples, nor tuples of size above 3.")
                raise error
            
        return a
    
    @classmethod
    @_tc.overload
    def abroadEach(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, *, each: None = None) -> _AbroadEachInitializer[int]: ...
    
    @classmethod
    @_tc.overload
    def abroadEach(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, *, each: _cal[[int], _T]) -> _AbroadEachInitializer[_T]: ...
    
    @classmethod
    def abroadEach(self, value1, /, value2 = None, modifier = None, *, each = None):
        """
        \\@since 0.3.25 (experimental for 0.3.25 - 0.3.26b1)
        ```ts
        // created 10.07.2024
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        Invoked is `each` callback for every item in `abroad()` function.
        """
        
        if (not callable(each) and each is not None):
            error = TypeError("expected None or callable with one integer parameter")
            raise error
        
        a = [0] if each is None else [object()]
        a.clear()
        
        for i in abroad(value1, value2, modifier):
            
            if each is None:
                a.append(i)
            
            else:
                a.append(each(i))
        
        return a
    
    @classmethod
    def abroadHex(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, mode = ABROAD_HEX_INCLUDE):
        """
        \\@since 0.3.25
        ```ts
        // created 10.07.2024
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        This variation of `abroad()` function returns hexadecimal representation of each integer.

        Modes (for 0.3.26rc2; to 0.3.27 support for integers):
        - `self.ABROAD_HEX_INCLUDE` - appends `0x` to each string. It faciliates casting to integer.
        - `self.ABROAD_HEX_INCLUDE_HASH` - appends `#` to each string. Reference from CSS.
        - `self.ABROAD_HEX_EXCLUDE` - nothing is appended.
        """
        a, ab = ([""], abroad(value1, value2, modifier))
        a.clear()
        
        for i in ab:
            
            if not isinstance(mode, _cl.AbroadHexMode):
                error = ValueError("expected a constant preceded with 'ABROAD_HEX_'")
                raise error
            
            elif mode == self.ABROAD_HEX_INCLUDE:
                a.append(hex(i))
                
            elif mode == self.ABROAD_HEX_HASH:
                a.append(_re.sub(r"^0x", "#", hex(i)))
                
            else:
                a.append(_re.sub(r"^0x", "", hex(i)))
        
        return _AbroadStringInitializer(a, ab.params[0], ab.params[1], ab.params[2])
    
    @classmethod
    def abroadBinary(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, include_0b = True):
        """
        \\@since 0.3.25
        ```ts
        // created 10.07.2024
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        This variation of `abroad()` function returns binary representation of each integer. \\
        Parameter `include_0b` allows to append `0b` before binary notation, what allows \\
        to faciliate casting to integer. Defaults to `True`
        """
        a, ab = ([""], abroad(value1, value2, modifier))
        a.clear()
        
        for i in ab:
            
            if not isinstance(include_0b, bool):
                error = TypeError("expected parameter 'include_0b' to be of type 'bool'.")
                raise error
            
            elif include_0b:
                a.append(bin(i))
                
            else:
                a.append(_re.sub(r"^0b", "", bin(i)))
                
        return _AbroadStringInitializer(a, ab.params[0], ab.params[1], ab.params[2])
    
    @classmethod
    def abroadOctal(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None):
        """
        \\@since 0.3.25
        ```ts
        // created 18.07.2024
        // to 0.3.34 in class NennaiAbroads
        "class method" in class Tense
        ```
        This variation of `abroad()` function returns octal representation of each integer. \\
        Every string will be preceded with `0o`
        """
        a, ab = ([""], abroad(value1, value2, modifier))
        a.clear()
        
        for i in ab:
            # if not isinstance(include_0o, bool):
            #    err, s = (TypeError, "Expected parameter 'include_0o' to be of type 'bool'.")
            #    raise err(s)
            # elif include_0o:
                a.append(oct(i))
            # else:
            #   a.append(re.sub(r"^0o", "", oct(i)))
        return _AbroadStringInitializer(a, ab.params[0], ab.params[1], ab.params[2])
                
    @classmethod
    def upgrade(self, aveytense = True):
        """
        \\@since 0.3.36
        
        Console-specific method; alias to combination: `pip uninstall ...` + `pip install ...`
        
        `aveytense` option allows to upgrade AveyTense only if set to `True` (default value is `True`)
        """
        
        if aveytense:
            
            print(Color("Getting latest stable version of AveyTense...", 8, 69) % Color.BOLD_ITALIC)
            _subprocess.run([_sys.executable, "-m", "pip", "uninstall", "--yes", "AveyTense"])
            _subprocess.run([_sys.executable, "-m", "pip", "install", "AveyTense"])
        
        else:
            _st = Color("{}", 8, 69) % Color.BOLD_ITALIC
            _in = [_sys.executable, "-m", "pip", "install"]
            
            print(_st.format("Upgrade PyPi modules of your choice. Use appropriate module name(s). 'x' exits the program."))
            a = input(_st.format(">>>"))
            
            while a.lower() != "x":
                
                a = a.lower().strip()
                _subprocess.run(_in[:3] + ["uninstall", "--yes", a])
                _subprocess.run(_in + [a])
                a = input(_st.format(">>>"))
            
        return self
    
    @classmethod
    def architecture(self, executable = _sys.executable, bits = "", linkage = ""):
        """
        \\@since 0.3.26rc2 (0.3.27a5: added optional parameters)
        ```
        "class method" in class Tense
        ```
        Returns system's architecture
        """
        return _architecture(executable, bits, linkage)
    
    @classmethod
    def disassemble(
        self,
        x: _HaveCodeType = None,
        /,
        file: _tc.Optional[_tc.IO[str]] = None,
        depth: _tc.Optional[int] = None,
        showCaches = False,
        adaptive = False,
        showOffsets = False
    ):
        """
        \\@since 0.3.26rc3
        ```
        "class method" in class Tense
        ```
        Detach code of a class, type, function, methods and other compiled objects. \\
        If argument `x` is `None` (by default is `None`), disassembled is last traceback. \\
        See [`dis.dis()`](https://docs.python.org/3/library/dis.html#dis.dis) \\
        Modified 0.3.31: added missing parameter `showOffsets`
        """
        _dis.dis(x, file = file, depth = depth, show_caches = showCaches, adaptive = adaptive, show_offsets = showOffsets)
        return self
    
    @classmethod
    def timeit(
        self,
        statement: _tc.Optional[_Statement] = None,
        /,
        setup: _tc.Optional[_Statement] = None,
        timer: _Timer = TIMEIT_TIMER_DEFAULT,
        number = TIMEIT_NUMBER_DEFAULT,
        globals: _tc.Optional[dict[str, _Any]] = None
        ):
        """
        \\@since 0.3.26rc3
        ```
        "class method" in class Tense
        ```
        See [`timeit.timeit()`](https://docs.python.org/3/library/timeit.html#timeit.timeit) \\
        Return time execution for specific code scrap (`statement`). Basic use::

            Tense.timeit(lambda: pow(3, 2)) # 0.06483080000180053
            Tense.timeit(lambda: math.pow(3, 2)) # 0.1697132999979658
            Tense.timeit(lambda: Tense.pow(3, 2)) # 0.26907890000074985
        """
        return _timeit.timeit(
            stmt = "pass" if self.isNone(statement) else statement,
            setup = "pass" if self.isNone(setup) else setup,
            timer = timer,
            number = number,
            globals = globals
        )
        
    @classmethod
    def socket(self, family: _uni[int, _socket.AddressFamily] = -1, type: _uni[int, _socket.SocketKind] = -1, proto = -1, fileno: _opt[int] = None):
        """
        \\@since 0.3.27a2
        ```
        "class method" in class Tense
        ```
        See [`socket.socket`](https://docs.python.org/3/library/socket.html#socket.socket)
        """
        return _socket.socket(family, type, proto, fileno)
    
    
    @classmethod
    def cast(self, v: _Any, t: type[_T], /) -> _T: 
        """
        \\@since 0.3.36
        
        Casts a value to specific type, keeping its primal state before type casting.
        """
        
        return v
    
    # OVERLOAD 0.3.34
    @classmethod
    @_tc.overload
    def shuffle(self, v: str) -> str: ...
    
    @classmethod
    @_tc.overload
    def shuffle(self, v: _ab_mod.AbroadInitializer) -> list[int]: ...
    
    @classmethod
    @_tc.overload
    def shuffle(self, v: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]]) -> list[_T]: ...
    
    @classmethod
    @_tc.overload
    def shuffle(self, v: _tc.Mapping[_KT, _VT]) -> dict[_KT, _VT]: ...
    
    @classmethod
    def shuffle(self, v):
        """
        \\@since 0.3.26rc1
        ```ts
        "class method" in class Tense
        ```
        Shuffle a string, mapping or a sequence, and return shuffled iterable \\
        without changing passed iterable.
        """
        
        if self.isString(v):
            _v = [c for c in v]
            _random.shuffle(_v)
            _v = "".join(_v)
            
        elif isinstance(v, _ab_mod.AbroadInitializer):
            _v = +v
            _random.shuffle(_v)
            
        elif isinstance(v, (_tc.Sequence, _tc.Uniqual)):
            _v = [e for e in v]
            _random.shuffle(_v)
            
        elif isinstance(v, _tc.Mapping):
            _v2 = [k for k in v]
            _random.shuffle(_v2)
            _v = {k: v[k] for k in _v2}
        
        else:
            error = TypeError("expected a string, mapping, sequence or result of abroad() function")
            raise error
            
        return _v
    
    # OVERLOAD 0.3.34
    @classmethod
    @_tc.overload
    def reverse(self, v: str) -> str: ...
    
    @classmethod
    @_tc.overload
    def reverse(self, v: _ab_mod.AbroadInitializer) -> list[int]: ...
    
    @classmethod
    @_tc.overload
    def reverse(self, v: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]]) -> list[_T]: ...
    
    @classmethod
    @_tc.overload
    def reverse(self, v: _tc.Mapping[_KT, _VT]) -> dict[_KT, _VT]: ...
    
    @classmethod
    def reverse(self, v):
        """
        \\@since 0.3.26rc2
        ```ts
        "class method" in class Tense
        ```
        Reverse a string, mapping or sequence, and return reversed iterable \\
        without changing passed iterable.
        """
        
        if self.isString(v):
            
            _v = [c for c in v]
            _v.reverse()
            _v = "".join(_v)
            
        elif isinstance(v, _ab_mod.AbroadInitializer):
            
            _v = +v
            _v.reverse()
            
        elif isinstance(v, (_tc.Sequence, _tc.Uniqual)):
            
            _v = [e for e in v]
            _v.reverse()
            
        elif isinstance(v, _tc.Mapping):
            
            _v2 = [k for k in v]
            _v2.reverse()
            _v = {k: v[k] for k in _v2}
            
        else:
            error = TypeError("expected a string, mapping, sequence or result of abroad() function")
            raise error
        
        return _v
    
    # OVERLOAD 0.3.34
    @classmethod
    @_tc.overload
    def occurrences(self, v: str, *items: str, mode: _lit["case_sensitive"] = "case_sensitive") -> int: ...
    
    @classmethod
    @_tc.overload
    def occurrences(self, v: str, *items: str, mode: _lit["case_insensitive"]) -> int: ...
    
    @classmethod
    @_tc.overload
    def occurrences(self, v: _ab_mod.AbroadInitializer, *items: int, mode: _lit["normal"] = "normal") -> int: ...
    
    @classmethod
    @_tc.overload
    def occurrences(self, v: _ab_mod.AbroadInitializer, *items: int, mode: _lit["absolute"]) -> int: ...
    
    @classmethod
    @_tc.overload
    def occurrences(self, v: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]], *items: _T) -> int: ...
    
    @classmethod
    @_tc.overload
    def occurrences(self, v: _tc.Mapping[_KT, _VT], *items: _KT, mode: _lit["key"] = "key") -> int: ...
    
    @classmethod
    @_tc.overload
    def occurrences(self, v: _tc.Mapping[_KT, _VT], *items: _VT, mode: _lit["value"]) -> int: ...
    
    @classmethod
    def occurrences(self, v, *items, mode = "case_sensitive"):
        """
        \\@since 0.3.32
        
        Returns number of how many times specified item appears \\
        or items appear in a sequence
        """
        
        o = 0
        m = mode.lower()
        
        if not isinstance(m, str):
            
            error = TypeError("parameter 'mode' is not a string")
            raise error
        
        if m not in ("case_sensitive", "case_insensitive", "normal", "absolute", "key", "value"):
            
            error = ValueError("parameter 'mode' provides invalid mode")
            raise error
        
        if isinstance(v, (str, _ab_mod.AbroadInitializer, _tc.Sequence, _tc.Uniqual, _tc.Mapping)) and reckon(v) == 0:
            return 0
        
        if self.isString(v):
            
            if m not in ("case_sensitive", "case_insensitive"):
                
                error = ValueError("for strings parameter 'mode' can take one of 2 modes: 'case_sensitive' and 'case_insensitive'")
                raise error
            
            
            _v = v.split()
            _s = list(items)
            
            if not self.isList(_s, str):
                
                error = ValueError("parameter 'items' doesn't utterly consist of string items")
                raise error
            
            if m == "case_insensitive":
                _s = [self.cast(s, str).lower() for s in items]
                
            for s in _v:
                
                if (s in _s and m == "case_sensitive") or (s.lower() in _s and m == "case_insensitive"):
                    o += 1
                    
            return o
                    
        elif isinstance(v, _ab_mod.AbroadInitializer):
            
            if m not in ("normal", "absolute"):
                
                error = ValueError("for instances of internal class being result of abroad() function, parameter 'mode' can take one of 2 modes: 'normal' and 'absolute'".format(_ab_mod.AbroadInitializer.__name__))
                raise error
            
            _i = list(items)
            
            if not self.isList(_i, int):
                
                error = ValueError("parameter 'items' doesn't utterly consist of integer items")
                raise error
            
            if m == "absolute":
                _i = [abs(i) for i in items]
                
                
            for i in v:
                
                if (i in _i and m == "normal") or (abs(i) in _i and m == "absolute"):
                    o += 1
                    
            return o
                    
        elif isinstance(v, (_tc.Sequence, _tc.Uniqual)):
            
            _v = list(v)
            
            for e in _v:
                
                if e in items:
                    o += 1
                    
            return o
                    
        elif isinstance(v, _tc.Mapping):
            
            if m not in ("key", "value"):
                
                error = ValueError("for mappings parameter 'mode' can take one of 2 modes: 'key' and 'value'")
                raise error
            
            if m == "key":
                _v = list(v.keys())
                
            else:
                _v = list(v.values())
                
            for e in _v:
                
                if e in items:
                    o += 1
                    
            return o
            
        else:
            error = TypeError("expected a string, mapping, sequence or result of abroad() function")
            raise error
                    
    # OVERLOAD 0.3.34
    @classmethod
    @_tc.overload
    def difference(self, v1: type[_T1], v2: type[_T2], /, invert: bool = False, value_check: bool = True) -> list[str]: ...
    
    @classmethod
    @_tc.overload
    def difference(self, v1: type[_T1], v2: _tc.Mapping[str, _T2], /, invert: bool = False, value_check: bool = True) -> list[str]: ...
    
    @classmethod
    @_tc.overload
    def difference(self, v1: _tc.Mapping[str, _T1], v2: type[_T2], /, invert: bool = False, value_check: bool = True) -> list[str]: ...
    
    @classmethod
    @_tc.overload
    def difference(self, v1: _tc.Mapping[_KT1, _VT1], v2: _tc.Mapping[_KT2, _VT2], /, invert: _lit[False] = False, value_check: bool = True) -> list[_KT1]: ...
    
    @classmethod
    @_tc.overload
    def difference(self, v1: _tc.Mapping[_KT1, _VT1], v2: _tc.Mapping[_KT2, _VT2], /, invert: _lit[True], value_check: bool = True) -> list[_KT2]: ...
    
    @classmethod
    @_tc.overload
    def difference(self, v1: type[_T], v2: _uni[_tc.Sequence[str], _tc.Uniqual[str]], /, invert: bool = False, value_check: bool = True) -> list[str]: ...
    
    @classmethod
    @_tc.overload
    def difference(self, v1: _uni[_tc.Sequence[str], _tc.Uniqual[str]], v2: type[_T], /, invert: bool = False, value_check: bool = True) -> list[str]: ...
    
    @classmethod
    @_tc.overload
    def difference(self, v1: _ab_mod.AbroadInitializer, v2: _uni[_tc.Sequence[int], _tc.Uniqual[int]], /, invert: bool = False) -> list[int]: ...
    
    @classmethod
    @_tc.overload
    def difference(self, v1: _uni[_tc.Sequence[int], _tc.Uniqual[int]], v2: _ab_mod.AbroadInitializer, /, invert: bool = False) -> list[int]: ...
    
    @classmethod
    @_tc.overload
    def difference(self, v1: _ab_mod.AbroadInitializer, v2: _ab_mod.AbroadInitializer, /, invert: bool = False) -> list[int]: ...
    
    @classmethod
    @_tc.overload
    def difference(self, v1: _uni[_tc.Sequence[_T1], _tc.Uniqual[_T1]], v2: _uni[_tc.Sequence[_T2], _tc.Uniqual[_T2]], /, invert: _lit[False] = False) -> list[_T1]: ...
    
    @classmethod
    @_tc.overload
    def difference(self, v1: _uni[_tc.Sequence[_T1], _tc.Uniqual[_T1]], v2: _uni[_tc.Sequence[_T2], _tc.Uniqual[_T2]], /, invert: _lit[True]) -> list[_T2]: ...
    
    @classmethod
    def difference(self, v1, v2, /, invert = False, value_check = True):
        """
        \\@since 0.3.32
        
        Find items, which belong to `v1`, but do not belong to `v2` (math difference `v1 \\ v2`). \\
        With `invert` being `True` it is vice versa (`v2 \\ v1`).
        
        When `value_check` is `True`, values from fields in classes or dictionairies will be also checked. \\
        In this case when values are different, then they are included in the returned list.
        
        For class fields with roundly underscored names, these fields aren't counted.
        """
        _v1, _v2 = [{} for _ in abroad(2)]
        
        if isinstance(v1, type):
            
            if isinstance(v2, type):
                
                _v1 = {k: v1.__annotations__[k] for k in v1.__annotations__ if k[:1] != "_"}
                _v2 = {k: v2.__annotations__[k] for k in v2.__annotations__ if k[:1] != "_"}
            
            elif isinstance(v2, _tc.Mapping):
                
                if not self.isList([k for k in v2], str):
                    
                    error = ValueError("with comparison with a class expected a string-key-typed mapping")
                    raise error
                
                _v1 = {k: v1.__annotations__[k] for k in v1.__annotations__ if k[:1] != "_"}
                _v2 = {k: v2[k] for k in v2 if k[:1] != "_"}
            
            elif isinstance(v2, (_tc.Sequence, _tc.Uniqual)):
                
                if not self.isList([k for k in v2], str):
                    
                    error = ValueError("with comparison with a class expected a string-typed sequence")
                    raise error
                
                _v1 = [k for k in v1.__annotations__]
                _v2 = list(v2)
                
            else:
                error = TypeError("with comparison with a class expected another class or string sequence, mapping with string keys")
                raise error
        
        elif isinstance(v1, _tc.Mapping):
            
            if isinstance(v2, type):
                
                if not self.isList([k for k in v1], str):
                    
                    error = ValueError("with comparison with a class expected a string-key-typed mapping")
                    raise error
                
                _v1 = {k: v1[k] for k in v1 if k[:1] != "_"}
                _v2 = {k: v2.__annotations__[k] for k in v2.__annotations__ if k[:1] != "_"}
                
            elif isinstance(v2, _tc.Mapping):
                
                _v1 = {k: v1[k] for k in v1 if k[:1] != "_"}
                _v2 = {k: v2[k] for k in v2 if k[:1] != "_"}
                
            else:
                error = TypeError("with comparison with a mapping expected another mapping or a class")
                raise error
        
        elif isinstance(v1, _ab_mod.AbroadInitializer):
            
            if isinstance(v2, _ab_mod.AbroadInitializer):
                
                _v1 = +v1
                _v2 = +v2
                
                if invert:
                    return [e for e in _v1 if e not in _v2]
                
                else:
                    return [e for e in _v2 if e not in _v1]
                
            elif isinstance(v2, (_tc.Sequence, _tc.Uniqual)):
                
                if not self.isList([e for e in v2], int):
                    
                    error = ValueError("with comparison with a result from abroad() function expected an integer sequence")
                    raise error
                
                _v1 = +v1
                _v2 = list(v2)
                
            else:
                error = TypeError("with comparison with a result from abroad() function expected another abroad() function result or integer sequence")
                raise error
            
        elif isinstance(v1, (_tc.Sequence, _tc.Uniqual)):
            
            if isinstance(v2, type):
                
                if not self.isList([k for k in v1], str):
                    
                    error = ValueError("with comparison with a class expected a string-typed sequence")
                    raise error
                
                _v1 = list(v1)
                _v2 = [k for k in v2.__annotations__]
                
            elif isinstance(v2, _ab_mod.AbroadInitializer):
                
                if not self.isList([e for e in v2], int):
                    
                    error = ValueError("with comparison with a result from abroad() function expected an integer sequence")
                    raise error
                
                _v1 = list(v1)
                _v2 = +v2
                
            elif isinstance(v2, (_tc.Sequence, _tc.Uniqual)):
                
                _v1 = list(v1)
                _v2 = list(v2)
                
        if invert:
            _v1, _v2 = _v2, _v1
            
        _res = [k for k in _v1 if k not in _v2]
        
        if value_check and isinstance(_v1, dict) and isinstance(_v2, dict):
            
            for k in _v1:
                
                if k in _v2 and _v1[k] != _v2[k]:
                    _res.append(k)
        
        _res.sort()
        return _res
    
    # OVERLOAD 0.3.34
    @classmethod
    @_tc.overload
    def intersection(self, v: int, /, *_: int) -> int: ...
    
    @classmethod
    @_tc.overload
    def intersection(self, v: bool, /, *_: bool) -> bool: ...
    
    @classmethod
    @_tc.overload
    def intersection(self, v: _tc.Iterable[_T], /, *_: _tc.Iterable[_Any]) -> list[_T]: ...
                        
    @classmethod
    def intersection(self, v, /, *_):
        """
        \\@since 0.3.34
        
        Returns list of items, which appear in all sequences (math intersection `v1 \u2229 v2 \u2229 ... \u2229 vN`). \\
        In case of integers returned is bitwise AND (`&`) taken on all integers. \\
        In case of boolean values returned is logical AND (`and`) taken on all boolean values.
        """
        if isinstance(v, bool):
            
            if reckon(_) == 0:
                return v
            
            else:
                
                if not self.isList([e for e in _], bool):
                    
                    error = ValueError("expected every value a boolean value")
                    raise error
                
                _v = v
                
                for e in _:
                    _v = _v and e
                    
                return _v
        
        elif isinstance(v, int):
            
            if reckon(_) == 0:
                return v
            
            else:
                
                if not self.isList([e for e in _], int):
                    
                    error = ValueError("expected every value an integer")
                    raise error
                
                _v = v
                
                for e in _:
                    _v &= e
                    
                return _v
            
        elif isinstance(v, _tc.Iterable):
            
            if reckon(_) == 0:
                return list(v)
            
            else:
                
                if not self.isList([e for e in _], _tc.Iterable):
                    
                    error = ValueError("expected every value an iterable")
                    raise error
                
                return list(set(v).intersection(*_))
            
        else:
            error = TypeError("expected every value either integers, boolean values or iterable objects")
            raise error
    
    # OVERLOAD 0.3.34
    @classmethod
    @_tc.overload
    def union(self, v: int, /, *_: int) -> int: ...
    
    @classmethod
    @_tc.overload
    def union(self, v: bool, /, *_: bool) -> bool: ...
    
    @classmethod
    @_tc.overload
    def union(self, v: _tc.Iterable[_T1], /, *_: _tc.Iterable[_T2]) -> list[_uni[_T1, _T2]]: ...
    
    @classmethod
    def union(self, v, /, *_):
        """
        \\@since 0.3.34
        
        Returns list of items, which appear in any sequences (math union `v1 \u222A v2 \u222A ... \u222A vN`). \\
        In case of integers returned is bitwise OR (`|`) taken on all integers. \\
        In case of boolean values returned is logical OR (`or`) taken on all boolean values.
        """
        
        if isinstance(v, bool):
            
            if reckon(_) == 0:
                return v
            
            else:
                
                if not self.isList([e for e in _], bool):
                    
                    error = ValueError("expected every value a boolean value")
                    raise error
                
                _v = v
                
                for e in _:
                    _v = _v or e
                    
                return _v
        
        elif isinstance(v, int):
            
            if reckon(_) == 0:
                return v
            
            else:
                
                if not self.isList([e for e in _], int):
                    
                    error = ValueError("expected every value an integer")
                    raise error
                
                _v = v
                
                for e in _:
                    _v |= e
                    
                return _v
            
        elif isinstance(v, _tc.Iterable):
            
            if reckon(_) == 0:
                return list(v)
            
            else:
                
                if not self.isList([e for e in _], _tc.Iterable):
                    
                    error = ValueError("expected every value an iterable")
                    raise error
                
                return list(set(v).union(*_))
            
        else:
            error = TypeError("expected every value either integers, boolean values or iterable objects")
            raise error
    
    @classmethod
    def append(self, i: _tc.Iterable[_T], /, *items: _T):
        """
        \\@since 0.3.27a4
        ```ts
        "class method" in class Tense
        ```
        Same as `list.append()`, just variable amount of items can be passed. \\
        Input list remains non-modified, and returned is its modified copy.
        
        Since 0.3.34, because mutable sequences are normally coerced to list, allowed are also \\
        all other iterables
        """
        return [e for e in i] + [e for e in items]
    
    @classmethod
    def extend(self, i: _tc.Iterable[_T], /, *iters: _tc.Iterable[_T]):
        """
        \\@since 0.3.27a4
        ```ts
        "class method" in class Tense
        ```
        Same as `list.extend()`, just variable amount of iterables can be passed. \\
        Input list remains non-modified, and returned is its modified copy.
        
        Since 0.3.34, because mutable sequences are normally coerced to list, allowed are also \\
        all other iterables
        """
        _seq = [e for e in i]
        
        for e in iters:
            _seq.extend(e)
                
        return _seq
    
    @classmethod
    def exclude(self, i: _tc.Iterable[_T], /, *items: _T):
        """
        \\@since 0.3.34
        
        Return a new list from iterable without items specified
        """
        return [e for e in i if e not in items]
    
    @classmethod
    def explode(self, s: str, /, separator: _opt[str] = None, max = -1, no_empty = False):
        """
        \\@since 0.3.34
        
        Reference from PHP inbuilt function `explode()`. Split a string \\
        using specified separator into a string list.
        """
        _params = _get_all_params(self.explode)
        
        # error message template
        _msgtmpl = "expected {} in parameter '{}'"
        
        _msg = ["" for _ in abroad(_params)]
        _msg[0] = _msgtmpl.format("a string", _params[0])
        _msg[1] = _msgtmpl.format("a string or None", _params[1])
        _msg[2] = _msgtmpl.format("an integer for -1 above (not being zero)", _params[2])
        
        if not self.isString(s):
            error = TypeError(_msg[0])
            raise error
        
        if not self.isString(separator) and not self.isNone(separator):
            error = TypeError(_msg[1])
            raise error
        
        if not self.isInteger(max) or (self.isInteger(max) and max != -1 and max < 1):
            error = TypeError(_msg[2])
            raise error
        
        if no_empty:
            return [k for k in s.split(separator, max) if reckon(k) != 0]
        
        return s.split(separator, max)

    @classmethod
    def clear(self, *v: _tc.Union[_tc.MutableSequence[_T], _tc.MutableUniqual[_T], _tc.MutableMapping[_Any, _T], Color, str]):
        """
        \\@since 0.3.27a4
        ```ts
        "class method" in class Tense
        ```
        Same as `list.clear()`, just variable amount of lists can be passed. \\
        Since 0.3.27b1 strings are also passable. Since 0.3.36 - sets, and since \\
        0.3.37 - mutable mappings/dictionairies.
        """
        for seq in v:
            
            if self.isString(seq):
                seq = ""
                
            elif isinstance(seq, (_tc.MutableSequence, _tc.MutableUniqual, _tc.MutableMapping, Color)):
                seq.clear() # 4 definitions
                
            else:
                error = ValueError("expected a mutable sequence, mutable mapping or string")
                raise error
                
    @classmethod
    def copy(self, x: _T):
        """\\@since 0.3.34"""
        return _copy.copy(x)
    
    
    @classmethod
    def deepcopy(self, x: _T, memo: _opt[dict[int, _Any]] = None, _nil: _Any = []):
        """\\@since 0.3.34"""
        return _copy.deepcopy(x, memo, _nil)
    

    # OVERLOAD 0.3.34
    if False:
        @classmethod
        def eval(self, source: _tc.Union[str, _tc.Buffer, _ast.Module, _ast.Expression, _ast.Interactive], ast = False):
            
            if not ast:
                return eval(compile(source))
            
            else:
                
                if not self.isString(source) and not isinstance(source, _tc.Buffer):
                    error = TypeError("for ast.literal_eval expected a string or buffer")
                    raise error
                
                else:
                    return _ast.literal_eval(str(source) if not self.isString(source) else source)
                
    else:
        
        # for ValueError exception reason, there is no 'str' in this overload, instead create an AST instance
        @classmethod
        @_tc.overload
        def eval(self, source: _ast.AST, /) -> _Any:
            """\\@since 0.3.26rc2"""
            ...
            
        @classmethod
        @_tc.overload
        def eval(self, source: _uni[str, _tc.Buffer, _tc.CodeType], /, globals: _opt[dict[str, _Any]] = None, locals: _opt[_tc.Mapping[str, object]] = None) -> _Any:
            """\\@since 0.3.26rc2"""
            ...
            
        @classmethod
        @_tc.overload
        def eval(
            self,
            source: tuple[_uni[str, _tc.Buffer, _ast.Module, _ast.Expression, _ast.Interactive], _uni[str, _tc.Buffer, _tc.PathLike[_Any]], str],
            /,
            globals: _opt[dict[str, _Any]] = None,
            locals: _opt[_tc.Mapping[str, object]] = None,
            flags: int = 0,
            dont_inherit: bool = False,
            optimize: int = -1
        ) -> _Any:
            """\\@since 0.3.26rc2"""
            ...
            
        @classmethod
        def eval(self, source, /, globals = None, locals = None, flags = 0, dont_inherit = False, optimize = -1):
            
            if (
                isinstance(source, (str, _ast.AST, _tc.Buffer, _tc.CodeType)) and
                (isinstance(globals, dict) or globals is None) and
                (isinstance(locals, _tc.Mapping) or locals is None)
            ):
                
                if isinstance(source, (str, _tc.Buffer, _tc.CodeType)):
                            
                    return _builtins.eval(source, globals, locals)
                
                else:
                    
                    return _ast.literal_eval(source)
                    
            elif isinstance(source, tuple):
                
                if reckon(source) == 3 and (
                    isinstance(source[0], (str, _tc.Buffer, _ast.Module, _ast.Expression, _ast.Interactive)) and # 'source'
                    isinstance(source[1], (str, _tc.Buffer, _os.PathLike)) and # 'fn': importing 'PathLike' from 'os' since from abc module in this project is a type alias
                    isinstance(source[2], str) and # 'mode'
                    (isinstance(globals, dict) or globals is None) and
                    (isinstance(locals, _tc.Mapping) or locals is None) and
                    isinstance(flags, int) and
                    isinstance(dont_inherit, bool) and
                    isinstance(optimize, int)
                ):
                    
                    _res = compile(source[0], source[1], source[2], flags, dont_inherit, optimize)
                    
                    if isinstance(_res, _ast.AST):
                        
                        return _ast.literal_eval(_res)
                    
                    elif isinstance(_res, str):
                        
                        try:
                            return _ast.literal_eval(_res)
                        
                        except ValueError:
                            return _builtins.eval(_res, globals, locals)
                    
                    elif isinstance(_res, _tc.CodeType):
                        return _builtins.eval(_res, globals, locals)
                    
                    return _res # I would care less about this result
            
            error = TypeError("no matching function signature; make sure every type requirement is satisfied")
            raise error
                        
    # OVERLOAD 0.3.34
    @classmethod
    @_tc.overload
    def bisect(self, a: _tc.SizeableItemGetter[_T_richComparable], x: _T_richComparable, /, l: int = 0, h: _opt[int] = None, dir: _cl.BisectMode = BISECT_RIGHT, *, key: None = None) -> int:
        """\\@since 0.3.26rc2"""
        ...
    
    @classmethod
    @_tc.overload
    def bisect(self, a: _tc.SizeableItemGetter[_T], x: _T_richComparable, /, l: int = 0, h: _opt[int] = None, dir: _cl.BisectMode = BISECT_RIGHT, *, key: _cal[[_T], _T_richComparable]) -> int:
        """\\@since 0.3.26rc2"""
        ...
            
    @classmethod
    def bisect(self, a, x, /, l = 0, h = None, dir = BISECT_RIGHT, *, key = None):
        
        if (
            self.isInteger(l) and
            (self.isInteger(h) or self.isNone(h)) and
            isinstance(dir, _cl.BisectMode)
        ):
            
            if not _inspect.isfunction(key):
                return _bisect.bisect_right(a, x, l, h) if dir == self.BISECT_RIGHT else _bisect.bisect_left(a, x, l, h)
            
            else:
                return _bisect.bisect_right(a, x, l, h, key = key) if dir == self.BISECT_RIGHT else _bisect.bisect_left(a, x, l, h, key = key)
        
        error = TypeError("no matching function signature; make sure every type requirement is satisfied")
        raise error
    
    # OVERLOAD 0.3.34
    if False:
        @classmethod
        def insort(self, seq: _tc.MutableSequence[_T], item: _T, low: int = 0, high: _opt[int] = None, mode: _cl.InsortMode = INSORT_RIGHT, key: _opt[_cal[[_T], _T_richComparable]] = None):
            
            _seq = seq
            if mode == self.INSORT_LEFT:
                _bisect.insort_left(_seq, item, low, high, key = key)
                
            elif mode == self.INSORT_RIGHT:
                _bisect.insort_right(_seq, item, low, high, key = key)
                
            else:
                error = TypeError("incompatible value for 'mode' parameter. Expected one of constants: 'INSORT_LEFT' or 'INSORT_RIGHT'")
                raise error
            return _seq
        
    else:
        
        @classmethod
        @_tc.overload
        def insort(self, a: _tc.MutableSequence[_T_richComparable], x: _T_richComparable, /, l: int = 0, h: _opt[int] = None, dir: _cl.InsortMode = INSORT_RIGHT, *, key: None = None) -> None:
            """\\@since 0.3.26rc2"""
            ...
            
        @classmethod
        @_tc.overload
        def insort(self, a: _tc.MutableSequence[_T], x: _T_richComparable, /, l: int = 0, h: _opt[int] = None, dir: _cl.InsortMode = INSORT_RIGHT, *, key: _cal[[_T], _T_richComparable]) -> None:
            """\\@since 0.3.26rc2"""
            ...
            
        @classmethod
        def insort(self, a, x, /, l = 0, h = None, dir = INSORT_RIGHT, *, key = None):
            
            if (
                self.isInteger(l) and
                (self.isInteger(h) or self.isNone(h)) and
                isinstance(dir, _cl.InsortMode)
            ):
                
                if not _inspect.isfunction(key):
                    return _bisect.insort_right(a, x, l, h) if dir == self.INSORT_RIGHT else _bisect.insort_left(a, x, l, h)
                
                else:
                    return _bisect.insort_right(a, x, l, h, key = key) if dir == self.INSORT_RIGHT else _bisect.insort_left(a, x, l, h, key = key)
            
            error = TypeError("no matching function signature; make sure every type requirement is satisfied")
            raise error
    
    @classmethod
    def print(self, *values: object, separator: _opt[str] = " ", ending: _opt[str] = "\n", file: _uni[_tc.Writable[str], _tc.Flushable, None] = None, flush: bool = False, invokeAs = "INSERTION"):
        """
        \\@since 0.3.25
        ```
        "class method" in class Tense
        ```
        Same as `print()`, just with `INSERTION` beginning. It can be \\
        changed with `invokeAs` parameter. Since 0.3.26a1 this method \\
        returns reference to this class. Since 0.3.27b1, if setting \\
        `TenseOptions.insertionMessage` was `False`, `invokeAs` \\
        parameter will lose its meaning.
        """
        if TenseOptions.insertionMessage is True:
            e = super().fencordFormat()
            print(f"\33[1;90m{e}\33[1;38;5;45m {invokeAs}\33[0m", *values, sep = separator, end = ending, file = file, flush = flush)
            
        else:
            print(*values, sep = separator, end = ending, file = file, flush = flush)
            
        return self
    
    @classmethod
    @_tc.overload
    def random(self, x: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]], /) -> _T: ...
    
    @classmethod
    @_tc.overload
    def random(self, x: int, /) -> int: ...
    
    @classmethod
    @_tc.overload
    def random(self, x: int, y: int, /) -> int: ...
    
    @classmethod
    def random(self, x, y = None, /):
        """
        \\@since 0.3.24 (standard since 0.3.25) \\
        \\@lifetime ≥ 0.3.24 \\
        \\@modified 0.3.25, 0.3.26rc2 (support for `tkinter.IntVar`), 0.3.31 (cancelled support for `tkinter.IntVar`) \\
        0.3.34 (overloads)
        ```
        "class method" in class Tense
        ```
        With one parameter, returns an item from a sequence or integer from range [0, x) \\
        With two parameters, returns an integer in specified range [x, y] or [y, x] if x > y.
        """
        if self.isNone(y):
            
            if self.isInteger(x):
                
                if x <= 1:
                    error = ValueError("expected a positive integer above 1")
                    raise error
                
                # note random.randrange() is also a thing
                return _secrets.randbelow(x)
            
            elif isinstance(x, (_tc.Sequence, _tc.Uniqual)):
                
                return _random.choice(list(x))
            
        a = [x, y]
        
        if self.isList(a, int):
                
            _x, _y = x, y
            
            if x > y:
                _x, _y = _y, _x
            
            return _random.randint(_x, _y)
            
        error = TypeError("no matching function signature")
        raise error
                
    @classmethod
    def randstr(self, lower = True, upper = True, digits = True, special = True, length = 10):
        """
        \\@since 0.3.9 \\
        \\@lifetime ≥ 0.3.9; < 0.3.24; ≥ 0.3.25 \\
        to 0.3.34 known as `NennaiRandomize.randomizeStr()`
        ```
        # created 15.07.2024
        "class method" in class NennaiRandomize
        ```
        - `lower` - determine, if you want to include all lowercased letters from english alphabet. Defaults to `True`
        - `upper` - determine, if you want to include all uppercased letters from english alphabet. Defaults to `True`
        - `digits` - determine, if you want to include all numbers. Defaults to `True`
        - `special` - determine, if you want to include all remaining chars accessible normally via English keyboard. \\
        Defaults to `True`
        - `length` - allows to specify the length of returned string. Defaults to `10`.
        """
        # code change 0.3.34
        conv = [""]
        conv.clear()
        ret = ""
        
        if lower:
            conv.extend([e for e in _cp.STRING_LOWER])
                
        if upper:
            conv.extend([e for e in _cp.STRING_UPPER])
                
        if digits:
            conv.extend([e for e in _cp.STRING_DIGITS])
                
        if special:
            conv.extend([e for e in _cp.STRING_SPECIAL])
        
        # there no matter if negative or positive
        for _ in abroad(length):
            ret += self.pick(conv)
            
        return ret
    
    @classmethod
    def uuidPrimary(self, node: _uni[int, None] = None, clockSeq: _uni[int, None] = None):
        """
        \\@since 0.3.26a1 \\
        \\@modified 0.3.31 (cancelled support for `tkinter.IntVar`)
        ```ts
        // created 20.07.2024
        "class method" in class Tense
        ```
        Return an UUID from host ID, sequence number and the current time.
        """
        _n = node
        _c = clockSeq
        return _uuid.uuid1(node = _n, clock_seq = _c)
    
    @classmethod
    def uuidMd5(self, namespace: _tc.UUID, name: _uni[str, bytes]):
        """
        \\@since 0.3.26a1 \\
        \\@modified 0.3.31 (cancelled support for `tkinter.StringVar`)
        ```ts
        // created 20.07.2024
        "class method" in class Tense
        ```
        Return an UUID from the MD5 (Message Digest) hash of a namespace UUID and a name
        """
        return _uuid.uuid3(namespace = namespace, name = name)
    
    @classmethod
    def uuidRandom(self):
        """
        \\@since 0.3.26a1
        ```ts
        // created 20.07.2024
        "class method" in class Tense
        ```
        Return a random UUID
        """
        return _uuid.uuid4()
    
    @classmethod
    def uuidSha1(self, namespace: _tc.UUID, name: _uni[str, bytes]):
        """
        \\@since 0.3.26a1 \\
        \\@modified 0.3.31 (cancelled support for `tkinter.StringVar`)
        ```ts
        "class method" in class Tense
        ```
        Return an UUID from the SHA-1 (Secure Hash Algorithm) hash of a namespace UUID and a name
        """
        return _uuid.uuid5(namespace = namespace, name = name)
    
    @classmethod
    @_tc.overload
    def pick(self, i: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]], /, secure: bool = False) -> _T: ... # sets act the same as lists in this case
    
    @classmethod
    @_tc.overload
    def pick(self, i: _tc.Mapping[_KT, _VT], /, secure: bool = False) -> _VT: ...
    
    @classmethod
    def pick(self, i, /, secure = False):
        """
        \\@since 0.3.8 (standard since 0.3.24) \\
        \\@lifetime ≥ 0.3.8 \\
        \\@modified 0.3.25, 0.3.26rc2, 0.3.26rc3, 0.3.34
        ```ts
        "class method" in class Tense
        ```
        Returns random item from a sequence (+ mapping since 0.3.34)
        """
        if isinstance(i, (_tc.Sequence, _tc.Uniqual)):
            
            if secure:
                return _secrets.choice(i)
            
            else:
                return _random.choice(i)
        
        elif isinstance(i, _tc.Mapping):
            
            if secure:
                return i[_secrets.choice([k for k in i])]
            
            else:
                return i[_random.choice([k for k in i])]
        
        else:
            error = TypeError("expected a sequence or mapping")
            raise error
    
    if _cl.VERSION_INFO < (0, 3, 31) and False: # deprecated since 0.3.25, removed 0.3.31
        def error(self, handler: type[Exception], message: _uni[str, None] = None):
            """
            \\@since 0.3.24 \\
            \\@deprecated 0.3.25
            ```
            "class method" in class Tense
            ```
            """
            _user_defined_error = handler
            _user_defined_reason = message
            if _user_defined_reason is None:
                raise _user_defined_error()
            else:
                raise _user_defined_error(_user_defined_reason)
            
            
    # OVERLOAD 0.3.34
    @classmethod
    @_tc.overload
    def first(self, i: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]], /, condition: None = None, default: _S = None) -> _uni[_S, _T]: ...
    
    @classmethod
    @_tc.overload
    def first(self, i: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]], /, condition: _cal[[_T], bool], default: _S = None) -> _uni[_S, _T]: ...
            
    @classmethod
    def first(self, i, /, condition = None, default = None):
        """
        \\@since 0.3.26rc2
        ```
        "class method" in class Tense
        ```
        Return first element in a `seq` (sequence) which satisfies `condition`. If none found, returned \\
        is default value defined via parameter `default`, which by default has value `None`. On 0.3.27a4 \\
        removed this parameter, it has been restored on 0.3.34
        """
        
        if not _is_condition_callback(condition) and not self.isNone(condition):
            error = TypeError("expected 'condition' parameter to be a callable or 'None'")
            raise error
        
        _seq = list(i)
        
        for _i in abroad(_seq):
            
            if condition is not None and condition(_seq[_i]):
                return _seq[_i]
            
            else:
                if _seq[_i]: return _seq[_i]
                
        return default
    
    # OVERLOAD 0.3.34
    @classmethod
    @_tc.overload
    def last(self, i: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]], /, condition: None = None, default: _S = None) -> _uni[_S, _T]: ...
    
    @classmethod
    @_tc.overload
    def last(self, i: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]], /, condition: _cal[[_T], bool], default: _S = None) -> _uni[_S, _T]: ...
    
    @classmethod
    def last(self, i, /, condition = None, default = None):
        """
        \\@since 0.3.26rc2
        ```
        "class method" in class Tense
        ```
        Return last element in a `seq` (sequence) which satisfies `condition`. If none found, returned is default \\
        value defined via parameter `default`, which by default has value `None`. On 0.3.27a4 removed this parameter, \\
        it has been restored on 0.3.34
        """
        if not _is_condition_callback(condition) and not self.isNone(condition):
            error = TypeError("expected 'condition' parameter to be a callable or 'None'")
            raise error
        
        _seq = list(i)
        
        for _i in self.abroadNegative(1, _seq):
            
            if condition is not None and condition(_seq[_i]):
                return _seq[_i]
            
            else:
                if _seq[_i]: return _seq[_i]
                
        return default
    
    # OVERLOAD 0.3.34
    @classmethod
    @_tc.overload
    def any(self, i: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]], /, condition: None = None) -> bool: ...
    
    @classmethod
    @_tc.overload
    def any(self, i: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]], /, condition: _cal[[_T], bool]) -> bool: ...
    
    @classmethod
    def any(self, i, /, condition = None):
        """
        \\@since 0.3.26rc2
        ```
        "class method" in class Tense
        ```
        Equivalent to `any()` in-built function, but this method returns list of items, which satisfied `condition`, \\
        which has default value `None`. If none found, returned is empty list.
        Change 0.3.34: `any()` now returns boolean rather than shallow copy of sequence
        """
        if not _is_condition_callback(condition) and not self.isNone(condition):
            error = TypeError("expected 'condition' parameter to be a callable or 'None'. if it is callable, only one argument may be passed")
            raise error
        
        for e in list(i):
            
            # for better results consider using function/method that returns a boolean value
            if (condition is not None and condition(e)) or (condition is None and bool(e)):
                return True
            
        return False
            
    @classmethod
    @_tc.overload
    def all(self, i: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]], /, condition: None = None) -> bool: ...
    
    @classmethod
    @_tc.overload
    def all(self, i: _uni[_tc.Sequence[_T], _tc.Uniqual[_T]], /, condition: _cal[[_T], bool]) -> bool: ...
    
    @classmethod
    def all(self, i, /, condition = None): # slash was after 'condition' parameter before (0.3.34)
        """
        \\@since 0.3.26rc2
        ```
        "class method" in class Tense
        ```
        Change 0.3.36: if condition was a callable, it must return boolean value, otherwise will always return `False`
        Change 0.3.34: `all()` now returns boolean rather than shallow copy of sequence
        Change 0.3.27a4: removed parameter `default`.
        """
        if not _is_condition_callback(condition) and not self.isNone(condition):
            error = TypeError("expected 'condition' parameter to be a callable or 'None'. if it is callable, only one argument may be passed")
            raise error
        
        _placeholder = True
        
        for e in list(i):
            
            if condition is not None:
                
                # 0.3.36
                if self.isBool(condition(e)):
                    _placeholder = _placeholder and condition(e)
                    
                else:
                    return False
                
            else:
                _placeholder = _placeholder and bool(e)
        
        return _placeholder
    
    @classmethod
    def probability2(self, x: _T = 1, y: _T = 0, frequency = 1, length: _ProbabilityLengthType = 10000):
        """
        \\@since 0.3.8 (standard since 0.3.9) \\
        \\@lifetime ≥ 0.3.8; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.26a3, 0.3.26rc1, 0.3.31 \\
        https://aveyzan.glitch.me/tense/py/method.probability.html#2
        ```ts
        "class method" in class Tense
        ``` \n
        ``` \n
        # syntax since 0.3.25
        def probability2(x = 1, y = 0, frequency = 1, length = 10000): ...
        # syntax for 0.3.19 - 0.3.23; on 0.3.19 renamed from probability()
        def probability2(rareValue = 1, usualValue = 0, frequency = 1, length = 10000): ...
        # syntax before 0.3.19
        def probability(value = 1, frequency = 1, length = 10000): ...
        ```
        Randomize a value using probability `frequency/length` applied on parameter `x`. \\
        Probability for parameter `y` will be equal `(length - frequency)/length`. \\
        Default values:
        - for `x`: 1
        - for `y`: 0
        - for `frequency`: 1
        - for `length`: 10000 (since 0.3.26a3 `length` can also have value `-1`)

        To be more explanatory, `x` has `1/10000` chance to be returned by default (in percents: 0.01%), \\
        meanwhile the rest chance goes to `y` (`9999/10000`, 99.99%), hence `y` will be returned more \\
        frequently than `x`. Exceptions:
        - for `frequency` equal 0 or `x` equal `y`, returned is `y`
        - for `frequency` greater than (or since 0.3.25 equal) `length` returned is `x`
        """
        
        # due to swap from IntegerEnum to Enum in _ProbabilityLength class's subclass
        # it had to be replaced
        _length = 10000 if length in (-1, self.PROBABILITY_COMPUTE) else length
        _frequency = frequency
        
        # 0.3.33: refraining from using string literals, since they will need to be manually changed
        # once parameter names are changed
        # note that 'return' keyword is reserved for return annotation with '->' operator
        _params = _get_all_params(self.probability2) # 0.3.36: missing 2 after 'probability'
        _options = [k for k in TenseOptions.__dict__ if k[:1] != "_"]
            
        if not self.isInteger(_frequency):
            error = TypeError("expected an integer in parameter '{}'".format(_params[2]))
            raise error
        
        elif _frequency < 0:
            error = ValueError("expected a non-negative integer in parameter '{}'".format(_params[2]))
            raise error
        
        # types must match, otherwise you can meet an union-typed result, which is not useful during
        # type inspection, since you need to append appropriate 'if' statement!
        # exception: a function result being a union-typed one
        if not self.isList([x, y], type(x)):
            error = TypeError("provided types in parameters '{}' and '{}' do not match".format(_params[0], _params[1]))
            raise error
        
        if not self.isInteger(length) and length != self.PROBABILITY_COMPUTE:
            error = TypeError("expected an integer or constant '{}' in parameter '{}'".format("PROBABILITY_" + self.PROBABILITY_COMPUTE.name, _params[3]))
            raise error
        
        elif _length == 0:
            error = ZeroDivisionError("expected integer value from -1 or above in parameter '{}', but not equal zero".format(_params[3]))
            raise error
        
        elif _length > _sys.maxsize and not TenseOptions.disableProbability2LengthLimit:
            error = ValueError("integer value passed to parameter '{}' is too high, expected value below or equal {}. If you want to remove this error, toggle on option '{}'".format(
                _params[3], _sys.maxsize, "{}.{}".format(TenseOptions.__name__, _options[2])
            ))
            raise error
        
        elif _length < -1:
            error = ValueError("parameter '{}' may not have a negative integer value".format(_params[3]))
            raise error
        
        # these statements are according to probability math definition
        # once 'x' and 'y' are the same, there is no reason to activate loop at all
        if x == y or _frequency == 0:
            return y
        
        if _frequency >= _length:
            return x
        
        if TenseOptions.disableProbability2LengthLimit:
            
            # 0.3.33: change in _frequency (removed minus one) so that result will be
            # displayed correctly
            r = self.random(1, _length)
            return x if self.isInRange(r, 1, _frequency) else y
            
        else:
            # type of list will be deduced anyway, so there annotation may be skipped
            # 0.3.31: shortened code, reduced due to usage of list comprehension
            a = [y for _ in abroad(_length - _frequency)] + [x for _ in abroad(_length - _frequency, _length)]
            return self.pick(a)
        
    if _cl.VERSION_INFO >= (0, 3, 78) and False:
        
        def probability_temporary_to_be_applied(self, *vf: _ProbabilityType[_T], length: _ProbabilityLengthType = PROBABILITY_COMPUTE):
            
            _params = _get_all_params(self.probability)
            _length = -1 if length == self.PROBABILITY_COMPUTE else length
            
            if reckon(vf) == 1:
                
                e = vf[0]
                
                if isinstance(e, _tc.Mapping) and reckon(e) == 2:
                    
                    _keys = [k for k in e]
                    _values = [e[k] for k in e]
                    
                    if self.all(_values, lambda x: self.isNone(x) or self.isEllipsis(x)):
                        
                        return self.probability2(e[_keys[0]], e[_keys[1]], length = _length)
                        
                    return self.probability2(e[_keys[0]], e[_keys[1]], ) 
            
            elif reckon(vf) == 2:
                
                e1, e2 = (vf[0], vf[1])
                
                if (
                    (isinstance(e1, (_tc.Sequence, _tc.Uniqual)) and isinstance(e2, (_tc.Sequence, _tc.Uniqual))) or
                    (isinstance(e1, _tc.Mapping) and reckon(e1) == 1) and (isinstance(e2, _tc.Mapping) and reckon(e2) == 1) 
                ): ...
    
    @classmethod
    def probability(self, *vf: _ProbabilityTypeTmp[int], length: _ProbabilityLengthType = PROBABILITY_COMPUTE):
        """
        \\@since 0.3.8 (standard since 0.3.9) \\
        \\@lifetime ≥ 0.3.8 \\
        \\@modified 0.3.19, 0.3.24, 0.3.25, 0.3.26a3, 0.3.26b3, 0.3.26rc1, 0.3.26rc2, 0.3.31 \\
        https://aveyzan.glitch.me/tense/py/method.probability.html
        ```ts
        "class method" in class Tense
        ``` \n
        ``` \n
        # since 0.3.25
        def probability(*vf: int | list[int] | tuple[int, int | None] | dict[int, int | None] | deque[int], length: int = PROBABILITY_COMPUTE): ...

        # for 0.3.24
        def probability(*valuesAndFrequencies: int | list[int] | tuple[int] | dict[int, int | None], length: int = PROBABILITY_ALL): ...

        # during 0.3.19 - 0.3.23; on 0.3.19 renamed
        def probability(*valuesAndFrequencies: int | list[int] | tuple[int], length: int = -1): ...

        # during 0.3.8 - 0.3.18
        def complexity(values: list[_T] | tuple[_T], frequencies: int | list[int] | tuple[int], length: int = 10000): ...
        ```
        Extended version of `Tense.probability2()` method. Instead of only 2 values user can put more than 2. \\
        Nevertheless, comparing to the same method, it accepts integers only.

        *Parameters*:

        - `vf` - this parameter waits at least for 3 values (before 0.3.26a3), for 2 values you need to use `Tense.probability2()` method \\
        instead, because inner code catches unexpected exception `ZeroDivisionError`. For version 0.3.25 this parameter accepts: 
        - integers
        - integer lists of size 1-2
        - integer tuples of size 1-2
        - integer deques of size 1-2
        - integer key-integer/`None`/`...` value dicts
        - integer sets and frozensets of size 1-2 both

        - `length` (Optional) - integer which has to be a denominator in probability fraction. Defaults to `-1`, what means this \\
        number is determined by `vf` passed values (simple integer is plus 1, dicts - plus value or 1 if it is `None` or ellipsis, \\
        sequence - 2nd item; if `None`, then plus 1). Since 0.3.26b3 put another restriction: length must be least than or equal \\
        `sys.maxsize`, which can be either equal 2\\*\\*31 - 1 (2,147,483,647) or 2\\*\\*63 - 1 (9,223,372,036,854,775,807)
        """
        # explanation:
        # a1 is final list, which will be used to return the integer
        # a2 is temporary list, which will store all single integers, without provided "frequency" value (item 2)
        a1, a2 = [[0] for _ in abroad(2)]
        self.clear(a1, a2)

        # c1 sums all instances of single numbers, and with provided "frequency" - plus it
        # c2 is substraction of length and c1
        # c3 has same purpose as c1, but counts only items without "frequency" (second) item
        # c4 is last variable, which is used as last from all of these - counts the modulo of c2 and c3 (but last one minus 1 as well)
        # c5 gets value from rearmost iteration 
        c1, c2, c3, c4, c5 = [0 for _ in abroad(5)]
        
        # 0.3.33: refraining from using string literals, since they will need to be manually changed
        # once parameter names are changed
        # note that 'return' keyword is reserved for return annotation with '->' operator
        _params = _get_all_params(self.probability)
        
        if not self.isInteger(length) and length != self.PROBABILITY_COMPUTE:
            error = TypeError("expected integer or constant '{}' in parameter '{}'".format("PROBABILITY_" + self.PROBABILITY_COMPUTE.name, _params[1]))
            raise error
        
        _length = -1 if length == self.PROBABILITY_COMPUTE else length
        
        # length checking before factual probability procedure
        if _length < -1:
            error = ValueError("expected integer value from -1 or above in parameter '{}'".format(_params[1]))
            raise error
        
        elif _length == 0:
            error = ZeroDivisionError("expected integer value from -1 or above in parameter '{}', but not equal zero".format(_params[1]))
            raise error
        
        # 0.3.26b3: cannot be greater than sys.maxsize
        # 0.3.33: update of this statement (added the 'or' keyword with expression as right operand)
        elif _length > _sys.maxsize or (_length > _sys.maxsize and reckon(vf) == 2 and not TenseOptions.disableProbability2LengthLimit):
            error = ValueError("integer value passed to parameter '{}' is too high, expected value below or equal {}".format(_params[1], _sys.maxsize))
            raise error
        
        # START 0.3.26a3
        if reckon(vf) == 2:
            
            # alias to elements
            e1, e2 = (vf[0], vf[1])
            
            if self.isInteger(e1):
                
                if self.isInteger(e2):
                    
                    # 0.3.33: 'length = _length' instead of 'length = 2'
                    return self.probability2(e1, e2, length = _length)
                
                # 0.3.33: _ProbabilitySeq type alias to deputize (_ProbabilitySeqNoDict, dict) tuple
                # during type checking
                elif isinstance(e2, _ProbabilitySeq):
                    
                    if isinstance(e2, _ProbabilitySeqNoDict):
                    
                        if reckon(e2) in (1, 2):
                            
                            _tmp = e2[0] if reckon(e2) == 1 else (e2[0], e2[1])
                            
                            if self.isInteger(_tmp):
                                
                                # 0.3.33: 'length = _length' instead of 'length = 2'
                                return self.probability2(e1, _tmp, length = _length)
                            
                            # notable information: this duo of tuple items are, respectively:
                            # 'value' and 'frequency'
                            elif self.isTuple(_tmp):
                                
                                _v, _f = (_tmp[0], _tmp[1])
                                
                                if not self.isInteger(_v):
                                    error = TypeError("first item in an iterable is not an integer")
                                    raise error
                                
                                if not (self.isInteger(_f) or self.isEllipsis(_f) or self.isNone(_f)):
                                    error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                    raise error
                                
                                if self.isNone(_f) or self.isEllipsis(_f):
                                    return self.probability2(e1, _v, length = _length)
                                
                                elif _f < 1: # probability fraction cannot be negative
                                    error = ValueError("second item in an iterable is negative or equal zero")
                                    raise error
                                
                                return self.probability2(e1, _v, frequency = _f, length = _length)
                            
                            else:
                                error = RuntimeError("internal error")
                                raise error
                            
                        else:
                            error = IndexError("length of every iterable may have length 1-2 only")
                            raise error
                        
                    elif self.isDict(e2):
                        
                        if reckon(e2) != 1:
                            error = ValueError("expected one pair in a dictonary, received {}".format(reckon(e2)))
                            raise error
                        
                        # 0.3.33: removed loop, replacing it with inbuilt dictionary methods
                        _v, _f = (self.toList(e2.keys())[0], self.toList(e2.values())[0])
                        
                        if self.isNone(_f) or self.isEllipsis(_f):
                            return self.probability2(e1, _v, length = _length)
                        
                        elif _f < 1:
                            error = ValueError("value in a dictionary is negative or equal zero")
                            raise error
                            
                        return self.probability2(e1, _v, frequency = _f, length = _length)
                    
                    else:
                        error = TypeError("unsupported type in second item of variable parameter '{}', expected an integer, iterable with 1-2 items (first item being integer), or dictionary with one pair (key being integer)".format(_params[0]))
                        raise error
            
            # 0.3.33: _ProbabilitySeq type alias to deputize (_ProbabilitySeqNoDict, dict) tuple
            # during type checking
            elif isinstance(e1, _ProbabilitySeq):
                
                if self.isInteger(e2):
                
                    if isinstance(e1, _ProbabilitySeqNoDict):
                        
                        if reckon(e1) in (1, 2):
                            
                            _tmp = e1[0] if reckon(e1) == 1 else (e1[0], e1[1])
                            
                            if self.isInteger(_tmp):
                                
                                # 0.3.33: 'length = _length' instead of 'length = 2'
                                # + 'e2' and '_tmp' are placed vice versa
                                return self.probability2(_tmp, e2, length = _length)
                            
                            elif self.isTuple(_tmp):
                                
                                _v, _f = (_tmp[0], _tmp[1])
                                
                                if not self.isInteger(_v):
                                    error = TypeError("first item in an iterable is not an integer")
                                    raise error
                                
                                if not (self.isInteger(_f) or self.isEllipsis(_f) or self.isNone(_f)):
                                    error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                    raise error
                                
                                if self.isNone(_f) or self.isEllipsis(_f):
                                    return self.probability2(_v, e2, length = _length)
                                
                                elif _f < 1: # probability fraction cannot be negative
                                    error = ValueError(f"second item in an iterable is negative or equal zero")
                                    raise error
                                
                                return self.probability2(_v, e2, frequency = _f, length = _length)
                            
                            else:
                                error = RuntimeError("internal error")
                                raise error
                            
                        else:
                            error = IndexError("length of every iterable may have length 1-2 only")
                            raise error
                    
                    elif self.isDict(e1):
                        
                        if reckon(e1) != 1:
                            error = ValueError("expected only one pair in a dictonary, received {}".format(reckon(e1)))
                            raise error
                        
                        # 0.3.33: removed loop, replacing it with inbuilt dictionary methods
                        _v, _f = (self.toList(e1.keys())[0], self.toList(e1.values())[0])
                        
                        if self.isNone(_f) or self.isEllipsis(_f):
                            
                            # 0.3.33: '_v' and 'e2' vice versa
                            return self.probability2(_v, e2, length = _length)
                        
                        elif _f < 1:
                            error = ValueError("value in a dictionary is negative or equal zero")
                            raise error
                        
                        # 0.3.33: '_v' and 'e2' vice versa
                        return self.probability2(_v, e2, frequency = _f, length = _length)
                
                # 0.3.33: _ProbabilitySeq type alias to deputize (_ProbabilitySeqNoDict, dict) tuple
                # during type checking
                elif isinstance(e2, _ProbabilitySeq):
                    
                    if isinstance(e1, _ProbabilitySeqNoDict):
                    
                        if isinstance(e2, _ProbabilitySeqNoDict):
                            
                            if reckon(e1) == 1:
                                
                                if reckon(e2) == 1:
                                    
                                    _1, _2 = (e1[0], e2[0])
                                    
                                    if not self.isInteger(_1) or not self.isInteger(_2):
                                        error = TypeError("first item in an iterable is not an integer")
                                        raise error
                                    
                                    return self.probability2(_1, _2, length = _length)
                                
                                elif reckon(e2) == 2:
                                    
                                    _1, _2_1, _2_2 = (e1[0], e2[0], e2[1])
                                    
                                    if not self.isInteger(_1) or not self.isInteger(_2_1):
                                        error = TypeError("first item in an iterable is not an integer")
                                        raise error
                                    
                                    if not self.isEllipsis(_2_2) and not self.isInteger(_2_2) and not self.isNone(_2_2):
                                        error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                        raise error
                                    
                                    if self.isNone(_2_2) or self.isEllipsis(_2_2):
                                        
                                        return self.probability2(_1, _2_1, length = _length)
                                    
                                    return self.probability2(_1, _2_1, frequency = _2_2, length = _length)
                                
                                else:
                                    error = IndexError("length of every iterable may have length 1-2 only")
                                    raise error
                            
                        elif reckon(e1) == 2:
                            
                            if reckon(e2) == 1:
                                
                                _1_1, _1_2, _2 = (e1[0], e1[1], e2[0])
                                
                                if not self.isInteger(_1_1) or not self.isInteger(_2):
                                    error = TypeError("first item in an iterable is not an integer")
                                    raise error
                                
                                if not self.isEllipsis(_1_2) and not self.isInteger(_1_2) and self.isNone(_1_2):
                                    error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                    raise error
                                
                                if self.isNone(_1_2) or self.isEllipsis(_1_2):
                                    
                                    return self.probability2(_1_1, _2, length = _length)
                                
                                return self.probability2(_1_1, _2, frequency = _length - _1_2, length = _length)
                            
                            elif reckon(e2) == 2:
                                
                                _1_1, _1_2, _2_1, _2_2 = (e1[0], e1[1], e2[0], e2[1])
                                
                                if not self.isInteger(_1_1) or not self.isInteger(_2_1):
                                    error = TypeError("first item in an iterable is not an integer")
                                    raise error
                                
                                if (
                                    not self.isEllipsis(_1_2) and not self.isInteger(_1_2) and self.isNone(_1_2)) or (
                                    not self.isEllipsis(_2_2) and not self.isInteger(_2_2) and self.isNone(_2_2)
                                ):
                                    error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                    raise error
                                
                                if self.isNone(_1_2) or self.isEllipsis(_1_2):
                                    
                                    if self.isNone(_2_2) or self.isEllipsis(_2_2):
                                        return self.probability2(_1_1, _2_1, length = _length)
                                    
                                    else:
                                        return self.probability2(_1_1, _2_1, frequency = _length - _2_2, length = _length)
                                    
                                elif self.isInteger(_1_2):
                                    
                                    if self.isNone(_2_2) or self.isEllipsis(_2_2):
                                        return self.probability2(_1_1, _2_1, frequency = _1_2, length = _length)
                                    
                                    else:
                                        return self.probability2(_1_1, _2_1, frequency = _1_2, length = _length if _length > _1_2 + _2_2 else _1_2 + _2_2)
                                    
                                else:
                                    error = RuntimeError("internal error")
                                    raise error
                                    
                            else:
                                error = IndexError("length of every iterable may have length 1-2 only")
                                raise error
                            
                        else:
                            error = IndexError("length of every iterable may have length 1-2 only")
                            raise error
                    
                    elif self.isDict(e1):
                        
                        if reckon(e1) != 1:
                            error = ValueError("expected only one pair in a dictonary, received {}".format(reckon(e1)))
                            raise error
                        
                        # 0.3.33: removed loop, replacing it with inbuilt dictionary methods
                        _v, _f = (self.toList(e1.keys())[0], self.toList(e1.values())[0])
                        
                        if isinstance(e2, _ProbabilitySeqNoDict):
                            
                            if self.isNone(_f) or self.isEllipsis(_f):
                                
                                if reckon(e2) in (1, 2):
                                    
                                    _tmp = e2[0] if reckon(e2) == 1 else (e2[0], e2[1])
                            
                                    if self.isInteger(_tmp):
                                        
                                        return self.probability2(_v, _tmp, length = _length)
                                    
                                    elif self.isTuple(_tmp):
                                        
                                        # avoid name collision
                                        _v2, _f2 = (_tmp[0], _tmp[1])
                                        
                                        if not self.isInteger(_v2):
                                            error = TypeError("first item in an iterable is not an integer")
                                            raise error
                                        
                                        if not (self.isInteger(_f2) or self.isEllipsis(_f2) or self.isNone(_f2)):
                                            error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                            raise error
                                        
                                        if self.isNone(_f2) or self.isEllipsis(_f2):
                                            return self.probability2(_v, _v2, length = _length)
                                        
                                        elif _f2 < 1:
                                            error = ValueError("second item in an iterable is negative or equal zero")
                                            raise error
                                        
                                        return self.probability2(_v, _v2, frequency = _length - _f2, length = _length)
                            
                                    else:
                                        error = RuntimeError("internal error")
                                        raise error
                                
                                else:
                                    error = IndexError("length of every iterable may have length 1-2 only")
                                    raise error
                            
                            elif _f < 1:
                                error = ValueError("value in a dictionary is negative or equal zero")
                                raise error
                            
                            if reckon(e2) in (1, 2):
                                    
                                _tmp = e2[0] if reckon(e2) == 1 else (e2[0], e2[1])
                        
                                if self.isInteger(_tmp):
                                    
                                    return self.probability2(_v, _tmp, length = _length)
                                
                                elif self.isTuple(_tmp):
                                    
                                    # avoid name collision
                                    _v2, _f2 = (_tmp[0], _tmp[1])
                                    
                                    if not self.isInteger(_v2):
                                        error = TypeError("first item in an iterable is not an integer")
                                        raise error
                                    
                                    if not (self.isInteger(_f2) or self.isEllipsis(_f2) or self.isNone(_f2)):
                                        error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                        raise error
                                    
                                    if self.isNone(_f2) or self.isEllipsis(_f2):
                                        return self.probability2(_v, _v2, length = _length)
                                    
                                    elif _f2 < 1:
                                        error = ValueError("second item in an iterable is negative or equal zero")
                                        raise error
                                    
                                    return self.probability2(_v, _v2, frequency = _length - _f2, length = _length)
                                
                                else:
                                    error = RuntimeError("internal error")
                                    raise error
                            
                            else:
                                error = IndexError("length of every iterable may have length 1-2 only")
                                raise error
                                
                        elif self.isDict(e2):
                            
                            if reckon(e2) != 1:
                                error = ValueError("expected only one pair in a dictonary, received {}".format(reckon(e1)))
                                raise error
                            
                            _v2, _f2 = (self.toList(e2.keys())[0], self.toList(e2.values())[0])
                            
                            if self.isNone(_f) or self.isEllipsis(_f):
                                
                                if self.isNone(_f2) or self.isEllipsis(_f2):
                                    
                                    return self.probability2(_v, _v2, length = _length)
                                
                                elif _f2 < 1:
                                    error = ValueError("value in a dictionary is negative or equal zero")
                                    raise error
                                
                                return self.probability2(_v, _v2, frequency = _length - _f2, length = _length)
                            
                            elif _f < 1:
                                error = ValueError("value in a dictionary is negative or equal zero")
                                raise error
                            
                            return self.probability2(_v, _v2, frequency = _f, length = _length if _length > _f + _f2 else _f + _f2)
                            
                        else:
                            error = TypeError("unsupported type in second item of variable parameter '{}', expected an integer, iterable with 1-2 items (first item being integer), or dictionary with one pair (key being integer)".format(_params[0]))
                            raise error
                    else:
                        error = TypeError("unsupported type in first item of variable parameter '{}', expected an integer, iterable with 1-2 items (first item being integer), or dictionary with one pair (key being integer)".format(_params[0]))
                        raise error
                else:
                    error = TypeError("unsupported type in first item of variable parameter '{}', expected an integer, iterable with 1-2 items (first item being integer), or dictionary with one pair (key being integer)".format(_params[0]))
                    raise error
            else:
                error = TypeError("unsupported type in first item of variable parameter '{}', expected an integer, iterable with 1-2 items (first item being integer), or dictionary with one pair (key being integer)".format(_params[0]))
                raise error         
                    
        # END 0.3.26a3
        
        elif reckon(vf) < 2:
            
            error = _tc.MissingValueError("expected at least 2 items in variable parameter '{}', received {}".format(_params[0], reckon(vf)))
            raise error
        
        # reading all items provided
        for e in vf:
            
            # value is an integer (that means it cannot have "frequency"),
            # which is "value" parameter equivalent
            if self.isInteger(e):
                a1.append(e)
                a2.append(e)
                c1 += 1
                c3 += 1
                
            elif isinstance(e, _ProbabilitySeqNoDict):
                # we have only one item, and that item is "value"
                # 0.3.25 (additional statement for tuple and overall)
                if reckon(e) == 1:
                    
                    if not self.isInteger(e[0]):
                        error = TypeError("every iterable may have integer as first item")
                        raise error
                    
                    a1.append(e[0])
                    a2.append(e[0])
                    c1 += 1
                    c3 += 1
                    
                # those are, respectively, "value" and "frequency"
                elif reckon(e) == 2:
                    
                    if not self.isInteger(e[0]):
                        error = TypeError("every iterable may have integer as first item")
                        raise error
                    
                    if not (self.isInteger(e[1]) or self.isEllipsis(e[1]) or self.isNone(e[1])):
                        error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                        raise error
                    
                    if self.isEllipsis(e[1]) or self.isNone(e[1]):
                        a1.append(e[0])
                        a2.append(e[0])
                        c1 += 1
                        c3 += 1
                    
                    elif e[1] < 1:
                        error = ValueError("second item in an iterable is a negative integer")
                        raise error
                    
                    a1.extend([e[0] for _ in abroad(e[1])])
                    c1 += int(e[1])
                    
                # if thought that the length is third item, that is wrong presupposition
                else:
                    error = IndexError("length of every iterable may have length 1-2 only")
                    raise error
                
            # 0.3.24 (dict support)
            elif self.isDict(e):
                
                if reckon(e) == 0:
                   error = ValueError("Expected at least one pair in every dictonary, received {}".format(reckon(e)))
                   raise error
               
                for f in e:
                    
                    if not self.isInteger(f):
                        error = KeyError(f"One of keys in dictionaries is not an integer. Ensure every key is of type 'int'. Error thrown by item: '{f}'")
                        raise error
                    
                    if not (self.isInteger(e[f]) or self.isEllipsis(e[f]) or self.isNone(e[f])):
                        error = ValueError(f"One of values in dictionaries is neither an integer, 'None', nor an ellipsis. Ensure every values satisfies this requirement. Error thrown by item: '{f}'")
                        raise error
                    
                    if e[f] < 1:
                        error = ValueError(f"One of values in dictionaries is negative integer or equal zero. Ensure every value is positive integer. Error thrown by item: '{e[f]}'")
                        raise error
                    
                    elif self.isEllipsis(e[f]) or self.isNone(e[f]):
                        a1.append(f)
                        a2.append(f)
                        c1 += 1
                        c3 += 1
                        
                    else:
                        a1.extend([f for _ in abroad(e[f])])
                        c1 += 1
                        
            # incorrect type defined
            else:
                error = TypeError("unsupported type in an item of variable parameter '{}', expected an integer, iterable with 1-2 items (first item being integer), or dictionary with one pair (key being integer)".format(_params[0]))
                raise error   
            
        # length minus times when single integers are provided is needed
        # to continue extended probability
        if length == self.PROBABILITY_COMPUTE:
            c2 = c1
            
        else:
            c2 = _length - c1
        
        # hint: if not that minus one, last item will be also included
        # and we want the modulo just for the last item
        if c3 > 1: c3 -= 1
        
        # that instruction shouldn't be complicated
        # also, it is impossible to get into here, since
        # most values do not have "frequency" (aka 2nd item)
        if c2 != c1 and c2 > _length:
            tmp = [0]
            tmp.clear()
            tmp.extend([a1[i] for i in abroad(_length)])
            a1 = tmp
            del tmp
            
        # look in here: used is abroad() method, but before the valid
        # loop, all items of temporary variable will become positive
        elif c2 == c1 or (c2 != c1 and c2 < _length):
            
            for i in abroad(c2):
                
                # there we are looking for the highest number, which will
                # be divisible by number of integers passed to "vf" parameter
                if i % c3 == 0:
                    c5 = i
                    break
            # this loop is nested as we use to repeat all items from a2 list
            for i in abroad(a2):
                a1.extend([a2[i] for _ in abroad(c5 / c3)])
                    
            # modulo will be used merely there (0.3.35 patch there)
            try:
                c4 = c2 % c3
                
            except ZeroDivisionError:
                c4 = 0
            
            # that one will be always done (more likely)
            # only indicated whether result in more than zero
            if c4 > 0:
                a1.extend([a2[reckon(a2) - 1] for _ in abroad(c4)])

        # code with following 'if False' below: as a general warning, you would use Tense.architecture()
        # to find your system's architecture, because it determines about value of sys.maxsize, which is
        # max size for all sequences not entirely sure, if creating 2d sequences to increase 'length'
        # parameter value is a good idea. scrap code below is projected
        if False:
            a3 = [[0]]
            a3.clear()
            _2d_i = 0
            while _2d_i < sys.maxsize:
                for _ in abroad(sys.maxsize):
                    a3[_2d_i].append(self.pick(a1))
                _2d_i += 1
            return self.pick(self.pick(a3))
        
        return self.pick(a1) # this will be returned
    
    @classmethod
    def until(self, desiredString: _tc.StringUnion[_tc.Sequence[str]], /, message: _opt[str] = None, caseInsensitive: bool = True):
        """
        \\@since 0.3.25
        ```ts
        "class method" in class Tense
        ```
        Console method, which will repeat the program until user won't \\
        write correct string. Case is insensitive, may be configured via \\
        optional parameter `caseInsensitive`, which by default has \\
        value `True`. Returned is reference to this class.
        
        0.3.35 - Patch in first parameter `desiredString`
        """
        s = ""
        c = False
        
        if not isinstance(desiredString, (str, _tc.Sequence)) or (isinstance(desiredString, _tc.Sequence) and not self.isString(desiredString) and not self.isList(list(desiredString), str)):
            
            error = ValueError("expected a string or string sequence")
            raise error
        
        while c:
            
            s = input(message if message is not None and message != "" else "")
            c = s.lower() != desiredString.lower() if self.isString(desiredString) else s.lower() not in (_s.lower() for _s in desiredString)
            
            if not caseInsensitive:
                c = s != desiredString if self.isString(desiredString) else s not in desiredString
                
        return self
    
    @classmethod
    def sleep(self, seconds: float, /):
        """
        \\@since 0.3.25
        ```ts
        "class method" in class Tense
        ```
        Define an execution delay, which can be a floating-point number \\
        with 2 fractional digits. Returned is reference to this class.
        """
        _time.sleep(seconds)
        return self
    
    @classmethod
    def repeat(self, value: _T, times: _opt[int] = None, /): # 0.3.31: default value 'None'
        """
        \\@since 0.3.25 `itertools.repeat`
        ```ts
        "class method" in class Tense
        ```
        Returns list with `value` repeated `times` times. \\
        Equals `itertools.repeat()` (0.3.31).
        """
        
        return _itertools.repeat(value, times) if not self.isNone(times) else _itertools.repeat(value)
    
    
    @classmethod
    def cycle(self, i: _tc.Iterable[_T], /):
        """
        \\@since 0.3.34 `itertools.cycle`
        """
        return _itertools.cycle(i)
    
    
    count = _itertools.count # not subscriptable, what would explain overloads
    """\\@since 0.3.34"""
    
    groupby = _itertools.groupby # not subscriptiable, what would explain overloads
    """\\@since 0.3.35"""
    
    @classmethod
    def starmap(self, f: _cal[..., _T], i: _tc.Iterable[_tc.Iterable[_Any]], /):
        """
        \\@since 0.3.35 `itertools.starmap`
        """
        return _itertools.starmap(f, i)
    
    __all__ = [n for n in locals() if n[:1] != "_"]
    "\\@since 0.3.26rc2"
    
    __dir__ = [n for n in locals() if n[:1] != "_"]
    "\\@since 0.3.26rc2"
    
tense = Tense
TenseType = type(Tense())
TenseInstance = Tense()
"\\@since 0.3.27a5. Instance of `Tense` to use for `>>` and `<<` operators especially"

class RGB(_util.Final):
    """
    \\@since 0.3.28
    
    ```
    class RGB: ...
    from tense import RGB
    ```
    
    Auxiliary class for `Color` class. Represents red-green-blue color representation.
    """
    def __init__(self, red = 0, green = 0, blue = 0, /):
        
        _parameters = {
            "red": red,
            "green": green,
            "blue": blue
        }
        
        for key in _parameters:
            
            if not Tense.isInteger(_parameters[key]) or (Tense.isInteger(_parameters[key]) and _parameters[key] not in abroad(0x100)):
                error = TypeError("expected a non-negative integer in parameter '{}' in range 0-255".format(key))
                raise error
            
        self.__rgb = (red, green, blue)
        
    def __str__(self):
        """
        \\@since 0.3.28
        """
        return "{}({})".format(type(self).__name__, ", ".join([str(e) for e in self.__rgb]))
        
    def __repr__(self):
        """
        \\@since 0.3.28
        """
        return "<{}.{} object: {}>".format(self.__module__, type(self).__name__, self.__str__())
    
    def __hex__(self):
        """
        \\@since 0.3.28
        
        Provides conversion to hexadecimal format
        """
        _r = hex(self.__rgb[0])[2:] if self.__rgb[0] >= 0x10 else "0" + hex(self.__rgb[0])[2:]
        _g = hex(self.__rgb[1])[2:] if self.__rgb[1] >= 0x10 else "0" + hex(self.__rgb[1])[2:]
        _b = hex(self.__rgb[2])[2:] if self.__rgb[2] >= 0x10 else "0" + hex(self.__rgb[2])[2:]
        return "0x" + _r + _g + _b
    
    def __int__(self):
        """
        \\@since 0.3.28
        
        Converts RGB tuple into its corresponding integer representation
        """
        return int(self.__hex__()[2:], base = 16)
    
    # little deviation from type hinting in methods below
    # read document strings to figure it out
    def __lt__(self, other):
        """
        \\@since 0.3.28
        
        To return true, following conditions must be satisfied:
        - `int(self) < int(other)`
        - `other` must be instance of `RGB` class
        """
        return self.__int__() < other.__int__() if type(other) is type(self) else False
    
    def __gt__(self, other):
        """
        \\@since 0.3.28
        
        To return true, following conditions must be satisfied:
        - `int(self) > int(other)`
        - `other` must be instance of `RGB` class
        """
        return self.__int__() > other.__int__() if type(other) is type(self) else False
    
    def __eq__(self, other):
        """
        \\@since 0.3.28
        
        To return true, following conditions must be satisfied:
        - `int(self) == int(other)`
        - `other` must be instance of `RGB` class
        """
        return self.__int__() == other.__int__() if type(other) is type(self) else False
    
    def __le__(self, other):
        """
        \\@since 0.3.28
        
        To return true, following conditions must be satisfied:
        - `int(self) <= int(other)`
        - `other` must be instance of `RGB` class
        """
        return self.__int__() <= other.__int__() if type(other) is type(self) else False
    
    def __ge__(self, other):
        """
        \\@since 0.3.28
        
        To return true, following conditions must be satisfied:
        - `int(self) >= int(other)`
        - `other` must be instance of `RGB` class
        """
        return self.__int__() >= other.__int__() if type(other) is type(self) else False
    
    def __ne__(self, other):
        """
        \\@since 0.3.28
        
        To return true, following conditions must be satisfied:
        - `int(self) != int(other)`
        - `other` must be instance of `RGB` class
        """
        return self.__int__() != other.__int__() if type(other) is type(self) else False
    
    def __pos__(self):
        """
        \\@since 0.3.28
        
        Returns a RGB tuple
        """
        return self.__rgb
    
    def __neg__(self):
        """
        \\@since 0.3.28
        
        Returns a RGB tuple
        """
        return self.__rgb
    
    def __invert__(self):
        """
        \\@since 0.3.28
        
        Returns a RGB tuple
        """
        return self.__rgb
    
    @_util.finalproperty
    def hex(self):
        """
        \\@since 0.3.38
        
        Provides conversion to hexadecimal format
        """
        return self.__hex__()
    
    @_util.finalproperty
    def tuple(self):
        """
        \\@since 0.3.38
        
        Returns a RGB tuple
        """
        return self.__rgb
    
    @staticmethod
    def fromValue(n: _uni[int, str], /):
        """
        \\@since 0.3.36
        
        Returns a new `RGB` class object using specific integer or string value. \\
        If string was provided, it must contain a valid number in either hexadecimal, \\
        decimal, octal or binary notation.
        
        Updated 0.3.37, 0.3.38, 0.3.39
        """
        
        if (Tense.isInteger(n) and n in abroad(_cp.RGB_MAX + 1)) or (Tense.isString(n) and ((_is_hexadecimal(n) or _is_decimal(n) or _is_octal(n) or _is_binary(n)) and _int_conversion(n) in abroad(_cp.RGB_MAX + 1))):
        
            if Tense.isInteger(n):
                # if this notation with * was removed for strings, then code below would be:
                # "".join(["0" for _ in abroad(6 - reckon(hex(n)[2:]))]) + hex(n)[2:]
                _hex = "0" * (6 - reckon(hex(n)[2:])) + hex(n)[2:]
                
            else:
                _hex = "0" * (6 - reckon(hex(int(n, base = 0))[2:])) + hex(int(n, base = 0))[2:]
            
            return RGB(int(_hex[:2], 16), int(_hex[2:4], 16), int(_hex[4:], 16))
        
        else:
            
            error = ValueError("expected a number in range 0-16777215")
            raise error
        
        
class RGBA(_util.Final):
    """
    \\@since 0.3.37
    
    ```
    class RGBA: ...
    from tense import RGBA
    ```
    
    Represents red-green-blue-alpha color representation.
    """
    
    def __init__(self, red = 0, green = 0, blue = 0, alpha = 1.0):
        
        _parameters = {
            "red": red,
            "green": green,
            "blue": blue,
        }
        
        for key in _parameters:
            
            if not Tense.isInteger(_parameters[key]) or (Tense.isInteger(_parameters[key]) and _parameters[key] not in abroad(0x100)):
                
                error = TypeError("expected a non-negative integer in parameter '{}' in range 0-255".format(key))
                raise error
            
        if not Tense.isFloat(alpha) or (Tense.isFloat(alpha) and not Math.isInRange(alpha, 0, 1)):
            
            error = TypeError("expected a non-negative float in parameter '{}' in range 0-1".format("alpha"))
            raise error
            
        self.__rgba = (red, green, blue, round(alpha, 2))
        
    def __str__(self):
        """
        \\@since 0.3.37
        """
        return "{}({}, {})".format(type(self).__name__, ", ".join([str(e) for e in self.__rgba][:-1]), self.__rgba[-1])
    
    def __repr__(self):
        """
        \\@since 0.3.37
        """
        return "<{}.{} object: {}>".format(self.__module__, type(self).__name__, self.__str__())
    
    def __hex__(self):
        """
        \\@since 0.3.38
        
        Provides conversion to hexadecimal format. \\
        Does not occur with alpha value - use `float()` instead.
        """
        _r = hex(self.__rgba[0])[2:] if self.__rgba[0] >= 0x10 else "0" + hex(self.__rgba[0])[2:]
        _g = hex(self.__rgba[1])[2:] if self.__rgba[1] >= 0x10 else "0" + hex(self.__rgba[1])[2:]
        _b = hex(self.__rgba[2])[2:] if self.__rgba[2] >= 0x10 else "0" + hex(self.__rgba[2])[2:]
        return "0x" + _r + _g + _b
    
    def __int__(self):
        """
        \\@since 0.3.38
        
        Converts RGBA tuple into its corresponding integer representation. \\
        Does not occur with alpha value - use `float()` instead.
        """
        return int(self.__hex__()[2:], base = 16)
    
    def __float__(self):
        """
        \\@since 0.3.38
        
        Returns alpha value
        """
        return self.__rgba[-1]
    
    # little deviation from type hinting in methods below
    # read document strings to figure it out
    def __lt__(self, other):
        """
        \\@since 0.3.38
        
        To return true, following conditions must be satisfied:
        - `int(self) + float(self) < int(other) + float(other)`
        - `other` must be instance of `RGBA` class
        """
        return self.__int__() + self.__float__() < other.__int__() + other.__float__() if type(other) is type(self) else False
    
    def __gt__(self, other):
        """
        \\@since 0.3.38
        
        To return true, following conditions must be satisfied:
        - `int(self) + float(self) > int(other) + float(other)`
        - `other` must be instance of `RGBA` class
        """
        return self.__int__() + self.__float__() > other.__int__() + other.__float__() if type(other) is type(self) else False
    
    def __eq__(self, other):
        """
        \\@since 0.3.38
        
        To return true, following conditions must be satisfied:
        - `int(self) + float(self) == int(other) + float(other)`
        - `other` must be instance of `RGBA` class
        """
        return self.__int__() + self.__float__() == other.__int__() + other.__float__() if type(other) is type(self) else False
    
    def __le__(self, other):
        """
        \\@since 0.3.38
        
        To return true, following conditions must be satisfied:
        - `int(self) + float(self) <= int(other) + float(other)`
        - `other` must be instance of `RGBA` class
        """
        return self.__int__() + self.__float__() <= other.__int__() + other.__float__() if type(other) is type(self) else False
    
    def __ge__(self, other):
        """
        \\@since 0.3.38
        
        To return true, following conditions must be satisfied:
        - `int(self) + float(self) >= int(other) + float(other)`
        - `other` must be instance of `RGBA` class
        """
        return self.__int__() + self.__float__() >= other.__int__() + other.__float__() if type(other) is type(self) else False
    
    def __ne__(self, other):
        """
        \\@since 0.3.38
        
        To return true, following conditions must be satisfied:
        - `int(self) + float(self) != int(other) + float(other)`
        - `other` must be instance of `RGBA` class
        """
        return self.__int__() + self.__float__() != other.__int__() + other.__float__() if type(other) is type(self) else False
    
    def __pos__(self):
        """
        \\@since 0.3.38
        
        Returns a RGBA tuple
        """
        return self.__rgba
    
    def __neg__(self):
        """
        \\@since 0.3.38
        
        Returns a RGBA tuple
        """
        return self.__rgba
    
    def __invert__(self):
        """
        \\@since 0.3.38
        
        Returns a RGBA tuple
        """
        return self.__rgba
    
    @staticmethod
    def fromValue(n: _uni[int, str], opacity: float, /):
        """
        \\@since 0.3.38
        
        Returns a new `RGBA` class object using specific integer or string value, and opacity. \\
        If string was provided on first parameter, it must contain a valid number in either hexadecimal, \\
        decimal, octal or binary notation.
        """
        
        _rgb = +RGB.fromValue(n)
        
        if not Tense.isFloat(opacity) or (Tense.isFloat(opacity) and not Math.isInRange(opacity, 0, 1)):
            
            error = TypeError("expected a non-negative float in parameter '{}' in range 0-1".format("alpha"))
            raise error
        
        return RGBA(_rgb[0], _rgb[1], _rgb[2], opacity)
    
    
class CMYK(_util.Final):
    """
    \\@since 0.3.28
    
    ```
    class CMYK(Final): ...
    from tense import CMYK
    ```
    
    Auxiliary class for `Color` class. Represents cyan-magenta-yellow color representation. \\
    Once instantiated, returns `RGB` class instance, only with inverted color values, that is: \\
    255 is 0, 254 is 1, 253 is 2 and so on, up to 0 being 255.
    """
    
    def __new__(self, cyan = 0, magenta = 0, yellow = 0, /):
        
        _parameters = {
            "cyan": cyan,
            "magenta": magenta,
            "yellow": yellow
        }
        
        for key in _parameters:
            
            if not isinstance(_parameters[key], int) or (isinstance(_parameters[key], int) and _parameters[key] not in abroad(0x100)):
                error = TypeError("expected a non-negative integer in parameter '" + key + "' in range 0-255")
                raise error
            
        return RGB(
            0xff - cyan,
            0xff - magenta,
            0xff - yellow
        )
        
class _FileRead(_tc.IntegerFlag):
    "\\@since 0.3.26rc2"
    CHARS = 0
    LINES = _tc.auto()

# _FileReadType = _lit[_FileRead.CHARS, _FileRead.LINES] # unnecessary since 0.3.27b2
# _T_stringOrIterable = _var("_T_stringOrIterable", bound = _uni[str, _tc.Iterable[str]]) ### < 0.3.36

if _cl.VERSION_INFO < (0, 3, 36) and False:
    @_tc.deprecated("Deprecated since 0.3.32, will be removed on 0.3.36")
    class File:
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts
        // created 18.07.2024
        in module tense
        ```
        Providing file IO operations
        """
        CHARS = _FileRead.CHARS
        LINES = _FileRead.LINES
        
        def __init__(self, fn: _FileType, mode: _FileMode = "r", /, buffering: int = -1, encoding: _opt[str] = None, errors: _opt[str] = None, newline: _opt[str] = None, closefd: bool = True, opener: _opt[_FileOpener] = None):
            
            self.__i = open(fn, mode, buffering, encoding, errors, newline, closefd, opener)
            
        @_tc.overload
        def read(self, mode: _lit[_FileRead.CHARS, "CHARS", "chars", "_constants", "C"] = CHARS, size: int = -1, /) -> str: ...
        
        @_tc.overload
        def read(self, mode: _lit[_FileRead.LINES, "LINES", "lines", "l", "L"], hint: int = -1, /) -> list[str]: ...
            
        def read(self, mode = CHARS, size = -1, /):
            "\\@since 0.3.26rc2"
            
            if not Tense.isInteger(size):
                error = TypeError("expected 'size' parameter to be an integer")
                raise error
            
            if self.__i.readable():
                
                if mode in (self.CHARS, "CHARS", "chars", "c", "C"):
                    return self.__i.read(size)
                
                elif mode in (self.LINES, "LINES", "lines", "l", "L"):
                    return self.__i.readlines(size)
                
                else:
                    error = TypeError("expected one of constants: 'CHARS', 'LINES'")
                    raise error
                
            else:
                error = IOError("file is not open for reading")
                raise error
            
        def write(self, content: _T_stringOrIterable):
            "\\@since 0.3.26rc2"
            
            if not Tense.isString(content) and not isinstance(content, _tc.Iterable):
                error = TypeError("Expected a string iterable or a string")
                raise error
        
            if self.__i.writable():
                
                if Tense.isString(content):
                    self.__i.write(content)
                    
                else:
                    self.__i.writelines(content)
                    
            else:
                error = IOError("file is not open for writing")
                raise error
            
        def pickle(self, o: object, protocol: _opt[int] = None, *, fixImports = True, bufferCallback: _opt[_cal[[_pickle.PickleBuffer], None]] = None):
            "\\@since 0.3.26rc2"
            if isinstance(self.__i, (
                # only on binary mode files
                _io.BufferedRandom,
                _io.BufferedReader,
                _io.BufferedWriter
            )):
                _pickle.dump(o, self.__i, protocol, fix_imports = fixImports, buffer_callback = bufferCallback)
                
            else:
                error = IOError("file is not open in binary mode")
                raise error
            
        def unpickle(self, *, fixImports = True, encoding = "ASCII", errors = "strict", buffers: _opt[_tc.Iterable[_Any]] = ()):
            "\\@since 0.3.26rc2"
            
            a = []
            
            if isinstance(self.__i, (
                # only on binary mode files
                _io.BufferedRandom,
                _io.BufferedReader,
                _io.BufferedWriter
            )):
                
                while True:
                
                    try:
                        a.append(_pickle.load(self.__i, fix_imports = fixImports, encoding = encoding, errors = errors, buffers = buffers))
                        
                    except:
                        break
                    
                return a
                
            else:
                error = IOError("file is not open in binary mode")
                raise error

# class _ChangeVarState(tc.IntegerFlag): # to 0.3.28
class _ChangeVarState(_tc.Enum):
    "\\@since 0.3.26rc1. Internal class for `ChangeVar.setState()` method"
    I = 1
    D = 2

# _ChangeVarStateSelection = _lit[_ChangeVarState.D, _ChangeVarState.I] # unnecessary since 0.3.27b2

class ChangeVar(_tc.UnaryOperable, _tc.Comparable, _tc.AdditionReassignable, _tc.SubtractionReassignable):
    """
    \\@since 0.3.26rc1 \\
    \\@lifetime ≥ 0.3.26rc1
    ```py
    class ChangeVar: ...
    from tense import ChangeVar
    ```
    Auxiliary class for creating sentinel inside `while` loop.

    Use `~instance` to receive integer value. \\
    Use `+instance` to increment by 1. \\
    Use `-instance` to decrement by 1. \\
    Use `instance += any_int` to increment by `any_int`. \\
    Use `instance -= any_int` to decrement by `any_int`.
    """
    D = _ChangeVarState.D
    I = _ChangeVarState.I
    __v = 0
    __m = 1
    __default = 0

    def __init__(self, initialValue = 0):
        
        if not Tense.isInteger(initialValue):
            error = TypeError("expected an integer value")
            raise error
        
        self.__v = initialValue
        self.__default = initialValue

    def __pos__(self):
        self.__v += self.__m

    def __neg__(self):
        self.__v -= self.__m

    def __invert__(self):
        return self.__v
    
    def __eq__(self, other: int):
        return self.__v == other if Tense.isInteger(other) else False
    
    def __contains__(self, value: int):
        return self.__v == value if Tense.isInteger(value) else False
    
    def __ne__(self, other: int):
        return self.__v != other if Tense.isInteger(other) else False
    
    def __ge__(self, other: int):
        return self.__v >= other if Tense.isInteger(other) else False
    
    def __gt__(self, other: int):
        return self.__v > other if Tense.isInteger(other) else False
    
    def __le__(self, other: int):
        return self.__v <= other if Tense.isInteger(other) else False
    
    def __lt__(self, other: int):
        return self.__v < other if Tense.isInteger(other) else False
    
    def __iadd__(self, other: int):
        
        if not Tense.isInteger(other):
            error = TypeError("expected an integer as a right operand") # error replaced 0.3.34; earlier was NotInitializedError
            raise error
        
        _tmp = self.__v
        _tmp += other
        self.__v = _tmp
        return _tmp
    
    def __isub__(self, other: int):
        
        if not Tense.isInteger(other):
            error = TypeError("expected an integer as a right operand") # error replaced 0.3.34; earlier was NotInitializedError
            raise error
        
        _tmp = self.__v
        _tmp -= other
        self.__v = _tmp
        return _tmp
    
    def reset(self):
        """
        \\@since 0.3.26rc1

        Reset the counter to value passed to the constructor, or - \\
        if `setDefault()` was invoked before - to value passed \\
        to that method.
        """
        self.__v = self.__default

    def setDefault(self, value: int):
        """
        \\@since 0.3.26rc1

        Set a new default value. This overwrites current default value. \\
        Whether `reset()` method is used after, internal variable \\
        will have the default value, which was passed to this method. \\
        Otherwise it will refer to value passed to constructor
        """
        if not Tense.isInteger(value):
            error = TypeError("expected an integer value")
            raise error
        self.__default = abs(value)

    def setState(self, s: _ChangeVarState = I, m: int = 1):
        """
        \\@since 0.3.26rc1

        Alternative for `+` and `-` unary operators.

        If `D` for `s` parameter is passed, sentinel will be decremented \\
        by 1, otherwise incremented by 1 (option `I`). Additionally, you \\
        can set a different step via `m` parameter.
        """
        _m = m
        
        if not Tense.isInteger(_m):
            error = TypeError("expected integer value for 'm' parameter")
            raise error
        
        elif abs(_m) == 0:
            _m = 1
            
        if s == self.D:
            self.__v -= abs(_m)
            
        elif s == self.I:
            self.__v += abs(_m)
            
        else:
            error = TypeError("expected 'ChangeVar.I' or 'ChangeVar.D' for 's' parameter")
            raise error
        
    def setModifier(self, m: int):
        """
        \\@since 0.3.26rc1

        Changes behavior for `+` and `-` unary operators. \\
        If passed integer value was negative, code will \\
        retrieve absolute value of it. If 0 passed, used will be 1
        """
        _params = _get_all_params(self.setModifier)
        
        if not Tense.isInteger(m):
            error = TypeError("expected integer value in parameter '{}'".format(_params[0]))
            raise error
        
        elif abs(m) == 0:
            self.__m == 1
            
        self.__m = abs(m)

class Color(_tc.ModuloOperable[_ColorStylingType, str], _tc.UnaryOperable):
    """
    \\@since 0.3.26rc1 \\
    \\@lifetime ≥ 0.3.26rc1
    ```py
    class Color: ...
    from tense import Color
    ```
    Deputy of experimental class `tense.extensions.ANSIColor` (≥ 0.3.24; < 0.3.26rc1).
    
    This class uses ANSI escape code for color purposes.

    Unary `+` and `-`, and `~` operators allow to get colored string. \\
    Since 0.3.34 using `str()` will also return colored string, other 3 ways \\
    to do so will remain due to compatibility with older versions of Tense.
    
    Modulo operator (`%`) allows to change the font style. The right operand must be \\
    an appropriate constant or lowercased string literal (for single font styles).
    Examples:
    ```ts
    Color("Tense") % Color.BOLD
    Color("Countryside!", 8, 0o105) % Color.ITALIC // italic, blue text
    Color("Creativity!", 24, 0xc0ffee) % Color.BOLD // bold, c0ffee hex code text
    Color("Illusive!", 24, 0, 0xc0ffee) % Color.BOLD // bold, c0ffee hex code background, black text
    ```

    Since 0.3.26rc2 you can use constants, which grant more than one font style simultaneously, like:
    ```ts
    Color("Lines!", 8, 93) % Color.UOLINE // lines above and below text
    ```

    **Warning**: 24-bit colors load longer than colors from lower bit shelves. In this case it is \\
    recommended to stick to 8-bit colors, but if there isn't a satisfying color, 24-bit color support \\
    will be kept. It is also somewhat a reason of `RGB` and `CMYK` colors existence.
    """
    __fg = None
    __bg = None
    if False: # 0.3.27
        __un = None
    __text = ""
    __bits = 8 # 24 to 0.3.34 

    NORMAL = _ColorStyling.NORMAL
    "\\@since 0.3.26rc1. Mere text"
    
    BOLD = _ColorStyling.BOLD
    "\\@since 0.3.26rc1. Text becomes bold"
    
    FAINT = _ColorStyling.FAINT
    "\\@since 0.3.26rc1. Also works as 'decreased intensity' or 'dim'"
    
    ITALIC = _ColorStyling.ITALIC
    "\\@since 0.3.26rc1. Text becomes oblique. Not widely supported"
    
    UNDERLINE = _ColorStyling.UNDERLINE
    "\\@since 0.3.26rc1. Text becomes underlined. Marked *experimental* as experimenting with underline colors, but normally it is OK to use"
    
    SLOW_BLINK = _ColorStyling.SLOW_BLINK
    "\\@since 0.3.26rc1. Text will blink for less than 150 times per minute"
    
    RAPID_BLINK = _ColorStyling.RAPID_BLINK
    "\\@since 0.3.26rc1. Text will blink for more than 150 times per minute. Not widely supported"
    
    REVERSE = _ColorStyling.REVERSE
    "\\@since 0.3.26rc2. Swap text and background colors"
    
    HIDE = _ColorStyling.HIDE
    "\\@since 0.3.26rc1. Text becomes transparent"
    
    STRIKE = _ColorStyling.STRIKE
    "\\@since 0.3.26rc1. Text becomes crossed out"
    
    DOUBLE_UNDERLINE = _ColorStyling.DOUBLE_UNDERLINE
    "\\@since 0.3.26rc2. Text becomes doubly underlined"
    
    # PROPORTIONAL = _ColorStyling.PROPORTIONAL
    "\\@lifetime >= 0.3.26rc1; < 0.3.26rc2. Proportional spacing. *Experimental*"
    
    FRAME = _ColorStyling.FRAME
    "\\@since 0.3.26rc1. Implemented in mintty as 'emoji variation selector'"
    
    ENCIRCLE = _ColorStyling.ENCIRCLE
    "\\@since 0.3.26rc1. Implemented in mintty as 'emoji variation selector'"
    
    OVERLINE = _ColorStyling.OVERLINE
    "\\@since 0.3.26rc1. Text becomes overlined"
    
    SUPERSCRIPT = _ColorStyling.SUPERSCRIPT
    "\\@since 0.3.26rc2. Text becomes superscripted (implemented in mintty only)"
    
    SUBSCRIPT = _ColorStyling.SUBSCRIPT
    "\\@since 0.3.26rc2. Text becomes subscripted (implemented in mintty only)"
    
    # 2x
    BOLD_ITALIC = _ColorAdvancedStyling.BOLD_ITALIC
    "\\@since 0.3.26rc2. Text becomes bold and oblique"
    
    BOLD_UNDERLINE = _ColorAdvancedStyling.BOLD_UNDERLINE
    "\\@since 0.3.26rc2. Text becomes bold and underlined"
    
    BOLD_STRIKE = _ColorAdvancedStyling.BOLD_STRIKE
    "\\@since 0.3.26rc2. Text becomes bold and crossed out"
    
    BOLD_OVERLINE = _ColorAdvancedStyling.BOLD_OVERLINE
    "\\@since 0.3.26rc2. Text becomes bold and overlined"
    
    ITALIC_UNDERLINE = _ColorAdvancedStyling.ITALIC_UNDERLINE
    "\\@since 0.3.26rc2. Text becomes oblique and underlined"
    
    ITALIC_STRIKE = _ColorAdvancedStyling.ITALIC_STRIKE
    "\\@since 0.3.26rc2. Text becomes oblique and crossed out"
    
    ITALIC_OVERLINE = _ColorAdvancedStyling.ITALIC_OVERLINE
    "\\@since 0.3.26rc2. Text becomes oblique and overlined"
    
    UNDERLINE_STRIKE = _ColorAdvancedStyling.UNDERLINE_STRIKE
    "\\@since 0.3.26rc2. Text becomes underlined and crossed out"
    
    UOLINE = _ColorAdvancedStyling.UOLINE
    "\\@since 0.3.26rc2. Alias to underline-overline. Text gets lines above and below"
    
    STRIKE_OVERLINE = _ColorAdvancedStyling.STRIKE_OVERLINE
    "\\@since 0.3.26rc2. Text becomes crossed out and overlined"
    
    # 3x
    BOLD_ITALIC_UNDERLINE = _ColorAdvancedStyling.BOLD_ITALIC_UNDERLINE
    "\\@since 0.3.26rc2. Text becomes bold, oblique and underlined"
    
    BOLD_ITALIC_STRIKE = _ColorAdvancedStyling.BOLD_ITALIC_STRIKE
    "\\@since 0.3.26rc2"
    
    BOLD_ITALIC_OVERLINE = _ColorAdvancedStyling.BOLD_ITALIC_OVERLINE
    "\\@since 0.3.26rc2"
    
    BOLD_UNDERLINE_STRIKE = _ColorAdvancedStyling.BOLD_UNDERLINE_STRIKE
    "\\@since 0.3.26rc2"
    
    BOLD_UOLINE = _ColorAdvancedStyling.BOLD_UOLINE
    "\\@since 0.3.26rc2"
    
    ITALIC_UNDERLINE_STRIKE = _ColorAdvancedStyling.ITALIC_UNDERLINE_STRIKE
    "\\@since 0.3.26rc2"
    
    ITALIC_UOLINE = _ColorAdvancedStyling.ITALIC_UOLINE
    "\\@since 0.3.26rc2"
    
    ITALIC_STRIKE_OVERLINE = _ColorAdvancedStyling.ITALIC_STRIKE_OVERLINE
    "\\@since 0.3.26rc2"
    
    STRIKE_UOLINE = _ColorAdvancedStyling.STRIKE_UOLINE
    "\\@since 0.3.26rc2"
        
    def __prepare_return(self):
        
        return _colorize(self.__text, self.__bits, self.__fg, self.__bg)
    
    if True: # since 0.3.27
        
        def __init__(self, text: str, /, bits: _Bits = 8, foregroundColor: _Color = None, backgroundColor: _Color = None): # slash since 0.3.26rc2
            """
            \\@since 0.3.26rc1. Parameters:
            - `text` - string to be colored. Required parameter
            - `bits` - number of bits, possible values: 3, 4, 8, 24. Defaults to 24 (since 0.3.26rc2 - 8)
            - `foregroundColor` - color of the foreground (text). String/integer/`None`. Defaults to `None`
            - `backgroundColor` - color of the background. String/integer/`None`. Defaults to `None`
            
            See https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit for color palette outside 24-bit colors
            """
            _os.system("color")
            
            _params = _get_all_params(self.__init__)
            
            if not Tense.isString(text):
                error = TypeError("expected string value for '{}' parameter".format(_params[0]))
                raise error
            
            if not Tense.isInteger(bits) or (Tense.isInteger(bits) and bits not in (3, 4, 8, 24)):
                error = TypeError("expected integer value: 3, 4, 8 or 24, for '{}' parameter".format(_params[1]))
                raise error
            
            for e in (foregroundColor, backgroundColor):
                
                # Issue caught and fixed on 0.3.37 (GeckoGM)
                # 0.3.38: Fixed for RGB instances
                if not isinstance(e, (_Color, RGB)):
                    error = TypeError("expected integer, string or 'None' value for both foreground and background color parameters")
                    raise error
                
                elif Tense.isString(e) and (
                    # changing this order may cause easier error
                    not _is_hexadecimal(e) and
                    not _is_decimal(e) and
                    not _is_octal(e) and
                    not _is_binary(e)
                ):
                    error = TypeError(f"malformed string in either foreground or background color parameters, expected clean binary, decimal, hexademical or octal string")
                    raise error
                
                elif bits == 24 and e is not None and (
                    Tense.isInteger(e) and e not in abroad(0x1000000) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x1000000) or
                    isinstance(e, RGB) and int(e) not in abroad(0x1000000)
                ):
                    error = ValueError("for 24-bit colors, expected \"RGB\" class instance of integer value, integer or string value in range 0-16777215")
                    raise error
                
                elif bits == 8 and e is not None and (
                    Tense.isInteger(e) and e not in abroad(0x100) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x100) or isinstance(e, RGB)
                ):
                    error = ValueError("for 8-bit colors, expected integer or string value in range 0-255. Cannot be used with \"RGB\" class instance")
                    raise error
                
                elif bits == 4 and e is not None and (
                    Tense.isInteger(e) and e not in abroad(0x10) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x10) or isinstance(e, RGB)
                ):
                    error = ValueError("for 4-bit colors, expected integer or string value in range 0-15. Cannot be used with \"RGB\" class instance")
                    raise error
                
                elif bits == 3 and e is not None and (
                    Tense.isInteger(e) and e not in abroad(0x8) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x8) or isinstance(e, RGB)
                ):
                    error = ValueError("for 3-bit colors, expected integer or string value in range 0-7. Cannot be used with \"RGB\" class instance")
                    raise error
            
            self.__text = text
            self.__bits = bits
            self.__fg = foregroundColor if Tense.isInteger(foregroundColor) else _int_conversion(foregroundColor) if Tense.isString(foregroundColor) else int(foregroundColor) if isinstance(foregroundColor, RGB) else None
            self.__bg = backgroundColor if Tense.isInteger(backgroundColor) else _int_conversion(backgroundColor) if Tense.isString(backgroundColor) else int(backgroundColor) if isinstance(backgroundColor, RGB) else None
            
    else:
        def __init__(self, text: str, /, bits: _Bits = 8, foregroundColor: _Color = None, backgroundColor: _Color = None, underlineColor: _Color = None):
            
            _os.system("color")
            
            if not Tense.isString(text):
                error = TypeError("Expected string value for 'text' parameter")
                raise error
            
            if not Tense.isInteger(bits) or (Tense.isInteger(bits) and bits not in (3, 4, 8, 24)):
                error = TypeError("Expected integer value: 3, 4, 8 or 24, for 'bits' parameter")
                raise error
            
            for e in (foregroundColor, backgroundColor, underlineColor):
                
                if not Tense.isInteger(e) and not Tense.isString(e) and e is not None:
                    error = TypeError(f"Expected integer, string or 'None' value for '{e.__name__}' parameter")
                    raise error
                
                elif Tense.isString(e) and (
                    not _is_hexadecimal(e) and
                    not _is_decimal(e) and
                    not _is_octal(e) and
                    not _is_binary(e)
                ):
                    error = TypeError(f"Malformed string in parameter 'e', expected clean binary, decimal, hexademical or octal string")
                    raise error
                
                elif bits == 24 and e is not None and (
                    Tense.isInteger(e) and e not in abroad(0x1000000) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x1000000)
                ):
                    error = ValueError(f"For 24-bit colors, expected integer or string value in range 0-16777215")
                    raise error
                
                elif bits == 8 and e is not None and (
                    Tense.isInteger(e) and e not in abroad(0x100) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x100)
                ):
                    error = ValueError(f"For 8-bit colors, expected integer or string value in range 0-255")
                    raise error
                
                elif bits == 4 and e is not None and (
                    Tense.isInteger(e) and e not in abroad(0x10) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x10)
                ):
                    error = ValueError(f"For 4-bit colors, expected integer or string value in range 0-15")
                    raise error
                
                elif bits == 3 and e is not None and (
                    Tense.isInteger(e) and e not in abroad(0x8) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x8)
                ):
                    error = ValueError(f"For 3-bit colors, expected integer or string value in range 0-7")
                    raise error
                
            self.__text = text
            self.__bits = bits
            self.__fg = foregroundColor if Tense.isInteger(foregroundColor) else _int_conversion(foregroundColor) if Tense.isString(foregroundColor) else None
            self.__bg = backgroundColor if Tense.isInteger(backgroundColor) else _int_conversion(backgroundColor) if Tense.isString(backgroundColor) else None
            self.__un = underlineColor if Tense.isInteger(underlineColor) else _int_conversion(underlineColor) if Tense.isString(underlineColor) else None
    
    def clear(self):
        """
        \\@since 0.3.26rc1
        
        Clear every color for foreground, background and underline. Should \\
        be used before `setBits()` method invocation to avoid conflicts. \\
        By default bits value is reset to 24. Since 0.3.27b1 - 8.
        """
        self.__fg = None
        self.__bg = None
        if False: # 0.3.27
            self.__un = None
        self.__bits = 8
        return self
    
    def setBits(self, bits: _Bits = 8, /):
        """
        \\@since 0.3.26rc1

        Possible values: 3, 4, 8, 24. Default is 24. \\
        Since 0.3.26rc2 default value is 8.
        """
        
        if not Tense.isInteger(bits) or (Tense.isInteger(bits) and bits not in (3, 4, 8, 24)):
            error = TypeError("expected integer value: 3, 4, 8 or 24, for 'bits' parameter")
            raise error
        
        # for e in (self.__fg, self.__bg, self.__un): ### removed 0.3.27
        for e in (self.__fg, self.__bg):
            
            if e is not None:
                
                if bits == 24 and e not in abroad(0x1000000):
                    error = ValueError("internal conflict caught while setting 'bits' value to 24. One of foreground or background values is beyond range 0-16777215. To prevent this conflict, use method 'Color.clear()'.")
                    raise error
                
                elif bits == 8 and e not in abroad(0x100):
                    error = ValueError("internal conflict caught while setting 'bits' value to 8. One of foreground or background values is beyond range 0-255. To prevent this conflict, use method 'Color.clear()'.")
                    raise error
                
                elif bits == 4 and e not in abroad(0x10):
                    error = ValueError("internal conflict caught while setting 'bits' value to 4. One of foreground or background values is beyond range 0-15. To prevent this conflict, use method 'Color.clear()'.")
                    raise error
                
                elif bits == 3 and e not in abroad(0x8):
                    error = ValueError("internal conflict caught while setting 'bits' value to 3. One of foreground or background values is beyond range 0-7. To prevent this conflict, use method 'Color.clear()'.")
                    raise error
                
        self.__bits = bits
    
    def setForegroundColor(self, color: _Color = None, /):
        """
        \\@since 0.3.26rc1
        
        Set foreground color manually.
        """
        _c = color if Tense.isInteger(color) or color is None else _int_conversion(color) if Tense.isString(color) else int(color) if isinstance(color, RGB) else None
        
        if _c is not None:
            
            if self.__bits == 3 and _c not in abroad(0x8):
                error = ValueError(f"for 3-bit colors, expected integer or string value in range 0-7")
                raise error
            
            elif self.__bits == 4 and _c not in abroad(0x10):
                error = ValueError(f"for 4-bit colors, expected integer or string value in range 0-15")
                raise error
            
            elif self.__bits == 8 and _c not in abroad(0x100):
                error = ValueError(f"for 8-bit colors, expected integer or string value in range 0-255")
                raise error
            
            elif self.__bits == 24 and _c not in abroad(0x1000000):
                error = ValueError(f"for 24-bit colors, expected integer, string or RGB/CMYK tuple value in range 0-16777215")
                raise error
            
            else:
                error = ValueError(f"internal 'bits' variable value is not one from following: 3, 4, 8, 24")
                raise error
            
        self.__fg = _c
        return self
    
    def setBackgroundColor(self, color: _Color = None, /):
        """
        \\@since 0.3.26rc1
        
        Set background color manually.
        """
        _c = color if Tense.isInteger(color) or color is None else _int_conversion(color) if Tense.isString(color) else int(color) if isinstance(color, RGB) else None
        
        if _c is not None:
            
            if self.__bits == 3 and _c not in abroad(0x8):
                error = ValueError(f"for 3-bit colors, expected integer or string value in range 0-7")
                raise error
            
            elif self.__bits == 4 and _c not in abroad(0x10):
                error = ValueError(f"for 4-bit colors, expected integer or string value in range 0-15")
                raise error
            
            elif self.__bits == 8 and _c not in abroad(0x100):
                error = ValueError(f"for 8-bit colors, expected integer or string value in range 0-255")
                raise error
            
            elif self.__bits == 24 and _c not in abroad(0x1000000):
                error = ValueError(f"for 24-bit colors, expected integer, string or RGB/CMYK tuple value in range 0-16777215")
                raise error
            
            else:
                error = ValueError(f"internal 'bits' variable value is not one from following: 3, 4, 8, 24")
                raise error
            
        self.__bg = _c
        return self
    
    if False:
        def setUnderlineColor(self, color: _Color = None, /):
            """
            \\@since 0.3.26rc1
            
            Set underline color manually. *Experimental* \\
            Since 0.3.26rc2 only accepted value is `None`.
            """
            _c = color if Tense.isInteger(color) or color is None else _int_conversion(color)
            if _c is not None:
                if self.__bits == 3 and _c not in abroad(0x8):
                    error = ValueError(f"For 3-bit colors, expected integer or string value in range 0-7")
                    raise error
                
                elif self.__bits == 4 and _c not in abroad(0x10):
                    error = ValueError(f"For 4-bit colors, expected integer or string value in range 0-15")
                    raise error
                
                elif self.__bits == 8 and _c not in abroad(0x100):
                    error = ValueError(f"For 8-bit colors, expected integer or string value in range 0-255")
                    raise error
                
                elif self.__bits == 24 and _c not in abroad(0x1000000):
                    error = ValueError(f"For 24-bit colors, expected integer or string value in range 0-16777215")
                    raise error
                
                else:
                    error = ValueError(f"Internal 'bits' variable value is not one from following: 3, 4, 8, 24")
                    raise error
                
            self.__un = _c
            return self
    
    
    def __pos__(self):
        """\\@since 0.3.26rc1. Receive colored string"""
        return self.__prepare_return()
    
    def __neg__(self):
        """\\@since 0.3.26rc1. Receive colored string"""
        return self.__prepare_return()
    
    def __invert__(self):
        """\\@since 0.3.26rc1. Receive colored string"""
        return self.__prepare_return()
    
    def __str__(self):
        """\\@since 0.3.34. Receive colored string"""
        return self.__prepare_return()
    
    def __repr__(self):
        """\\@since 0.3.35"""
        return "<{}.{} object: {}(\"{}\")>".format(
            self.__module__,
            type(self).__name__,
            type(self).__name__,
            self.__text
        )
    
    def __mod__(self, other: _ColorStylingType):
        """
        \\@since 0.3.26rc1
        
        Further styling. Use constant, which is in `__constants__` attribute.
        """
        # below: since 0.3.26rc1
        if other in (self.NORMAL, "normal"):
            return self.__prepare_return()
        
        elif other in (self.BOLD, "bold"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[1;", self.__prepare_return())
        
        elif other in (self.FAINT, "faint"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[2;", self.__prepare_return())
        
        elif other in (self.ITALIC, "italic"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[3;", self.__prepare_return())
        
        elif other in (self.UNDERLINE, "underline"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[4;", self.__prepare_return())
        
        elif other in (self.SLOW_BLINK, "slow_blink"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[5;", self.__prepare_return())
        
        elif other in (self.RAPID_BLINK, "rapid_blink"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[6;", self.__prepare_return())
        
        # below: since 0.3.26rc2
        elif other in (self.REVERSE, "reverse"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[7;", self.__prepare_return())
        
        # below: since 0.3.26rc1
        elif other in (self.HIDE, "hide"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[8;", self.__prepare_return())
        
        elif other in (self.STRIKE, "strike"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[9;", self.__prepare_return())
        
        elif other in (self.DOUBLE_UNDERLINE, "double_underline"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[21;", self.__prepare_return())
        
        # elif other == self.PROPORTIONAL:
        #    return _re.sub(r"^(\033\[|\u001b\[)", "\033[26;", self.__prepare_return())
        
        elif other in (self.FRAME, "frame"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[51;", self.__prepare_return())
        
        elif other in (self.ENCIRCLE, "encircle"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[52;", self.__prepare_return())
        
        elif other in (self.OVERLINE, "overline"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[53;", self.__prepare_return())
        
        # below: since 0.3.26rc2
        elif other in (self.SUPERSCRIPT, "superscript"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[73;", self.__prepare_return())
        
        elif other in (self.SUBSCRIPT, "subscript"):
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[74;", self.__prepare_return())
        # 2x; since 0.3.26rc2
        elif other == self.BOLD_ITALIC:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[1;3;", self.__prepare_return())
        
        elif other == self.BOLD_UNDERLINE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[1;4;", self.__prepare_return())
        
        elif other == self.BOLD_STRIKE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[1;9;", self.__prepare_return())
        
        elif other == self.BOLD_OVERLINE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[1;53;", self.__prepare_return())
        
        elif other == self.ITALIC_UNDERLINE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[3;4;", self.__prepare_return())
        
        elif other == self.ITALIC_STRIKE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[3;9;", self.__prepare_return())
        
        elif other == self.ITALIC_OVERLINE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[3;53;", self.__prepare_return())
        
        elif other == self.UNDERLINE_STRIKE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[4;9;", self.__prepare_return())
        
        elif other == self.UOLINE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[4;53;", self.__prepare_return())
        
        elif other == self.STRIKE_OVERLINE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[9;53;", self.__prepare_return())
        
        # 3x; since 0.3.26rc2
        elif other == self.BOLD_ITALIC_UNDERLINE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[1;3;4;", self.__prepare_return())
        
        elif other == self.BOLD_ITALIC_STRIKE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[1;3;9;", self.__prepare_return())
        
        elif other == self.BOLD_ITALIC_OVERLINE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[1;3;53;", self.__prepare_return())
        
        elif other == self.BOLD_UNDERLINE_STRIKE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[1;4;9;", self.__prepare_return())
        
        elif other == self.BOLD_UOLINE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[1;4;53;", self.__prepare_return())
        
        elif other == self.ITALIC_UNDERLINE_STRIKE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[3;4;9;", self.__prepare_return())
        
        elif other == self.ITALIC_UOLINE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[3;4;53;", self.__prepare_return())
        
        elif other == self.ITALIC_STRIKE_OVERLINE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[3;9;53;", self.__prepare_return())
        
        elif other == self.STRIKE_UOLINE:
            return _re.sub(r"^(\033\[|\u001b\[)", "\033[4;9;53;", self.__prepare_return())
        
        else:
            # replace error due to enumerator type change (0.3.27)
            if True:
                error = TypeError("expected one from following constant values as a right operand: " + repr(self.__constants__) + " or a specific lowercased string literal when single font style was meant to be applied")
            else:
                error = TypeError(
                    "Expected any from constant values: " + repr(self.__constants__) + ". You are discouraged to do common operations on these constants, like union as in case of regular expression flags, to satisfy this requirement, because it "
                    "won't warrant that returned string will be styled as thought"
                )
            raise error
    __dir__ = [n for n in locals() if n[:1] != "_"]
    "\\@since 0.3.26rc2"
    __all__ = [n for n in locals() if n[:1] != "_"]
    "\\@since 0.3.26rc2. Returns list of all non-underscore-preceded members of class `tense.Color`"
    __constants__ = [n for n in locals() if n[:1] != "_" and n.isupper()]
    
    """
    \\@since 0.3.26rc2

    Returns list of constants. These can be used as right operand for `%` operator. \\
    They are sorted as in ANSI escape code table, in ascending order
    """
    
Colour = Color
"""
\\@since 0.3.37: type alias `tense.Colour`
"""

if __name__ == "__main__":
    error = RuntimeError("this file is not for compiling, consider importing it instead")
    raise error

__all__ = sorted([n for n in globals() if n[:1] != "_"])
__dir__ = __all__

__author__ = "Aveyzan <aveyzan@gmail.com>"
"\\@since 0.3.26rc3"
__license__ = "MIT"
"\\@since 0.3.26rc3"
__version__ = Tense.version
"\\@since 0.3.26rc3"