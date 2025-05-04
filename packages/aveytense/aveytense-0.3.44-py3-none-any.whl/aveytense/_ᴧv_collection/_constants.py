"""
**AveyTense Internal Constants**

\\@since 0.3.35 \\
© 2024-Present Aveyzan // License: MIT
```ts
module aveytense._constants
```
Internal constants for AveyTense.
"""
from __future__ import annotations
from . import _types
from .. import util as _util
from platform import architecture as _architecture

_qualifier = ("alpha", "beta", "candidate", "final")
_qualifier_type = _types.Literal["alpha", "beta", "candidate", "final"]
_version_info_type = tuple[int, int, int, _qualifier_type, int]

# >= 0.3.43; These are used only for overloads in order to hide unnecessary parts of the code
# when used with 'if' via 'VERSION_INFO', like 'sys.version_info'
_current_version_info_type1 = tuple[_types.Literal[0]]
_current_version_info_type2 = tuple[_types.Unpack[_current_version_info_type1], _types.Literal[3]]
_current_version_info_type3 = tuple[_types.Unpack[_current_version_info_type2], _types.Literal[44]]
_current_version_info_type4 = tuple[_types.Unpack[_current_version_info_type3], _types.Literal["final"]]
_current_version_info_type5 = tuple[_types.Unpack[_current_version_info_type4], _types.Literal[0]]

_counter_version_type = 0

VERSION = "0.3.44"
"""
\\@since 0.3.26b3
https://aveyzan.glitch.me/tense#tense.constants.VERSION

Returns currently used version of AveyTense
"""

def _qualifier_convert(s: str, /): # 0.3.40
    
    if s == "alpha":
        return 0
    
    elif s == "beta":
        return 1
    
    elif s == "candidate":
        return 2
    
    elif s == "final":
        return 3
    
    else:
        return -1

def _check_if_correct_tuple(t, /): # 0.3.40
    
    return type(t) is tuple and (
        (len(t) in (1, 2, 3) and all([type(e) is int for e in t])) or
        (len(t) == 4 and all([type(e) is int for e in t][:3]) and t[3] in _qualifier) or
        (len(t) == 5 and all([type(e) is int for e in t][:3] + [type(t[4]) is int]) and t[3] in _qualifier)
    )

class _VERSION_INFO:
    """\\@since 0.3.40"""
    
    def __init__(self, major: int, minor: int, micro: int, releaselevel: _qualifier_type, serial: int, /): # 0.3.40
        
        global _counter_version_type
        
        if _counter_version_type == 1:
            error = TypeError("cannot instantiate internal class '{}'".format(type(self).__name__))
            raise error
        
        else:
            _counter_version_type = 1
        
        self.__tuple = (major, minor, micro, releaselevel, serial if releaselevel != "final" else 0)
        
    @_util.finalproperty
    def major(self): # 0.3.40
        return self.__tuple[0]
    
    @_util.finalproperty
    def minor(self): # 0.3.40
        return self.__tuple[1]
    
    @_util.finalproperty
    def micro(self): # 0.3.40
        return self.__tuple[2]
    
    @_util.finalproperty
    def releaselevel(self): # 0.3.40
        return self.__tuple[3]
    
    @_util.finalproperty
    def serial(self): # 0.3.40
        return self.__tuple[4]
    
    @_util.finalproperty
    def tuple(self): # 0.3.40
        return self.__tuple
    
    def __str__(self): # 0.3.40
        
        return "-----\nAveyTense {} \nversion_components[\n\033[3m  major = {},\n  minor = {},\n  micro = {},\n  releaselevel = '{}',\n  serial = {}\033[0m\n]\n-----".format(
            "\033[38;5;46m{}.{}.{}\033[0m (final release)".format(self.__tuple[0], self.__tuple[1], self.__tuple[2]) if self.__tuple[3] == "final" else
            "\033[38;5;208m{}.{}.{}a{}\033[0m (alpha release)".format(self.__tuple[0], self.__tuple[1], self.__tuple[2], self.__tuple[4]) if self.__tuple[3] == "alpha" else
            "\033[38;5;226m{}.{}.{}b{}\033[0m (beta release)".format(self.__tuple[0], self.__tuple[1], self.__tuple[2], self.__tuple[4]) if self.__tuple[3] == "beta" else
            "\033[38;5;154m{}.{}.{}rc{}\033[0m (release candidate)".format(self.__tuple[0], self.__tuple[1], self.__tuple[2], self.__tuple[4]),
            self.__tuple[0], self.__tuple[1], self.__tuple[2], self.__tuple[3], self.__tuple[4]
        )
        
    @_types.overload
    def __lt__(self, other: _current_version_info_type1) -> _types.Literal[False]: ...
        
    @_types.overload
    def __lt__(self, other: _current_version_info_type2) -> _types.Literal[False]: ...
    
    @_types.overload
    def __lt__(self, other: _current_version_info_type3) -> _types.Literal[False]: ...
    
    @_types.overload
    def __lt__(self, other: _current_version_info_type4) -> _types.Literal[False]: ...
    
    @_types.overload
    def __lt__(self, other: _current_version_info_type5) -> _types.Literal[False]: ...
    
    @_types.overload
    def __lt__(self, other: _version_info_type) -> bool: ...
        
    def __lt__(self, other: _version_info_type): # 0.3.40
        
        return bool(_check_if_correct_tuple(other) and (
            (len(other) == 1 and self.major < other[0]) or
            (len(other) == 2 and self.minor < other[1]) or
            (len(other) == 3 and self.micro < other[2]) or
            (len(other) == 4 and _qualifier_convert(self.releaselevel) < _qualifier_convert(other[3])) or
            (len(other) == 5 and self.serial < other[4])
        ))
        
    @_types.overload
    def __gt__(self, other: _current_version_info_type1) -> _types.Literal[False]: ...
        
    @_types.overload
    def __gt__(self, other: _current_version_info_type2) -> _types.Literal[False]: ...
    
    @_types.overload
    def __gt__(self, other: _current_version_info_type3) -> _types.Literal[False]: ...
    
    @_types.overload
    def __gt__(self, other: _current_version_info_type4) -> _types.Literal[False]: ...
    
    @_types.overload
    def __gt__(self, other: _current_version_info_type5) -> _types.Literal[False]: ...
    
    @_types.overload
    def __gt__(self, other: _version_info_type) -> bool: ...
        
    def __gt__(self, other: _version_info_type): # 0.3.40
        
        return bool(_check_if_correct_tuple(other) and (
            (len(other) == 1 and self.major > other[0]) or
            (len(other) == 2 and self.minor > other[1]) or
            (len(other) == 3 and self.micro > other[2]) or
            (len(other) == 4 and _qualifier_convert(self.releaselevel) > _qualifier_convert(other[3])) or
            (len(other) == 5 and self.serial > other[4])
        ))
        
    @_types.overload
    def __le__(self, other: _current_version_info_type1) -> _types.Literal[True]: ...
        
    @_types.overload
    def __le__(self, other: _current_version_info_type2) -> _types.Literal[True]: ...
    
    @_types.overload
    def __le__(self, other: _current_version_info_type3) -> _types.Literal[True]: ...
    
    @_types.overload
    def __le__(self, other: _current_version_info_type4) -> _types.Literal[True]: ...
    
    @_types.overload
    def __le__(self, other: _current_version_info_type5) -> _types.Literal[True]: ...
    
    @_types.overload
    def __le__(self, other: _version_info_type) -> bool: ...
        
    def __le__(self, other): # 0.3.40
        
        return bool(_check_if_correct_tuple(other) and (
            (len(other) == 1 and self.major <= other[0]) or
            (len(other) == 2 and self.minor <= other[1]) or
            (len(other) == 3 and self.micro <= other[2]) or
            (len(other) == 4 and _qualifier_convert(self.releaselevel) <= _qualifier_convert(other[3])) or
            (len(other) == 5 and self.serial <= other[4])
        ))
        
    @_types.overload
    def __ge__(self, other: _current_version_info_type1) -> _types.Literal[True]: ...
        
    @_types.overload
    def __ge__(self, other: _current_version_info_type2) -> _types.Literal[True]: ...
    
    @_types.overload
    def __ge__(self, other: _current_version_info_type3) -> _types.Literal[True]: ...
    
    @_types.overload
    def __ge__(self, other: _current_version_info_type4) -> _types.Literal[True]: ...
    
    @_types.overload
    def __ge__(self, other: _current_version_info_type5) -> _types.Literal[True]: ...
    
    @_types.overload
    def __ge__(self, other: _version_info_type) -> bool: ...
        
    def __ge__(self, other): # 0.3.40
        
        return bool(_check_if_correct_tuple(other) and (
            (len(other) == 1 and self.major >= other[0]) or
            (len(other) == 2 and self.minor >= other[1]) or
            (len(other) == 3 and self.micro >= other[2]) or
            (len(other) == 4 and _qualifier_convert(self.releaselevel) >= _qualifier_convert(other[3])) or
            (len(other) == 5 and self.serial >= other[4])
        ))
        
    def __eq__(self, other: _version_info_type): # 0.3.40
        
        return bool(_check_if_correct_tuple(other) and (
            (len(other) == 1 and self.major == other[0]) and
            (len(other) == 2 and self.minor == other[1]) and
            (len(other) == 3 and self.micro == other[2]) and
            (len(other) == 4 and _qualifier_convert(self.releaselevel) == _qualifier_convert(other[3])) and
            (len(other) == 5 and self.serial == other[4])
        ))
        
    def __ne__(self, other: _version_info_type): # 0.3.40
        
        return not self.__eq__(other)

VERSION_INFO = _VERSION_INFO(0, 3, 44, _qualifier[3], 0)
"""
\\@since 0.3.26b3
https://aveyzan.glitch.me/tense#tense.constants.VERSION_INFO
"""

VERSION_INFO_TYPE = type(VERSION_INFO)
"""\\@since 0.3.36"""

_VERSION_INFO = _util.abstract(_VERSION_INFO)

class AbroadHexMode(_types.Enum):
    "\\@since 0.3.26rc2"
    
    INCLUDE = 0
    HASH = 1
    EXCLUDE = 2

class BisectMode(_types.Enum):
    "\\@since 0.3.26rc2"
    
    LEFT = 0
    RIGHT = 1
    
class InsortMode(_types.Enum):
    "\\@since 0.3.26rc2"
    
    LEFT = 0
    RIGHT = 1

class ProbabilityLength(_types.Enum):
    "\\@since 0.3.26rc2"
    
    COMPUTE = -1
    DEFAULT = 10000
    
    if _architecture()[0] == "64bit":
        MAX = 2 ** 63 - 1 # 9223372036854775807
        
    else:
        MAX = 2 ** 31 - 1 # 2147483647
    
    MIN = 1
    
    
class ModeSelection(_types.Enum):
    "\\@since 0.3.36"
    
    AND = 0
    OR = 1
    
if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error