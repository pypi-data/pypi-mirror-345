"""
**Tense Internal Constants**

\\@since 0.3.35 \\
© 2024-Present Aveyzan // License: MIT
```ts
module tense._constants
```
Internal constants for AveyTense.
"""

from ._init_types import Enum as _Enum
from platform import architecture as _architecture

_qualifier = ("alpha", "beta", "candidate", "final")

VERSION = "0.3.39"
"""
\\@since 0.3.26b3
https://aveyzan.glitch.me/tense#tense.constants.VERSION

Returns currently used version of AveyTense
"""

VERSION_INFO = (0, 3, 39, _qualifier[3], 0)
"""
\\@since 0.3.26b3
https://aveyzan.glitch.me/tense#tense.constants.VERSION_INFO
"""

VERSION_INFO_TYPE = type(VERSION_INFO)
"""\\@since 0.3.36"""

class AbroadHexMode(_Enum):
    "\\@since 0.3.26rc2"
    
    INCLUDE = 0
    HASH = 1
    EXCLUDE = 2

class BisectMode(_Enum):
    "\\@since 0.3.26rc2"
    
    LEFT = 0
    RIGHT = 1
    
class InsortMode(_Enum):
    "\\@since 0.3.26rc2"
    
    LEFT = 0
    RIGHT = 1

class ProbabilityLength(_Enum):
    "\\@since 0.3.26rc2"
    
    COMPUTE = -1
    DEFAULT = 10000
    
    if _architecture()[0] == "64bit":
        MAX = 2 ** 63 - 1 # 9223372036854775807
        
    else:
        MAX = 2 ** 31 - 1 # 2147483647
    
    MIN = 1
    
    
class ModeSelection(_Enum):
    "\\@since 0.3.36"
    
    AND = 0
    OR = 1
    