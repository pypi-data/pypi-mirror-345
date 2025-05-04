"""
**Tense Constants** \n
\\@since 0.3.26rc3 \\
© 2023-Present Aveyzan // License: MIT
```ts
module tense.constants
```
Constants wrapper for AveyTense. Extracted from former `tense.tcs` module
"""

from ._constants import (
    VERSION,
    VERSION_INFO as VERSION_INFO,
    VERSION_INFO_TYPE as VERSION_INFO_TYPE,
    AbroadHexMode as _AbroadHexMode,
    BisectMode as _BisectMode,
    InsortMode as _InsortMode,
    ProbabilityLength as _ProbabilityLength,
    ModeSelection as _ModeSelection
)
from .util import finalproperty as _finalproperty

#################################### MATH CONSTANTS (0.3.26b3) ####################################

MATH_NAN = float("nan")
MATH_INF = float("inf")
MATH_E = 2.718281828459045235360287471352
MATH_PI = 3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132823066470938446095505822317253594081284811174502841027019385211055596446229489549303819644288109756659334461
MATH_TAU = 6.283185307179586476925287
MATH_SQRT2 = 1.4142135623730950488016887242097
MATH_THOUSAND           = 10 ** 3
MATH_MILLION            = 10 ** 6
MATH_BILLION            = 10 ** 9
MATH_TRILLION           = 10 ** 12
MATH_QUADRILLION        = 10 ** 15
MATH_QUINTILLION        = 10 ** 18
MATH_SEXTILLION         = 10 ** 21
MATH_SEPTILLION         = 10 ** 24
MATH_OCTILLION          = 10 ** 27
MATH_NONILLION          = 10 ** 30
MATH_DECILLION          = 10 ** 33
MATH_UNDECILLION        = 10 ** 36
MATH_DUODECILLION       = 10 ** 39
MATH_TREDECILLION       = 10 ** 42
MATH_QUATTUOR_DECILLION = 10 ** 45
MATH_QUINDECILLION      = 10 ** 48
MATH_SEXDECILLION       = 10 ** 51
MATH_SEPTEN_DECILLION   = 10 ** 54
MATH_OCTODECILLION      = 10 ** 57
MATH_NOVEMDECILLION     = 10 ** 60
MATH_VIGINTILLION       = 10 ** 63
MATH_GOOGOL             = 10 ** 100
MATH_CENTILLION         = 10 ** 303

#################################### OTHER CONSTANTS ####################################

JS_MIN_SAFE_INTEGER = -9007199254740991
"""
\\@since 0.3.26b3

`-(2^53 - 1)` - the smallest safe integer in JavaScript
"""
JS_MAX_SAFE_INTEGER = 9007199254740991
"""
\\@since 0.3.26b3

`2^53 - 1` - the biggest safe integer in JavaScript
"""
JS_MIN_VALUE = 4.940656458412465441765687928682213723650598026143247644255856825006755072702087518652998363616359923797965646954457177309266567103559397963987747960107818781263007131903114045278458171678489821036887186360569987307230500063874091535649843873124733972731696151400317153853980741262385655911710266585566867681870395603106249319452715914924553293054565444011274801297099995419319894090804165633245247571478690147267801593552386115501348035264934720193790268107107491703332226844753335720832431936092382893458368060106011506169809753078342277318329247904982524730776375927247874656084778203734469699533647017972677717585125660551199131504891101451037862738167250955837389733598993664809941164205702637090279242767544565229087538682506419718265533447265625e-324
"""
\\@since 0.3.26b3

`2^-1074` - the smallest possible number in JavaScript \\
Precision per digit
"""
JS_MAX_VALUE = 17976931348623139118889956560692130772452639421037405052830403761197852555077671941151929042600095771540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368
"""
\\@since 0.3.26b3

`2^1024 - 2^971` - the biggest possible number in JavaScript \\
Precision per digit
"""

SMASH_HIT_CHECKPOINTS = 13
"""
\\@since 0.3.26b3

Amount of checkpoints in Smash Hit (12 normal, 0-11 + 1 endless)
"""
MC_ENCHANTS = 42
"""
\\@since 0.3.26b3

Amount of enchantments in Minecraft
"""

class _MC_DURABILITY:
    """
    \\@since 0.3.37
    
    A class with a list of final properties. \\
    Suffix `_j` means item in Java version. \\
    Suffix `_b` means item in Bedrock version.
    """
    
    @_finalproperty
    def helmet_turtleShell(self):
        return 275
    
    @_finalproperty
    def helmet_leather(self):
        return 55
    
    @_finalproperty
    def helmet_golden(self):
        return 77
    
    @_finalproperty
    def helmet_chainmail(self):
        return 165
    
    @_finalproperty
    def helmet_iron(self):
        return 165
    
    @_finalproperty
    def helmet_diamond(self):
        return 363
    
    @_finalproperty
    def helmet_netherite(self):
        return 407
    
    @_finalproperty
    def chestplate_leather(self):
        return 80
    
    @_finalproperty
    def chestplate_golden(self):
        return 112
    
    @_finalproperty
    def chestplate_chainmail(self):
        return 240
    
    @_finalproperty
    def chestplate_iron(self):
        return 240
    
    @_finalproperty
    def chestplate_diamond(self):
        return 528
    
    @_finalproperty
    def chestplate_netherite(self):
        return 592
    
    @_finalproperty
    def leggings_leather(self):
        return 75
    
    @_finalproperty
    def leggings_golden(self):
        return 105
    
    @_finalproperty
    def leggings_chainmail(self):
        return 225
    
    @_finalproperty
    def leggings_iron(self):
        return 225
    
    @_finalproperty
    def leggings_diamond(self):
        return 495
    
    @_finalproperty
    def leggings_netherite(self):
        return 555
    
    @_finalproperty
    def boots_leather(self):
        return 65
    
    @_finalproperty
    def boots_golden(self):
        return 91
    
    @_finalproperty
    def boots_chainmail(self):
        return 195
    
    @_finalproperty
    def boots_iron(self):
        return 195
    
    @_finalproperty
    def boots_diamond(self):
        return 429
    
    @_finalproperty
    def boots_netherite(self):
        return 481
    
    @_finalproperty
    def bow(self):
        return 384
    
    @_finalproperty
    def shield(self):
        return 336
    
    @_finalproperty
    def trident(self):
        return 250
    
    @_finalproperty
    def elytra(self):
        return 432
    
    @_finalproperty
    def crossbow_j(self):
        return 465
    
    @_finalproperty
    def crossbow_b(self):
        return 464
    
    @_finalproperty
    def brush(self):
        return 64
    
    @_finalproperty
    def fishingRod_j(self):
        return 64
    
    @_finalproperty
    def fishingRod_b(self):
        return 384
    
    @_finalproperty
    def flintAndSteel(self):
        return 64
    
    @_finalproperty
    def carrotOnStick(self):
        return 25
    
    @_finalproperty
    def warpedFungusOnStick(self):
        return 100
    
    @_finalproperty
    def sparkler_b(self):
        return 100
    
    @_finalproperty
    def glowStick_b(self):
        return 64
    
    @_finalproperty
    def tool_gold(self):
        return 32
    
    @_finalproperty
    def tool_wood(self):
        return 65
    
    @_finalproperty
    def tool_stone(self):
        return 131
    
    @_finalproperty
    def tool_iron(self):
        return 250
    
    @_finalproperty
    def tool_diamond(self):
        return 1561
    
    @_finalproperty
    def tool_netherite(self):
        return 2031
    
    __all__ = sorted([k for k in locals() if k[:1] != "_"])
    """
    \\@since 0.3.37
    
    Returns list of all properties within the local class holding Minecraft durabilities
    """

MC_DURABILITY = _MC_DURABILITY()
"""
\\@since 0.3.26?

To 0.3.37 this constant was a dictionary holding keys being items, and their values being their durabilities. \\
Since 0.3.37 this constants is object of a local class holding final properties representing items in Minecraft.

If no suffix, item is universal (both Java and Bedrock), suffix `_j` means an item is only on Java, and suffix `_b` \\
means an item is only on Bedrock version of Minecraft.
"""

__version__ = VERSION
"""
\\@since 0.3.27a3

Returns currently used version of AveyTense
"""

ABROAD_HEX_INCLUDE = _AbroadHexMode.INCLUDE # 0.3.35
ABROAD_HEX_HASH = _AbroadHexMode.HASH # 0.3.35
ABROAD_HEX_EXCLUDE = _AbroadHexMode.EXCLUDE # 0.3.35

BISECT_LEFT = _BisectMode.LEFT # 0.3.35
BISECT_RIGHT = _BisectMode.RIGHT # 0.3.35

INSORT_LEFT = _InsortMode.LEFT # 0.3.35
INSORT_RIGHT = _InsortMode.RIGHT # 0.3.35

PROBABILITY_MIN = _ProbabilityLength.MIN # 0.3.35
PROBABILITY_MAX = _ProbabilityLength.MAX # 0.3.35
PROBABILITY_COMPUTE = _ProbabilityLength.COMPUTE # 0.3.35
PROBABILITY_DEFAULT = _ProbabilityLength.DEFAULT # 0.3.35

STRING_LOWER = "abcdefghijklmnopqrstuvwxyz" # 0.3.36
STRING_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" # 0.3.36
STRING_LETTERS = STRING_LOWER + STRING_UPPER # 0.3.36
STRING_HEXADECIMAL = "0123456789abcdefABCDEF" # 0.3.36
STRING_DIGITS = "0123456789" # 0.3.36
STRING_OCTAL = "01234567" # 0.3.36
STRING_BINARY = "01" # 0.3.36
STRING_SPECIAL = r"""`~!@#$%^&*()-_=+[]{};:'"\|,.<>/?""" # 0.3.36

MODE_AND = _ModeSelection.AND # 0.3.36
MODE_OR = _ModeSelection.OR # 0.3.36

RGB_MIN = 0 # 0.3.37
RGB_MAX = 2 ** 24 - 1 # 0.3.37
