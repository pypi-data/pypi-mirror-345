"""
**AveyTense Primal** \n
\\@since 0.3.24 \\
© 2023-Present Aveyzan // License: MIT
```ts
module aveytense._primal
```
To 0.3.26rc3 module `tense.primary`.

This module holds these 2 special functions: `abroad()` and  `reckon()`, \\
crucial AveyTense declarations, which are equivalents to Python functions \\
`range()` and `len()`.

"""

import sys as _sys

import datetime as _datetime
import decimal as _decimal
import fractions as _fractions
import math as _math
import numbers as _numbers
import tkinter as _tkinter
import warnings as _warnings

from . import _abroad as _ab_mod
from . import _constants as _lconstants
from .. import constants as _constants
from .. import types_collection as _tc
from .. import util as _util

__module__ = "tense"
# between @since and @author there is unnecessarily long line spacing
# hence this warning is being thrown; it is being disabled.
_warnings.filterwarnings("ignore", category = SyntaxWarning)

# types
_var = _tc.TypeVar

_T = _var("_T")
_T_fi = _var("_T_fi", int, float) # Bound to float/int
_T1 = _var("_T1")
_T2 = _var("_T2")
_T3 = _var("_T3")

RAM = int
_RAM = _tc.MutableSequence[RAM]
_MODE_AND = _constants.MODE_AND
_MODE_OR = _constants.MODE_OR
_Ellipsis = _tc.EllipsisType
_Mode = _tc.Union[_lconstants.ModeSelection, _tc.Literal["and", "or"]]
_ReckonTypePre = _ab_mod.ReckonType[_T]
_ReckonNGTPre = _ab_mod.ReckonNGT
_AbroadValue1Pre = _ab_mod.AbroadValue1[_T]
_AbroadValue2Pre = _ab_mod.AbroadValue2[_T]
_AbroadModifierPre = _ab_mod.AbroadModifier[_T]
_FloatOrInteger = _tc.FloatOrInteger
_OptionalFloatOrInteger = _tc.Union[_FloatOrInteger, _tc.EllipsisType]
_OptionalInteger = _tc.Union[int, _tc.EllipsisType]
_TenseVersionType = _tc.TenseVersionType[int]


def _domain_checker(x: _FloatOrInteger, f: _tc.Literal["asin", "acos", "asec", "acosec"] = "asin"): # 0.3.38
    
    if f in ("asin", "acos") and (x < -1 or x > 1):
        
        error = ValueError("bad math domain, expected value in range [-1; 1]")
        raise error
    
    elif f in ("asec", "acosec") and abs(x) < 1:
        
        error = ValueError("bad math domain, expected value not in range (-1; 1)")
        raise error
    
    return True
        

@_util.final
class _TenseVersion(_tc.ComparableWithoutIn):
    """
    \\@since 0.3.25
    ```ts
    in module tense._primal
    ```
    Special class for Tense version checking
    """
    __local_version = _constants.VERSION_INFO
    @property
    def major(self): return _constants.VERSION_INFO.major
    
    @property
    def minor(self): return _constants.VERSION_INFO.minor
    
    @property
    def micro(self): return _constants.VERSION_INFO.micro
    
    @property
    def releaselevel(self): return _constants.VERSION_INFO.releaselevel
    
    @property
    def serial(self): return _constants.VERSION_INFO.serial # note we handle 'final' so it should return zero
        
    STRING_VER = _constants.VERSION # since 0.3.26b2
    """
    \\@since 0.3.26b3
    ```
    const in class _TenseVersion
    ```
    Returns current Tense version as a string. \\
    *Warning*: it is managed automatically, and \\
    hence it shouldn't be changed.
    """
    @classmethod
    def receive(self):
        """
        \\@since 0.3.25
        ```ts
        "class method" in class _TenseVersion
        ```
        Returns current Tense version
        """
        return self.__local_version
    def __ge__(self, other: _TenseVersionType):
        """
        \\@since 0.3.26b3
        ```
        'operator >=' in class _TenseVersion
        ```
        Comparison: Check whether version is greater than or equal current one.
        """
        return (
            other[0] >= self.major or
            other[1] >= self.minor or
            other[2] >= self.micro
        )
    def __le__(self, other: _TenseVersionType):
        """
        \\@since 0.3.26b3
        ```
        'operator <=' in class _TenseVersion
        ```
        Comparison: Check whether version is least than or equal current one.
        """
        return (
            other[0] <= self.major or
            other[1] <= self.minor or
            other[2] <= self.micro
        )
    def __gt__(self, other: _TenseVersionType):
        """
        \\@since 0.3.26b3
        ```
        'operator >' in class _TenseVersion
        ```
        Comparison: Check whether version is greater than current one.
        """
        return (
            other[0] > self.major or
            other[1] > self.minor or
            other[2] > self.micro
        )
    def __lt__(self, other: _TenseVersionType):
        """
        \\@since 0.3.26b3
        ```
        'operator <' in class _TenseVersion
        ```
        Comparison: Check whether version is least then current one.
        """
        return (
            other[0] < self.major or
            other[1] < self.minor or
            other[2] < self.micro
        )
    def __eq__(self, other: _TenseVersionType):
        """
        \\@since 0.3.26b3
        ```
        'operator ==' in class _TenseVersion
        ```
        Comparison: Check whether version is equal the current one.
        """
        return (
            other[0] == self.major and
            other[1] == self.minor and
            other[2] == self.micro
        )
    def __ne__(self, other: _TenseVersionType):
        """
        \\@since 0.3.26b3
        ```
        'operator !=' in class _TenseVersion
        ```
        Comparison: Check whether version is inequal to the current one.
        """
        return (
            other[0] != self.major or
            other[1] != self.minor or
            other[2] != self.micro
        )

_TENSE_VERSION = _TenseVersion()
"""
\\@since 0.3.24
```
in module aveytense
```
Return currently used Tense version as a tuple. \\
Since 0.3.25 returns instance of local class `_TenseVersion`, \\
hence to gain version as a tuple, use class method `receive()`.

No longer public since 0.3.34, instead use `Tense.version` or `tenseVersion()`.
"""
def tenseVersion(asTuple = False):
    """
    \\@since 0.3.8
    ```
    def tenseVersion(asTuple = False): ...
    from aveytense import tenseVersion
    ``` \n
    ``` \n
    # since 0.3.24
    def tenseVersion(asTuple: bool = False): ...
    # before 0.3.24
    def tenseVersion(): ...
    ```
    Returns Tense version installed. Ensure you have version up-to-date to make everything actually working. If optional parameter \\
    is set to `True`, returned is tuple with 3 items, which together compose version of Tense. This argument is also responsible for \\
    deletion of global function `tenseVersionAsTuple()` on 0.3.24.
    """
    if asTuple: return _TENSE_VERSION.receive()
    else: return _TENSE_VERSION.STRING_VER


# declarations

# class Tense08AbroadRadex(object):
"""
    `Tense08AbroadRadex`
    ++++
    https://aveyzan.glitch.me/tense/08/class.Tense08AbroadRadex.html \\
    \\@since 0.3.12, to 0.3.24 \\
    \\@standard-since 0.3.12 \\
    \\@last-change 0.3.24

    Appendix to the last parameter in `abroad()` method.
    """
    # __arr: list[int] = []
    # @classmethod
    # def __new__(self, *values: int):
    #    i = 0
    #    while i < len(values):
    #        self.__arr.append(values[i])
    #        i += 1
    # @classmethod
    # def retrieve(self): return self.__arr

def _reckon_prepend_init(*countables: _ReckonTypePre[_T]):
    
    i = 0
    for e in countables:
        
        if isinstance(e, _tc.IO):
            
            try:
                for _ in e.read():
                    i += 1
            except:
                pass
            
        # elif isinstance(e, _tkinter.StringVar): # < 0.3.39
        #    i += len(e.get())
            
        elif isinstance(e, _tc.Iterable):
            
            for _ in e:
                i += 1
                
        elif isinstance(e, _tc.Sizeable):
            i += len(e)
            
        elif isinstance(e, _tc.ReckonOperable):
            i += e.__reckon__()
            
        else:
            error = TypeError("expected sizeable or iterable object, or object of class extending '{}' base class".format(_tc.ReckonOperable.__name__))
            raise error
        
    return i

def _reckon_init(*countables: _ReckonTypePre[_T]):
    return _reckon_prepend_init(*countables)


class _AbroadInitializer:
    """
    \\@since 0.3.28
    
    Better identifier for returned sequence from `abroad()` function
    """
    def __new__(cls, seq: _tc.Iterable[int], v1: int, v2: int, m: int, /):
        return _ab_mod.AbroadInitializer(seq, v1, v2, m)
    

def _abroad_prepend_init(value1: _AbroadValue1Pre[_T1], /, value2: _AbroadValue2Pre[_T2] = None, modifier: _AbroadModifierPre[_T3] = None):
    
    _pre = (_tc.IO, _tc.Iterable, _tc.ReckonOperable, _tc.Sizeable)
    
    conv, v1, v2, m = [0], 0, 0, 0
    del conv[0]
    
    # v1 (value1)
    if isinstance(value1, _pre):
        v1 = _reckon_init(value1)
        
    elif isinstance(value1, int):
        v1 = value1
        
    elif isinstance(value1, float):
        
        if value2 in (_math.inf, _math.nan):
            error = _tc.IncorrectValueError("'inf' or 'nan' as value for 'value1' (1st parameter) is not allowed.")
            raise error
        
        else:
            v1 = _math.trunc(value1)
            
    elif isinstance(value1, complex):
        v1 = _math.trunc(value1.real)
        
    else:
        error = TypeError("Missing value or invalid type of 'value1' (1st parameter). Used type '{}' does not match any of types, which are allowed in this parameter.".format(type(value1).__name__))
        raise error
    
    # v2 (value2)
    if isinstance(value2, _pre):
        v2 = _reckon_init(value2)
        
    elif isinstance(value2, (bool, _Ellipsis)) or value2 is None:
        
        if isinstance(value1, complex):
            v2 = _math.trunc(value1.imag)
            
        else:
            v2 = v1
            
    elif isinstance(value2, int):
        v2 = value2
        
    elif isinstance(value2, float):
        
        if value2 in (_math.inf, _math.nan):
            error = _tc.IncorrectValueError("'inf' or 'nan' as value for 'value2' (2nd parameter) is not allowed.")
            raise error
        
        else:
            v2 = _math.trunc(value2)
    else:
        error = TypeError("Invalid type of 'value2' (2nd parameter). Used type '{}' does not match any of types, which are allowed in this parameter.".format(type(value2).__name__))
        raise error
    
    # m (modifier)
    if isinstance(modifier, _pre):
        
        m = _reckon_init(modifier)
        
        if m == 0:
            m = 1
            
    elif isinstance(modifier, int):
        
        if modifier == 0:
            m = 1
            
        else:
            m = abs(modifier)
            
        if m == 0:
            m = 1
            
    elif isinstance(modifier, float):
        
        if modifier == _math.inf:
            error = _tc.IncorrectValueError("'inf' as value for 'modifier' (3rd parameter) is not allowed")
            raise error
        
        elif modifier == _math.nan:
            m = 1
            
        else:
            m = abs(_math.trunc(modifier))
            if m == 0: m = 1
            
    elif isinstance(modifier, complex):
        
        m = _math.trunc(modifier.real) + _math.trunc(modifier.imag)
        
        if m < 0:
            m = abs(m)
            
        elif m == 0:
            m = 1
            
    elif isinstance(modifier, _Ellipsis) or modifier is None:
        m = 1
        
    else:
        error = TypeError("Invalid type of 'modifier' (3rd parameter). Used type '{}' does not match any of types, which are allowed in this parameter.".format(type(modifier).__name__))
        raise error
    
    # iteration begins
    if (v1 == v2 or isinstance(value1, complex)) and (isinstance(value2, bool) or value2 is None):
        
        if isinstance(value1, complex):
            
            v1 = _math.trunc(value1.real)
            v2 = _math.trunc(value1.imag)
            
            if v1 < v2:
                
                i = v1
                
                while i < v2:
                    
                    if value2 is False:
                        conv.append(-i - 1)
                        
                    else:
                        conv.append(i)
                        
                    i += m
            else:
                
                i = v1
                
                while i > v2:
                    
                    if value2 is False:
                        conv.append(-i - 1)
                        
                    else:
                        conv.append(i)
                        
                    i -= m
                    
            if value2 is False:
                conv.reverse()
                
        else:
            
            if v1 > 0:
                
                i = 0
                
                while i < v1:
                    
                    if value2 is False:
                        conv.append(-i - 1)
                        
                    else:
                        conv.append(i)
                        
                    i += m
            else:
                
                i = v1
                
                while i < 0:
                    
                    if value2 is False:
                        conv.append(-i - 1)
                        
                    else:
                        conv.append(i)
                        
                    i += m
                    
            if value2 is False:
                conv.reverse()
                
        # earlier: return conv (< 0.3.28)
        return _AbroadInitializer(
            conv,
            0 if v1 == v2 else v1,
            v1 if v1 == v2 else v2,
            m
        )
        
    if isinstance(value2, float):
        
        if v2 >= 0 or (v1 < 0 and v2 < 0):
            v2 += 1
            
        else:
            v2 -= 1
            
    if v1 < v2:
        
        i = v1
        
        while i < v2:
            conv.append(i)
            i += m
    else:
        
        i = v1
        
        while i > v2:
            conv.append(i)
            i -= m
            
    # earlier: return conv (< 0.3.28)
    return _AbroadInitializer(conv, v1, v2, m)

def _abroad_init(value1: _AbroadValue1Pre[_T1], /, value2: _AbroadValue2Pre[_T2] = None, modifier: _AbroadModifierPre[_T3] = None):
    return _abroad_prepend_init(value1, value2, modifier)

class Time:
    """
    \\@since 0.3.25
    ```
    # created 04.07.2024
    class Time: ...
    from aveytense import Time
    ```
    Access to time
    """
    
    __forced_unix_year_range = False
    @classmethod
    def forceUnixYearRange(self, option = False, /):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Forces year range to 1st Jan 1970 - 19th Jan 2038. \\
        If set to `False`, it is reset.
        """
        self.__forced_unix_year_range = option
        return self
    
    @classmethod
    def fencordFormat(self):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Returned is present time in `tense.fencord.Fencord` class format.
        Formatted as `%Y-%m-%d %H:%M:%S`. Timezone is user's local timezone. \\
        This format also uses `discord` module.
        """
        return _datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def isLeapYear(self, year: int):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Returned is `True` only when:
        - year is an integer and is positive (above 0)
        - year is divisible by 4 and not divisible by 100 or year is divisible by 400
        - if Unix year range is enforced, only years in range 1970 - 2038

        If none of these requirements are granted, returned is `False`.
        """
        b = ((isinstance(year, int) and year >= 1) and (year % 4 == 0 and year % 100 != 0) or year % 400 == 0)
        if self.__forced_unix_year_range: b = b and (year >= 1970 and year <= 2038)
        return b
    
    @classmethod
    def verifyDate(self, year: int, month: int, day: int):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Returned is `True` only when every parameter is an integer and year is from 1 up, \\
        month is from 1 up and day is from 1 up, and one of these statements are granted:
        - day has value 31 for months: 1, 3, 5, 7, 8, 10, 12
        - day has value 30 for every month in range 1-12 excluding 2
        - day has value 29 for every month in range 1-12, for 2 only if year is leap
        - day is in range 1-28 for every month in range 1-12
        - additionally, if Unix year range is enforced, year is in range 1970-2038

        If none of these requirements are granted, returned is `False`.
        """
        return (
                isinstance(year, int) and isinstance(month, int) and isinstance(day, int)) and (year >= 1 and month >= 1 and day >= 1) and (
                (day == 31 and month in (1, 3, 5, 7, 8, 10, 12)) or (day == 30 and month in set(_abroad_init(1, 12.1)).difference({2})) or
                (day == 29 and month in _abroad_init(1, 12.1) and self.isLeapYear(year)) or (day < 29 and month in _abroad_init(1, 12.1))
            )
                
    @classmethod
    def getMillennium(self):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Returns current millennium. Expected would be only `return 3`, \\
        but code itself in reality verifies current date and what not.
        """
        return _math.trunc(int(_datetime.datetime.now().strftime("%Y")) / 1000) + 1
    
    @classmethod
    def getCentury(self):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Returns current century. Expected would be only `return 21`, \\
        but code itself in reality verifies current date and what not.
        """
        return _math.trunc(int(_datetime.datetime.now().strftime("%Y")) / 100) + 1
    
    @classmethod
    def getDecade(self):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Returns current decade. Warning: it does not return something like \\
        3rd decade of 21st century, but decade in overall, which have elapsed \\
        since Anno Domini time period. So what that means: for 2024 (4th July \\
        2024, when created this method) returned is 203.

        It does not match 0-to-9 decades, but 1-to-0, so 203 will be returned \\
        by years in range 2021-2030 (not in 2020-2029), including both points.
        """
        return _math.trunc(int(_datetime.datetime.now().strftime("%Y")) / 10) + 1
    
    @classmethod
    def getYear(self):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Returns current year
        """
        return int(_datetime.datetime.now().strftime("%Y"))
    
    @classmethod
    def getMonth(self):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Returns current month
        """
        return int(_datetime.datetime.now().strftime("%m"))
    
    @classmethod
    def getDay(self):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Returns current day. Basing on local timezone.
        Warning: This doesn't return day of the year \\
        or day of the week, but only day of the month
        """
        return int(_datetime.datetime.now().strftime("%d"))
    
    @classmethod
    def getHour(self):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Returns current hour. Basing on local timezone.
        """
        return int(_datetime.datetime.now().strftime("%H"))
    
    @classmethod
    def getMinute(self):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Returns current minute. Basing on local timezone.
        """
        return int(_datetime.datetime.now().strftime("%M"))
    
    @classmethod
    def getSecond(self):
        """
        \\@since 0.3.25
        ```
        # created 04.07.2024
        "class method" in class Time
        ```
        Returns current second. Basing on local timezone.
        """
        return int(_datetime.datetime.now().strftime("%S"))
    
    __all__ = [n for n in locals() if n[:1] != "_"]
    "\\@since 0.3.26c2"
    
class Math:
    """
    \\@since 0.3.25
    ```
    # created 04.07.2024
    class Math: ...
    from aveytense import Math
    ```
    Math methods and constants
    """
    PI = _constants.MATH_PI
    """
    \\@since 0.3.25
    ```
    # created 04.07.2024
    const in class Math
    ```
    Value of irrational constant π (pi). This well-known constant \\
    is used in circles, that is ratio of its circumference to its diameter. \\
    First use of this letter was found in the essay written by William \\
    Jones back on 1706.
    """
    E = _constants.MATH_E
    """
    \\@since 0.3.25
    ```
    # created 04.07.2024
    const in class Math
    ```
    Value of irrational constant `e`. Known as Euler's constant \\
    or Napier's constant. Who knows, maybe its definition should \\
    have forenames of both mathematicians, like Euler-Napier's \\
    constant? However, back then on 1683, Swiss mathematician \\
    Jacob Bernoulli was the first person to discover `e`. It could \\
    be an interesting subject to conduct.
    """
    INF = _constants.MATH_INF
    """
    \\@since 0.3.25
    ```
    # created 05.07.2024
    const in class Math
    ```
    Infinity
    """
    NAN = _constants.MATH_NAN
    """
    \\@since 0.3.25
    ```
    # created 05.07.2024
    const in class Math
    ```
    Not a number
    """
    TAU = _constants.MATH_TAU
    """
    \\@since 0.3.25
    ```
    # created 05.07.2024
    const in class Math
    ```
    Value of irrational constant τ (tau)
    """
    SQRT2 = _constants.MATH_SQRT2
    """
    \\@since 0.3.25
    ```
    # created 05.07.2024
    const in class Math
    ```
    Square root of 2. Reference from JavaScript: `Math.SQRT2`
    """
    CENTILLION = _constants.MATH_CENTILLION
    """
    \\@since 0.3.25
    ```
    # created 19.07.2024
    const in class Math
    ```
    `1e+303`
    """
    
    @classmethod
    def isNegative(self, x: _tc.Union[_FloatOrInteger, _tc.Sequence[_FloatOrInteger]], /):
        """
        \\@since 0.3.31 (no doc yet)
        
        Check whether a number is negative. If provided is a sequence, \\
        each number in it must satisfy this condition.
        """
        
        if not isinstance(x, (int, float, _tc.Sequence)):
            error = TypeError("expected a number (integer or float) or sequence of numbers")
            raise error
        
        elif isinstance(x, (int, float)):
            return x < 0
        
        else:
            
            for e in x:
                
                if not isinstance(e, (int, float)):
                    error = TypeError("expected a number (integer or float) or sequence of numbers")
                    raise error
            
            _r = [e for e in x if e < 0]
            return _reckon_init(_r) == _reckon_init(x)
                
    
    @classmethod
    def isPositive(self, x: _tc.Union[_FloatOrInteger, _tc.Sequence[_FloatOrInteger]], /):
        """
        \\@since 0.3.31 (no doc yet)
        
        Check whether a number is positive. If provided is a sequence, \\
        each number in it must satisfy this condition.
        """
        
        if not isinstance(x, (int, float, _tc.Sequence)):
            error = TypeError("expected a number (integer or float) or sequence of numbers")
            raise error
        
        elif isinstance(x, (int, float)):
            return x > 0
        
        else:
            
            for e in x:
                
                if not isinstance(e, (int, float)):
                    error = TypeError("expected a number (integer or float) or sequence of numbers")
                    raise error
            
            _r = [e for e in x if e > 0]
            return _reckon_init(_r) == _reckon_init(x)
    
    @classmethod
    def isPrime(self, x: int, /):
        """
        \\@since 0.3.31 (no doc yet)
        
        Check whether an integer is prime
        """
        if not isinstance(x, int) or (isinstance(x, int) and self.isNegative(x)):
            error = TypeError("expected a positive integer")
            raise error
        
        if x in (0, 1):
            return False
        
        for i in _abroad_init(2, x):
            
            if x % i == 0:
                return False
            
        return True
    
    @classmethod
    def isComposite(self, x: int, /):
        """
        \\@since 0.3.31 (no doc yet)
        
        Check whether an integer is composite
        """
        if not isinstance(x, int) or (isinstance(x, int) and self.isNegative(x)):
            error = TypeError("expected a positive integer")
            raise error
        
        if x in (0, 1):
            return False
        
        return not self.isPrime(x)
    
    @classmethod
    def isInRange(self, x: _tc.Union[_FloatOrInteger, _tc.Sequence[_FloatOrInteger]], a: _FloatOrInteger, b: _FloatOrInteger, /, mode = "c"):
        """
        \\@since 0.3.36 https://aveyzan.glitch.me/tense#aveytense.Math.isInRange
        
        Returns `True`, if number(s) are in specific range [a; b]. \\
        For empty sequences returned is `False`.
        
        On 0.3.39 added optional parameter `mode` to modify intervals:
        - `"c"` (default value) / `"cc"` = `<a; b>` = `a <= x <= b`
        - `"co"` = `<a; b)` = `a <= x < b`
        - `"o"` / `"oo"` = `(a; b)` = `a < x < b`
        - `"oc"` = `(a; b>` = `a < x <= b`
        """
        
        # 0.3.41: Excluding inf and nan
        if all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in [a, b]]):
            
            _mode = mode.lower()
            
            # 0.3.41: Brackets
            if _mode not in ("c", "cc", "oc", "co", "o", "oo"):
                error = TypeError("expected an approriate string value in parameter 'mode' from following: 'c', 'cc', 'oc', 'co', 'o', 'oo' (case insensitive), '[]', '[)', '(]', '()'")
                raise error
        
            _range = [a, b]
            
            if a > b:
                _range.reverse()
            
            if isinstance(x, (int, float)):
                
                if _mode in ("c", "cc"):
                    return x >= _range[0] and x <= _range[1]
                
                elif _mode in ("co",):
                    return x >= _range[0] and x < _range[1]
                
                elif _mode in ("oc",):
                    return x > _range[0] and x <= _range[1]
                
                else:
                    return x > _range[0] and x < _range[1]
            
            elif isinstance(x, _tc.Sequence) and all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
                
                if _reckon_init(x) == 0:
                    return False
                
                _placeholder = True
                
                for e in x:
                    
                    if _mode in ("c", "cc",):
                        _placeholder = _placeholder and (e >= _range[0] and e <= _range[1])
                        
                    elif _mode in ("co",):
                        _placeholder = _placeholder and (e >= _range[0] and e < _range[1])
                        
                    elif _mode in ("oc",):
                        _placeholder = _placeholder and (e > _range[0] and e <= _range[1])
                        
                    else:
                        _placeholder = _placeholder and (e > _range[0] and e < _range[1])
                    
                return _placeholder
        
        error = TypeError("expected 'x' as integer/float or sequence of integers and floats, 'a' and 'b' as integers or floats, all excluding infinity and NaN")
        raise error
                
    
    @classmethod
    def isIncreasing(self, x: _tc.Sequence[_FloatOrInteger], /):
        """
        \\@since 0.3.38 (no doc yet)
        
        Returns `True` if sequence has positive difference for consecutive members, \\
        and has at least 3 integer items.
        """
        
        if isinstance(x, _tc.Sequence) and all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
        
            if _reckon_init(x) < 3:
                return False
            
            _placeholder = True
            
            for i in _abroad_init(_reckon_init(x) - 1):
                
                _placeholder = _placeholder and x[i + 1] - x[i] > 0
                
            return _placeholder
            
            
        error = TypeError("expected a number sequence with at least 3 items, without infinity and NaN")
        raise error
    
    @classmethod
    def isDecreasing(self, x: _tc.Sequence[_FloatOrInteger], /):
        """
        \\@since 0.3.38 (no doc yet)
        
        Returns `True` if sequence has negative difference for consecutive members, \\
        and has at least 3 number items.
        """
        
        if isinstance(x, _tc.Sequence) and all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
        
            if _reckon_init(x) < 3:
                return False
            
            _placeholder = True
            
            for i in _abroad_init(_reckon_init(x) - 1):
                
                _placeholder = _placeholder and x[i + 1] - x[i] < 0
                
            return _placeholder
            
        error = TypeError("expected a number sequence with at least 3 items, without infinity and NaN")
        raise error
    
    @classmethod
    def isConstant(self, x: _tc.Sequence[_FloatOrInteger], /):
        """
        \\@since 0.3.38 (no doc yet)
        
        Returns `True` if sequence has difference equal 0 for consecutive members, \\
        and has at least 3 number items.
        """
        
        if isinstance(x, _tc.Sequence) and all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
        
            if _reckon_init(x) < 3:
                return False
            
            _placeholder = True
            
            for i in _abroad_init(_reckon_init(x) - 1):
                
                _placeholder = _placeholder and x[i + 1] - x[i] == 0
                
            return _placeholder
            
        error = TypeError("expected a number sequence with at least 3 items, without infinity and NaN")
        raise error
    
    @classmethod
    def isNonIncreasing(self, x: _tc.Sequence[_FloatOrInteger], /):
        """
        \\@since 0.3.38 (no doc yet)
        
        Returns `True` if sequence has negative difference or equal 0 for consecutive members, \\
        and has at least 3 number items.
        """
        
        if isinstance(x, _tc.Sequence) and all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
        
            if _reckon_init(x) < 3:
                return False
            
            _placeholder = True
            
            for i in _abroad_init(_reckon_init(x) - 1):
                
                _placeholder = _placeholder and x[i + 1] - x[i] <= 0
                
            return _placeholder
            
        error = TypeError("expected a number sequence with at least 3 items, without infinity and NaN")
        raise error
    
    @classmethod
    def isNonDecreasing(self, x: _tc.Sequence[_FloatOrInteger], /):
        """
        \\@since 0.3.38 (no doc yet)
        
        Returns `True` if sequence has positive difference or equal 0 for consecutive members, \\
        and has at least 3 number items.
        """
        
        if isinstance(x, _tc.Sequence) and all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
        
            if _reckon_init(x) < 3:
                return False
            
            _placeholder = True
            
            for i in _abroad_init(_reckon_init(x) - 1):
                
                _placeholder = _placeholder and x[i + 1] - x[i] >= 0
                
            return _placeholder
            
        error = TypeError("expected a number sequence with at least 3 items, without infinity and NaN")
        raise error
    
    @classmethod
    def isMonotonous(self, x: _tc.Sequence[_FloatOrInteger], /):
        """
        \\@since 0.3.38 (no doc yet)
        
        Returns `True`, if sequence is monotonous (is either increasing, \\
        decreasing, constant, non-decreasing or non-increasing).
        """
        
        if not isinstance(x, _tc.Sequence) or not all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
            error = TypeError("expected a number sequence with at least 3 items, without infinity and NaN")
            raise error
        
        return self.isIncreasing(x) or self.isDecreasing(x) or self.isConstant(x) or self.isNonDecreasing(x) or self.isNonIncreasing(x)
    
    
    @classmethod
    @_tc.overload
    def isFraction(self, o: _tc.Any, /) -> _tc.TypeIs[_fractions.Fraction]: ...
    
    @classmethod
    @_tc.overload
    def isFraction(self, o: _tc.Any, /, *_: _tc.Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isFraction(self, o, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.41
        
        Returns `True`, if value is instance of class `fractions.Fraction`.
        """
        
        if _reckon_init(_) == 0:
            return type(o) is _fractions.Fraction
        
        else:
            _many = (o,) + _
            
            if mode in (_constants.MODE_OR, "or"):
                return any([type(e) is _fractions.Fraction for e in _many])
            
            elif mode in (_constants.MODE_AND, "and"):
                return all([type(e) is _fractions.Fraction for e in _many])
            
            else:
                return False
            
            
    @classmethod
    @_tc.overload
    def isDecimal(self, o: _tc.Any, /) -> _tc.TypeIs[_decimal.Decimal]: ...
    
    @classmethod
    @_tc.overload
    def isDecimal(self, o: _tc.Any, /, *_: _tc.Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isDecimal(self, o, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.38
        
        Returns `True`, if value is decimal string (since 0.3.41 - `~.Tense.isDecimalString()`).
        - since 0.3.41: -  ^  - is instance of class `decimal.Decimal`.
        """
        
        if _reckon_init(_) == 0:
            return type(o) is _decimal.Decimal
        
        else:
            _many = (o,) + _
            
            if mode in (_constants.MODE_OR, "or"):
                return any([type(e) is _decimal.Decimal for e in _many])
            
            elif mode in (_constants.MODE_AND, "and"):
                return all([type(e) is _decimal.Decimal for e in _many])
            
            else:
                return False
            
            
    @classmethod
    @_tc.overload
    def isNumber(self, o: _tc.Any, /) -> _tc.TypeIs[_numbers.Number]: ...
    
    @classmethod
    @_tc.overload
    def isNumber(self, o: _tc.Any, /, *_: _tc.Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isNumber(self, o, /, *_, mode = _MODE_AND):
        """
        \\@since 0.3.41
        
        Returns `True` for any number
        """
        
        # _tuple = (_numbers.Number, _decimal.Decimal, _fractions.Fraction, _tc.Indexable, _tc.IntegerConvertible, _tc.FloatConvertible, _tc.ComplexConvertible, int, float, complex)
        
        if reckon(_) == 0:
            
            return isinstance(o, _numbers.Number)
        
        else:
            
            _many = (o,) + _
            
            if mode in (_constants.MODE_AND, "and"):
                
                return all([isinstance(e, _numbers.Number) for e in _many])
            
            elif mode in (_constants.MODE_OR, "or"):
                
                return any([isinstance(e, _numbers.Number) for e in _many])
            
            else:
                
                return False
    
    
    @classmethod
    def fib(self, n: int, /):
        """
        \\@since 0.3.41 (3rd March 2025)
        
        Allows to return specific number from Fibonacci's sequence, using `n` index. \\
        To formalize Fibonacci's sequence, use `[~.fib(i) for i in abroad(n)]`.
        """
        if type(n) is not int or n < 1:
            error = TypeError("expected integer value above zero")
            raise error
        
        n1, n2, _next, i = 0, 1, 1, 1
        
        while i <= n:
            i += 1
            n1, n2 = n2, _next
            _next = n1 + n2
            
        return _next
        
        
    @classmethod
    def fact(self, n: int, /):
        """
        \\@since 0.3.26rc3 https://aveyzan.glitch.me/tense#aveytense.Math.fact
        ```
        # created 20.08.2024
        "class method" in class Math
        ```
        Return `n!`
        """
        
        # CHANGEOVER 0.3.39
        if not isinstance(n, int) or (isinstance(n, int) and n < 0):
            error = TypeError("expected a non-negative integer")
            raise error
        
        # math.factorial(): since Python 2.6
        if hasattr(_math, "factorial"): 
            return _math.factorial(n)
        
        else:
            
            if n in (0, 1):
                return 1
            
            m, i = 2, 3
            
            # 0.3.41: Do not use 'for' loop in order to bypass limit of 'sys.maxsize'
            while i <= n: 
                m *= i
                i += 1
                
            return m
    
    @classmethod
    @_tc.deprecated("deprecated since 0.3.39, will be removed on 0.3.48")
    def outOfRoot(self, number: int, rootScale: int, /):
        """Since 0.3.?"""
        i = number
        while not isinstance(pow(number, 1/rootScale), int): i -= 1
        return [int(pow(i, 1/rootScale)), number - i]
    
    @classmethod
    def asin(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.asin
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns arc sine of `x` \\
        Result is in range [-π/2; π/2]
        """
        _domain_checker(x, "asin")
        
        return _math.asin(x)
    
    @classmethod
    def acos(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.acos
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns arc cosine of `x` \\
        Result is in range [0, π]
        """
        _domain_checker(x, "acos")
        
        return _math.acos(x)
    
    @classmethod
    def atan(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.atan
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns arc tangent of `x` \\
        Result is in range (-π/2; π/2)
        """
        
        # _domain_checker not required since x can be any real number
        
        return _math.atan(x)
    
    @classmethod
    def asinh(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.asinh
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns inverse hyperbolic sine of `x`
        """
        return _math.asinh(x)
    
    @classmethod
    def acosh(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.acosh
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns inverse hyperbolic cosine of `x`
        """
        return _math.acosh(x)
    
    @classmethod
    def atanh(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.atanh
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns inverse hyperbolic tangent of `x`
        """
        return _math.atanh(x)
    
    @classmethod
    def sin(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.sin
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns sine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.sin(x)
    
    @classmethod
    def cos(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.cos
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns cosine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.cos(x)
    
    @classmethod
    def tan(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.tan
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns tangent of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.tan(x)
    
    @classmethod
    def sinh(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.sinh
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns hyperbolic sine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.sinh(x)
    
    @classmethod
    def cosh(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.cosh
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns hyperbolic cosine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.cosh(x)
    
    @classmethod
    def tanh(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.tanh
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns hyperbolic tangent of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.tanh(x)
    
    @classmethod
    def cosec(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.cosec
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns cosecant of `x`. `x` *cannot* be divisible by 90.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or self.sin(x) == 0:
            error = TypeError("expected a number whose sine isn't equal 0")
            raise error
        
        return 1 / self.sin(x)
    
    @classmethod
    def sec(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.sec
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns secant of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or self.cos(x) == 0:
            error = TypeError("expected a number whose cosine isn't equal 0")
            raise error
        
        return 1 / self.cos(x)
    
    @classmethod
    def acosec(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.acosec
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Returns inverse cosecant of `x`. Equals `asin(1 / x)`
        """
        _domain_checker(x, "acosec")
        
        return self.asin(1 / x)
    
    @classmethod
    def asec(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.asec
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Returns inverse secant of `x`. Equals `acos(1 / x)`
        """
        _domain_checker(x, "asec")
        
        return self.acos(1 / x)
    
    @classmethod
    def cot(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.cot
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns cotangent of `x`. That is inversed tangent
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or self.tan(x) == 0:
            error = TypeError("expected a number whose tangent isn't equal 0")
            raise error
        
        return 1 / self.tan(x)
    
    @classmethod
    def versin(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.versin
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns versed sine of `x`. That is 1 minus its cosine
        """
        return 1 - self.cos(x)
    
    @classmethod
    def coversin(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.coversin
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns coversed sine of `x`. That is 1 minus its sine
        """
        return 1 - self.sin(x)
    
    @classmethod
    def vercos(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.vercos
        ```
        # created 04.07.2024
        # renamed on 0.3.39 from ~.vercosin()
        "class method" in class Math
        ```
        Returns versed cosine of `x`. That is 1 plus its cosine
        """
        return 1 + self.cos(x)
    
    @classmethod
    def covercos(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.covercos
        ```
        # created 04.07.2024
        # renamed on 0.3.39 from ~.covercosin()
        "class method" in class Math
        ```
        Returns coversed cosine of `x`. That is 1 plus its sine
        """
        return 1 + self.sin(x)
    
    @classmethod
    def haversin(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.haversin
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns haversed sine of `x`. That is half of its versed sine
        """
        return self.versin(x) / 2
    
    @classmethod
    def havercos(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.havercos
        ```
        # created 04.07.2024
        # renamed on 0.3.39 from ~.havercosin()
        "class method" in class Math
        ```
        Returns haversed cosine of `x`. That is half of its coversed sine
        """
        return self.coversin(x) / 2
    
    @classmethod
    def hacoversin(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.hacoversin
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns hacoversed sine of `x`. That is half of its versed cosine
        """
        return self.vercos(x) / 2
    
    @classmethod
    def hacovercos(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.hacovercos
        ```
        # created 04.07.2024
        # renamed on 0.3.39 from ~.hacovercosin()
        "class method" in class Math
        ```
        Returns hacoversed cosine of `x`. That is half of its coversed cosine
        """
        return self.covercos(x) / 2
    
    @classmethod
    def aversin(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.aversin
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns inverse versed sine of `x`. Equals `acos(1 - x)`
        """
        _domain_checker(1 - x, "acos")
        
        return self.acos(1 - x)
    
    @classmethod
    def acoversin(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.acoversin
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns inverse coversed sine of `x`. Equals `acos(x - 1)`
        """
        _domain_checker(x - 1, "acos")
        
        return self.acos(x - 1)
    
    @classmethod
    def avercos(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.avercos
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns inverse versed cosine of `x`. Equals `asin(1 - x)`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) and not self.isInRange(x, 0, 2):
            error = TypeError("expected a number in range [0; 2]")
            raise error
        
        return self.asin(1 - x)
    
    @classmethod
    def acovercos(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.acovercos
        ```
        # created 04.07.2024
        "class method" in class Math
        ```
        Returns inverse coversed cosine of `x`. Equals `asin(x - 1)`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or not self.isInRange(x, 0, 2):
            error = TypeError("expected a number in range [0; 2]")
            raise error
        
        return self.asin(x - 1)
    
    @classmethod
    def ahaversin(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.ahaversin
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Returns inverse haversed sine of `x`. Equals `acos(1 - 2x)`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or not self.isInRange(x, 0, 1):
            error = TypeError("expected a number in range [0; 1]")
            raise error
        
        return self.acos(1 - (2 * x))
    
    @classmethod
    def ahavercos(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.ahavercos
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Returns inverse haversed cosine of `x`. Equals `acos(2x - 1)`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or not self.isInRange(x, 0, 1):
            error = TypeError("expected a number in range [0; 1]")
            raise error
        
        return self.acos(2 * x - 1)
    
    @classmethod
    def ahacoversin(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.ahacoversin
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Returns inverse hacoversed sine of `x`. Equals `asin(1 - 2x)`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or not self.isInRange(x, 0, 1):
            error = TypeError("expected a number in range [0; 1]")
            raise error
        
        return self.asin(1 - (2 * x))
    
    @classmethod
    def ahacovercos(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.ahacovercos
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Returns inverse hacoversed cosine of `x`. Equals `asin(2x - 1)`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or not self.isInRange(x, 0, 1):
            error = TypeError("expected a number in range [0; 1]")
            raise error
        
        return self.asin(2 * x - 1)
    
    @classmethod
    def exsec(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.exsec
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Returns exsecant of `x`. That is its secant minus 1
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or not self.cos(x) == 0:
            error = TypeError("expected a number whose cosine isn't equal 0")
            raise error
        
        return self.sec(x) - 1
    
    @classmethod
    def excosec(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.excosec
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Returns excosecant/coexsecant of `x`. That is its cosecant minus 1
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or not self.sin(x) == 0:
            error = TypeError("expected a number whose sine isn't equal 0")
            raise error
        
        return self.cosec(x) - 1
    
    @classmethod
    def aexsec(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.aexsec
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Returns inverse exsecant of `x`. Equals `asec(x + 1)`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or self.isInRange(x, -2, 0, "o"):
            error = TypeError("expected a number not in range (-2; 0); values -2 and 0 are allowed")
            raise error
        
        return self.asec(x + 1)
    
    @classmethod
    def aexcosec(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.aexcosec
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Returns inverse excosecant of `x`. Equals `acosec(x + 1)`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or self.isInRange(x, -2, 0, "o"):
            error = TypeError("expected a number not in range (-2; 0); values -2 and 0 are allowed")
            raise error
        
        return self.acosec(x + 1)
    
    @classmethod
    def log(self, x: _FloatOrInteger, /, base: _OptionalFloatOrInteger = ...): # slash since 0.3.39
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.log
        ```
        # created 05.07.2024
        ```
        Logarithm of `x` with specified base. If `base` is omitted, \\
        returned is logarithm of base e.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number in parameter 'x'")
            raise error
        
        if not isinstance(base, (int, float, _tc.EllipsisType)):
            error = TypeError("expected a number, 'None' or ellipsis in parameter 'base'")
            raise error
        
        _base = self.E if isinstance(base, _tc.EllipsisType) else base
        return _math.log(x, _base)
        
    @classmethod
    def log2(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.log
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Logarithm of `x` with base 2.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.log2(x)
    
    @classmethod
    def log3(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.log
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Logarithm of `x` with base 3.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return self.log(x, 3)
    
    @classmethod
    def log5(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.log
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Logarithm of `x` with base 5.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return self.log(x, 5)
    
    @classmethod
    def log7(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.log
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Logarithm of `x` with base 7.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return self.log(x, 7)
    
    @classmethod
    def ln(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.log
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Natural logarithm of `x`. That is logarithm with base `e`.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return self.log(x)
    
    @classmethod
    def log10(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.log
        ```
        # created 05.07.2024
        ```
        Logarithm of `x` with base 10.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.log10(x)
    
    @classmethod
    def sqrt(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.sqrt
        ```
        # created 05.07.2024
        ```
        Square root of `x`.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number not being infinity nor NaN")
            raise error
        
        return _math.sqrt(x)
    
    @classmethod
    def cbrt(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.25 https://aveyzan.glitch.me/tense#aveytense.Math.cbrt
        ```
        # created 05.07.2024
        ```
        Cube root of `x`. To 0.3.26c2 this method \\
        wouldn't throw an error if used is Python 3.11 \\
        or greater.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number not being infinity nor NaN")
            raise error
        
        if _sys.version_info >= (3, 11):
            return _math.cbrt(x)
        
        else:
            return _math.pow(x, (1/3))
        
    @classmethod
    def pow(self, x: _FloatOrInteger, y: _FloatOrInteger, /):
        """
        \\@since 0.3.25 (no doc yet)
        ```
        # created 05.07.2024
        ```
        Equals `x**y`(`x` to the power of `y`).
        """
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)) or any([e in (_math.inf, _math.nan) for e in [x, y]]):
            error = TypeError("both parameters 'x' and 'y' must be numbers not being infinity nor NaN")
            raise error
        
        return _math.pow(x, y)
    
    @classmethod
    def abs(self, x: _tc.Absolute[_T_fi], /) -> _T_fi:
        """
        \\@since ? (before 0.3.24)
        
        https://aveyzan.glitch.me/tense#aveytense.Math.abs
        
        Returns absolute value of a number. \\
        This method is stricter version of `abs()` inbuilt function.
        """
        if not isinstance(x, _tc.Absolute) or (isinstance(x, _tc.Absolute) and type(abs(x)) not in (int, float)):
            error = TypeError("expected a number or object of class implementing __abs__ returning either integer or floating-point number")
            raise error
        
        # safety checking, not all __abs__() method implementations return absolute value of a number
        # but it is just in case! abs() function can be manipulated easily with method __abs__()
        return abs(abs(x))


    @classmethod
    def trunc(self, x: _tc.Truncable[int], /):
        """
        \\@since 0.3.41 (4th March 2025; no doc yet)
        
        Returns an integer from a floating-point number, wiping out the fraction. \\
        This method is stricter version of `math.trunc()` inbuilt function.
        """
        
        if not isinstance(x, _tc.Truncable) or (isinstance(x, _tc.Truncable) and type(_math.trunc(x)) is not int):
            error = TypeError("expected a number or object of class implementing __trunc__ returning an integer")
            raise error
        
        # again, safety checking there
        return _math.trunc(_math.trunc(x))
    
    @classmethod
    def triangular(self, n: int, /):
        """
        \\@since 0.3.27a4 https://aveyzan.glitch.me/tense#aveytense.Math.triangular
        
        Return triangular number.
        """
        if not isinstance(n, int) or (isinstance(n, int) and n < 0):
            error = TypeError("expected a positive integer")
            raise error
        
        return int((n * (n + 1)) / 2)
    
    @classmethod
    def pentagonal(self, n: int, /):
        """
        \\@since 0.3.27a4 https://aveyzan.glitch.me/tense#aveytense.Math.pentagonal
        
        Return pentagonal number.
        """
        if not isinstance(n, int) or (isinstance(n, int) and n < 0):
            error = TypeError("expected a positive integer")
            raise error
        
        return int((3 * (n ** 2) - n) / 2)
    
    @classmethod
    def hexagonal(self, n: int, /):
        """
        \\@since 0.3.27a4 https://aveyzan.glitch.me/tense#aveytense.Math.hexagonal
        
        Return hexagonal number.
        """
        if not isinstance(n, int) or (isinstance(n, int) and n < 0):
            error = TypeError("expected a positive integer")
            raise error
        
        return int(((2 * n) * (2 * n - 1)) / 2)
    
    @classmethod
    def heptagonal(self, n: int, /):
        """
        \\@since 0.3.27a4 https://aveyzan.glitch.me/tense#aveytense.Math.heptagonal
        
        Return heptagonal number.
        """
        if not isinstance(n, int) or (isinstance(n, int) and n < 0):
            error = TypeError("expected a positive integer")
            raise error
        
        return int((5 * (n ** 2) - (3 * n)) / 2)
    
    @classmethod
    def octagonal(self, n: int, /):
        """
        \\@since 0.3.27a4 https://aveyzan.glitch.me/tense#aveytense.Math.octagonal
        
        Return octagonal number.
        """
        if not isinstance(n, int) or (isinstance(n, int) and n < 0):
            error = TypeError("expected a positive integer")
            raise error
        
        return int(3 * (n ** 2) - (2 * n))
    
    @classmethod
    def nonagonal(self, n: int, /):
        """
        \\@since 0.3.27a4 https://aveyzan.glitch.me/tense#aveytense.Math.nonagonal
        
        Return nonagonal number.
        """
        if not isinstance(n, int) or (isinstance(n, int) and n < 0):
            error = TypeError("expected a positive integer")
            raise error
        return int((n * (7 * n - 5)) / 2)
    
    @classmethod
    def decagonal(self, n: int, /):
        """
        \\@since 0.3.27a4 https://aveyzan.glitch.me/tense#aveytense.Math.decagonal
        
        Return decagonal number.
        """
        if not isinstance(n, int) or (isinstance(n, int) and n < 0):
            error = TypeError("expected a positive integer")
            raise error
        
        return int(4 * (n ** 2) - (3 * n))
    
    @classmethod
    def polygonal(self, n: int, s: int, /):
        """
        \\@since 0.3.27a4 https://aveyzan.glitch.me/tense#aveytense.Math.polygonal
        
        Return polygonal number, with defined amount of sides.
        """
        if (type(n) is not int or n < 0) or (type(s) is not int or s < 3):
            error = TypeError("expected a positive integer as first parameter and second parameter equal or greater than 3")
            raise error
        
        return int(((s - 2) * (n ** 2) - (s - 4) * n) * 0.5)
    
    @classmethod
    def diagonals(self, s: int, /, distinct = False):
        """
        \\@since 0.3.41 (6th March 2025; no doc yet)
        
        Return amount of diagonals in an equilateral polygon with defined amount of sides.
        """
        if type(s) is not int or s < 3:
            error = TypeError("expected at least 3 sides")
            raise error
        
        if distinct: # about distinct: https://en.wikipedia.org/wiki/Diagonal
            return int((s - 2) / 2)
        
        else:
            return int((s * (s - 3)) / 2)
    
    @classmethod
    def lcm(self, *i: int):
        """
        \\@since 0.3.31 https://aveyzan.glitch.me/tense#aveytense.Math.lcm
        
        Return least common multiple of provided integers
        """
        
        if _reckon_init(i) < 2 or (_reckon_init(i) >= 2 and not all([type(e) is int and not self.isNegative(e) for e in i])):
            error = ValueError("expected at least 2 non-negative integers")
            raise error
        
        if _sys.version_info >= (3, 9):
            return _math.lcm(*i)
        
        else:
            from functools import reduce # >= 2.6
            
            def _gcd(a: int, b: int):
                
                while b:      
                    a, b = b, a % b
                return a
            
            def _lcm(a: int, b: int):
                return a * b // _gcd(a, b)
            
            return reduce(_lcm, i)
        
    @classmethod
    def gcd(self, *i: int):
        """
        \\@since 0.3.31 https://aveyzan.glitch.me/tense#aveytense.Math.gcd
        
        Return greatest common divisor of provided integers
        """
        
        if _reckon_init(i) < 2 or (_reckon_init(i) >= 2 and not all([type(e) is int and not self.isNegative(e) for e in i])):
            error = ValueError("expected at least 2 non-negative integers")
            raise error
        
        if _sys.version_info >= (3, 9):
            return _math.gcd(*i)
        
        else:
            from functools import reduce # >= 2.6
            
            def _gcd(a: int, b: int):
                
                while b:
                    a, b = b, a % b
                return a
            
            return reduce(_gcd, i)
        
    @classmethod
    def toDigits(self, n: int, /):
        """
        \\@since 0.3.39 https://aveyzan.glitch.me/tense#aveytense.Math.toDigits
        
        Splits an integer to a digit list.
        """
        
        if not isinstance(n, int):
            error = TypeError("expected an integer")
            raise error
        
        if self.abs(n) < 10:
            return [self.abs(n)]
        
        return [int(c, base = 10) for c in str(self.abs(n))]
        
    @classmethod
    def minDigit(self, n: int, /):
        """
        \\@since 0.3.39 https://aveyzan.glitch.me/tense#aveytense.Math.minDigit
        
        Returns minimum digit in a number. Sign isn't counted.
        """
        
        if not isinstance(n, int):
            error = TypeError("expected an integer")
            raise error
        
        if self.abs(n) < 10:
            return self.abs(n)
        
        return min(self.toDigits(n))
    
    
    @classmethod
    def maxDigit(self, n: int, /):
        """
        \\@since 0.3.39 https://aveyzan.glitch.me/tense#aveytense.Math.maxDigit
        
        Returns maximum digit in a number. Sign isn't counted.
        """
        
        if not isinstance(n, int):
            error = TypeError("expected an integer")
            raise error
        
        if self.abs(n) < 10:
            return self.abs(n)
        
        return max(self.toDigits(n))
            

    @classmethod
    def lwdp(self, n: int, /):
        """
        \\@since 0.3.39 https://aveyzan.glitch.me/tense#aveytense.Math.lwdp
        
        Return number *least with digit product* of `n`. To be more explanatory, this method returns a number, which \\
        digits create `n` via multiply operation, e.g. for `n` equal 18, method would return 29, because: 2 * 9 = 18.
        
        If this class method cannot find smallest number with digit product of `n`, it will return -1.
        
        """
        if not isinstance(n, int):
            error = TypeError("expected a non-negative integer")
            raise error
        
        r, m, b, i = 0, 1, self.abs(n), 9
        
        while i > 1: # 0.3.41: changed loop
            
            while b % i == 0:
                
                r += m * i
                m *= 10
                b //= i
                
            i -= 1
        
        if m == 10:
            r += 10
            
        return r if b == 1 else -1
    
    @classmethod
    def perm(self, n: int, k: _OptionalInteger = ..., /): # <- slash since 0.3.40
        """
        \\@since 0.3.39 https://aveyzan.glitch.me/tense#aveytense.Math.perm
        
        Formula `n! / (n - k)!`
        """
        
        if not isinstance(n, int):
            error = TypeError("expected an integer in first parameter")
            raise error
        
        if not isinstance(k, (int, _tc.EllipsisType)):
            error = TypeError("expected an integer, None or ellipsis in second parameter")
            raise error
        
        if isinstance(k, _tc.EllipsisType):
            return self.fact(n)
        
        else:
            return int(self.fact(n) / (self.fact(k) * self.fact(n - k)) * self.fact(k))
        
    @classmethod
    def mean(self, *n: _FloatOrInteger, mode = "a"):
        """
        \\@since 0.3.40 https://aveyzan.glitch.me/tense#aveytense.Math.mean
        
        - 0.3.41: Floating-point numbers are now allowed
        """
        
        if _reckon_init(n) == 0:
            error = TypeError("expected at least one value")
            raise error
        
        if type(mode) is not str:
            error = TypeError("expected a string in parameter 'mode'")
            raise error
        
        _mode = mode.lower()
        
        if _mode not in ("a", "g", "q", "h"):
            error = TypeError("expected a string value in parameter 'mode' from following: 'a', 'g', 'h' and 'q'")
            raise error
        
        for e in n:
            
            if type(e) not in (int, float) or e in (self.INF, self.NAN) or (_mode == "a" and self.isNegative(e)):
                error = TypeError("expected all values as numbers not being infinity nor NaN; for geometric mean - non-negative numbers only")
                raise error
            
        r = 0
        
        import statistics
        
        if _mode == "a":
            
            if hasattr(statistics, "mean"):
                return statistics.mean(n)
            
            for e in n:
                r += e
                
            return r / _reckon_init(n)
        
        elif _mode == "g":
            
            if hasattr(statistics, "geometric_mean"):
                return statistics.geometric_mean(n)
            
            r = 1
            
            for e in n:
                r *= e
                
            return self.pow(r, (1 / _reckon_init(n)))
        
        # 0.3.41
        elif _mode == "h":
            
            if hasattr(statistics, "harmonic_mean"):
                return statistics.harmonic_mean(n)
            
            r = .0
            
            for e in n:
                
                if e == 0:
                    error = ZeroDivisionError("one of integers equals zero")
                    raise error
                
                r += 1 / e
                
            return _reckon_init(n) / r
            
        
        else: # root mean square (rms)
            
            for e in n:
                r += e ** 2
                
            return self.sqrt(r / _reckon_init(n))
        
        
    @classmethod
    def stdev(self, *i: int):
        """
        \\@since 0.3.41
        
        Returns standard deviation of all given integers.
        """
        
        if _reckon_init(i) == 0:
            error = TypeError("expected at least one value")
            raise error
        
        for e in i:
            
            if type(e) is not int:
                error = TypeError("expected all values as integers")
                raise error
        
        import statistics
        
        if hasattr(statistics, "stdev"):
            return statistics.stdev(i)
        
        _mean = self.mean(*i, mode = "a")
        _res = .0
        
        for e in i:
            _res += (e - _mean) ** 2
            
        return self.sqrt(_res / _reckon_init(i))
    
    
    @classmethod
    def toRadians(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.41
        
        Returns angle in radians notation. Formula: `x*(π/180)`
        """
        
        if type(x) not in (int, float) or x in (self.NAN, self.INF):
            error = TypeError("expected a number not being infinity nor NaN")
            raise error
        
        if hasattr(_math, "radians"):
            return _math.radians(x)
        
        return x * (self.PI / 180)
        
        
    @classmethod
    def toDegrees(self, x: _FloatOrInteger, /):
        """
        \\@since 0.3.41
        
        Returns radians to angle notation. Formula: `x*(180/π)`
        """
        
        if type(x) not in (int, float) or x in (self.NAN, self.INF):
            error = TypeError("expected a number not being infinity nor NaN")
            raise error
        
        if hasattr(_math, "degrees"):
            return _math.degrees(x)
        
        return x * (180 / self.PI)
    
    
    @classmethod
    def toGradians(self, x: _FloatOrInteger, /, n = "r"):
        """
        \\@since 0.3.41
        
        Returns radians/degrees to gradians notation.
        """
        if type(x) not in (int, float) or x in (self.NAN, self.INF):
            error = TypeError("expected a number not being infinity nor NaN")
            raise error
        
        if n.lower() not in ("r", "d"):
            error = TypeError("expected 'r' or 'd' in parameter 'n'")
            raise error
        
        if n.lower() == "r":
            return x * (self.PI / 200)
        
        else:
            return x * (9 / 10)
        
        
        
    __all__ = sorted([n for n in locals() if n[:1] != "_"]) # 0.3.41: sorted()
    "\\@since 0.3.26c2"
    __dir__ = __all__
    "\\@since 0.3.26c2"

_ReckonType = _ReckonTypePre[_T]
_AbroadValue1 = _AbroadValue1Pre[_T]
_AbroadValue2 = _AbroadValue2Pre[_T]
_AbroadModifier = _AbroadModifierPre[_T]

def abroad(value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None):
    """
    \\@since 0.3.9  (standard since 0.3.10) \\
    \\@modified 0.3.25 (moved slash to between `value1` and `value2`)
    https://aveyzan.glitch.me/tense/py/function.abroad.html
    ```
    def abroad(value1, /, value2 = None, modifier = None): ...
    from aveytense import abroad
    ```
    Same function as `range()`, but more improved. `abroad()` has the following advantages:
    - supports countable objects, without using `len()` function, for all parameters
    - no overloads, only one version of function; that means there are 3 parameters, last 2 are optional
    - returns mutable sequence of integers, while `range()` returns integer-typed immutable sequence
    - `abroad()` is a function to faciliate recognizion; `range` is simultaneously a function and class
    - modifier will be always positive, negative values doesn't matter (!)
    - sequence begins from least of `value1` and `value2`, if `value2` is `bool` or `None`, begins \\
    from 0 to `value1` (or from `value1` to 0, if `value1` is negative)
    - `value2` as floating-point number allows the truncated integer to become endpoint, which will \\
    be included

    If `value2` is set to `None`, it will behave identically as `True` boolean value. It allows the \\
    iteration to go normally. Setting to `False` will flip the order and making all integers negative, \\
    put in ascending order.

    Function supports `range` class itself. \\
    Below `range()` values and `abroad()` function equivalents:
    ```js \\
    range(23) = abroad(23)
    range(2, 23) = abroad(2, 23)
    range(2, 24) = abroad(2, 23.6) // or just abroad(2, 24)
    range(23, 5, -1) = abroad(23, 5) // modifier skipped, default is 1
    range(23, 5, -3) = abroad(23, 5, 3) // there 3 also can be -3
    range(len("Perfect!")) = abroad("Perfect!")
    ``` \n
    By providing `range()` as an argument of this function, it simultaneously allows to alter the \\
    sequence from immutable to mutable. It is actually recommended to keep the same endpoint as \\
    `range` has, otherwise it may bind with returning not these results. Keep on mind this syntax:
    ```py \\
    abroad(range(0, x, m), x, m) # x - endpoint; m (optional) - step/modifier
    ```
    where `x` is stop/endpoint and `m` is step/modifier. That `m` can be omitted. \\
    That number 0 is set specially, because it may lead with returning unexpected \\
    sequence of numbers. But if it is intentional - sure, why not! But from Aveyzan's \\
    perspective it isn't recommended. \\
    For example:
    ```py \\
    abroad(range(0, 13), 13) # empty sequence
    abroad(range(0, 13), 13.24) # 13
    abroad(range(0, 13), 13, 2) # empty sequence
    abroad(range(0, 13, 2), 13, 2) # 7, 9, 11 (13 / 2 (round up) = 7)
    abroad(range(5, 13), 13) # 7, 8, 9, 10, 11, 12 (13 - 5 - 1 = 7)
    ```

    If `range` function is used commonly, with one parameter, syntax will be shortened:
    ```py \\
    abroad(range(x)) # x - endpoint
    ```
    where `x` is stop/endpoint. This is the common way to convert the immutable sequence to mutable.

    Usages:
    ```py \\
    # value1 = integer | Countable
    # value2 = None
    # modifier = 1
    abroad(92) # 0, 1, 2, 3, ..., 90, 91
    abroad(-92) # -92, -91, -90, ..., -2, -1
    abroad(["jump", "on", "the", "roof"]) # 0, 1, 2, 3
    abroad("Hello!") # 0, 1, 2, 3, 4, 5

    # value1 = integer
    # value2 = integer, float
    # modifier = 1
    abroad(92, 3) # 92, 91, 90, ..., 5, 4
    abroad(3, 92) # 3, 4, 5, ..., 90, 91
    abroad(92, 3.05) # 92, 91, 90, ..., 5, 4, 3 (!)
    abroad(3, 92.05) # 3, 4, 5, ..., 90, 91, 92 (!)

    # value1 = integer
    # value2 = bool | None | ... (None and ellipsis equal True)
    # modifier = 1
    abroad(92, True) # 0, 1, 2, 3, ..., 90, 91
    abroad(-92, True) # -92, -91, -90, ..., -2, -1
    abroad(92, False) # -92, -91, -90, ..., -2, -1
    abroad(-92, False) # 0, 1, 2, 3, ..., 90, 91

    # value1 = complex (under experiments)
    # value2 = bool | None | ... (None and ellipsis equal True)
    # modifier = 1
    abroad(3+9j, True) # 3, 4, ..., 7, 8
    abroad(3+9j, False) # -9, -8, ..., -5, -4
    abroad(3-9j, True) # 3, 2, 1, ..., -7, -8
    abroad(3-9j, False) # 7, 6, 5, ..., -3, -4
    abroad(-3+9j, True) # -3, -2, ..., 7, 8
    abroad(-3+9j, False) # -9, -8, ..., 1, 2
    abroad(-3-9j, True) # -3, -4, -5, ..., -7, -8
    abroad(-3-9j, False) # 7, 6, 5, ..., 3, 2

    # value1 = integer
    # value2 = bool | None (None equals True)
    # modifier = 4 (-4 will also result 4)
    abroad(92, True, 4) # 0, 4, 8, 12, ..., 84, 88
    abroad(-92, True, 4) # -92, -88, -84, ..., -8, -4
    abroad(92, False, 4) # -92, -88, -84, ..., -8, -4
    abroad(-92, False, 4) # 0, 4, 8, 12, ..., 84, 88
    ```
    """
    # if isinstance(value1, ModernString): v1 = value1.get()
    # else: v1 = value1
    # if isinstance(value2, ModernString): v2 = value2.get()
    # else: v2 = value2
    # if isinstance(modifier, ModernString): m = modifier.get()
    # else: m = modifier
    # return _abroad_init(v1, v2, m)
    return _abroad_init(value1, value2, modifier)

def reckon(*countables: _ReckonType[_T]):
    """
    \\@since 0.3.7 (standard since 0.3.7) \\
    \\@modified 0.3.27a5
    https://aveyzan.glitch.me/tense/tsl/reckon.html
    ```
    def reckon(*countables): ...
    from aveytense import reckon
    ```
    Extension of `len()` built-in function. Supports `IO` and \\
    its subclasses, classes having either `__len__`, `__iter__` \\
    or `__reckon__` magic methods.
    """
    i = 0
    for e in countables:
        # if isinstance(e, ModernString):
        #     for _ in e.get():
        #         i += 1
        # else: i += _reckon_init(e)
        i += _reckon_init(e)
    return i

def reckonLeast(*countables: _ReckonType[_T]):
    """
    \\@since 0.3.25 (standard since 0.3.25)
    ```
    def reckonLeast(*countables): ...
    from aveytense import reckonLeast
    ```
    Get least length from iterable objects passed.
    """
    n = 0
    for e in countables:
        if n > reckon(e):
            n = reckon(e)
    return n

def reckonGreatest(*countables: _ReckonType[_T]):
    """
    \\@since 0.3.25 (standard since 0.3.25)
    ```
    def reckonGreatest(*countables): ...
    from aveytense import reckonGreatest
    ```
    Get greatest length from iterable objects passed.
    """
    n = 0
    for e in countables:
        if n < reckon(e):
            n = reckon(e)
    return n

def reckonIsLeast(countable1: _ReckonType[_T], countable2: _ReckonType[_T], /):
    """
    \\@since 0.3.25 (standard since 0.3.25)
    ```
    def reckonIsLeast(countable1, countable2): ...
    from aveytense import reckonIsLeast
    ```
    Comparison: Check whether first argument is length-less than the second.
    """
    return reckon(countable1) < reckon(countable2)


def reckonIsGreater(countable1: _ReckonType[_T], countable2: _ReckonType[_T], /):
    """
    \\@since 0.3.25 (standard since 0.3.25)
    ```
    def reckonIsGreater(countable1, countable2): ...
    from aveytense import reckonIsGreater
    ```
    Comparison: Check whether first argument is length-greater than the second.
    """
    return reckon(countable1) > reckon(countable2)

@_tc.deprecated("Deprecated since 0.3.42, will be removed on 0.3.48")
class Reckon(_tc.Generic[_T]):
    """
    \\@since 0.3.25 (standard since 0.3.25)
    ```
    # created 05.07.2024
    class Reckon: ...
    from aveytense import Reckon
    ```
    Class version of function `reckon()`
    """
    __countables = None
    def __init__(self, *countables: _ReckonType[_T]):
        self.__countables: list[_ReckonType[_T]] = []
        for e in countables:
            self.__countables.append(e)
            
    def get(self, specific: _tc.Optional[int] = None, /):
        """
        \\@since 0.3.25 (standard since 0.3.25)
        ```
        # created 05.07.2024
        "method" in class Reckon
        ```
        Return size of all sizeable objects together. \\
        If `specific` is not `None`, returned is only \\
        at specified index. Out of range is typical \\
        Python error.
        """
        if specific is not None: return reckon(self.__countables[specific])
        else: return reckon(self.__countables)
        
    def least(self):
        """
        \\@since 0.3.25 (standard since 0.3.25)
        ```
        # created 05.07.2024
        "method" in class Reckon
        ```
        Get least length from iterable objects passed to the constructor.
        """
        n = 0
        for e in self.__countables:
            if n > reckon(e):
                n = reckon(e)
        return n
    
    def greatest(self):
        """
        \\@since 0.3.25 (standard since 0.3.25)
        ```
        # created 05.07.2024
        "method" in class Reckon
        ```
        Get greatest length from iterable objects passed to the constructor.
        """
        n = 0
        for e in self.__countables:
            if n < reckon(e):
                n = reckon(e)
        return n
    
    def isLeast(self, index1: int, index2: int, /):
        """
        \\@since 0.3.25 (standard since 0.3.25)
        ```
        # created 05.07.2024
        "method" in class Reckon
        ```
        Both arguments lead to sizeable objects passed to the constructor. \\
        Returned is `True`, if size of object at index `index1` is least than \\
        object at index `index2`
        """
        return reckon(self.__countables[index1]) < reckon(self.__countables[index2])
    
    def isGreater(self, index1: int, index2: int, /):
        """
        \\@since 0.3.25 (standard since 0.3.25)
        ```
        # created 05.07.2024
        "method" in class Reckon
        ```
        Both arguments lead to sizeable objects passed to the constructor. \\
        Returned is `True`, if size of object at index `index1` is greater than \\
        object at index `index2`
        """
        return reckon(self.__countables[index1]) > reckon(self.__countables[index2])
    

class protogen(_RAM):
    """
    \\@since 0.3.20 (standard since 0.3.20) \\
    \\@modified 0.3.24, 0.3.25 \\
    https://aveyzan.glitch.me/tense/py/function.abroad.html
    ```
    class protogen: ...
    from aveytense import protogen
    ```

    This class is a joke, but alternative of `abroad()` function.
    """
    _ProtogenActivate = _ab_mod.AbroadInitializer
    def __new__(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None) -> _ProtogenActivate:
        """
        \\@since 0.3.20 (standard since 0.3.20) \\
        \\@modified 0.3.24, 0.3.25 \\
        https://aveyzan.glitch.me/tense/py/function.abroad.html
        ```
        class protogen: ...
        from aveytense import protogen
        ```
        Construct a new `protogen` object, which will produce next integers, until an endpoint is caught. \\
        For more information, see `abroad()` function.
        """
        return abroad(value1, value2, modifier)
    @staticmethod
    def info():
        """Receive information about this class."""
        print(
            "Class name: protogen",
            "Class name for furry community: a furry species",
            "Class author: Aveyzan",
            "Extends: MutableSequence[int] (can be recognized as list)",
            "Created: 31.10.2023 (31st October 2023)",
            "Available since: Tense 0.3.20",
            "Standard since: Tense 0.3.20",
            "Main target: replacing range() function due to functionality",
            "Usage: similar to range(), identical to abroad()",
            sep = "\n"
        )

if _sys.version_info < (0, 3, 39):
    @_tc.deprecated("Deprecated since 0.3.31 due to loose of Tkinter support, will be removed on 0.3.36")
    class TenseTk:
        """
        \\@since 0.3.24
        ```
        in module tense
        ```
        TensePy Tk class from `tkinter` module equivalent.
        """
        
        __loc_tk = None
        __loc_frame = None
        __loc_label = None
        __loc_button = None
        __loc_buttons = None
        __loc_checkbutton = None
        __loc_checkbuttons = None
        __loc_radiobutton = None
        __loc_radiobuttons = None
        
        def __init__(self, screenName: _tc.Optional[str] = None, baseName: _tc.Optional[str] = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: _tc.Optional[str] = None) -> None:
            self.__loc_tk = _tkinter.Tk(
                screenName = screenName,
                baseName = baseName,
                className = className,
                useTk = useTk,
                sync = sync,
                use = use
            )
            self.__loc_frame = _tkinter.Frame(self.__loc_tk)
        
        def mainloop(self, n = 0):
            """
            \\@since 0.3.24
            ```
            "method" in class YamiTk
            ```
            Call main loop of Tk
            """
            if self.__loc_tk is not None:
                self.__loc_tk.mainloop(n)
            else:
                err, s = (_tc.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            return self
        
        def setWindowSize(self, x: int, y: int, /):
            """
            \\@since 0.3.26a3
            ```
            "method" in class YamiTk
            ```
            Set the window size measured in pixels. \\
            `x` means width, and `y` means height of the window
            """
            if self.__loc_tk is not None:
                self.__loc_tk.geometry(f"{x}x{y}")
            else:
                err, s = (_tc.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            return self
        
        def setMaxWindowSize(self, x: int, y: int, /):
            """
            \\@since 0.3.26a3
            ```
            "method" in class YamiTk
            ```
            Set the max window size measured in pixels. \\
            `x` means width, and `y` means height of the window
            """
            if self.__loc_tk is not None:
                self.__loc_tk.maxsize(x, y)
            else:
                err, s = (_tc.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            return self
        
        def setTitle(self, title: str, /):
            """
            \\@since 0.3.26a3
            ```
            "method" in class YamiTk
            ```
            Set title of the window
            """
            if self.__loc_tk is not None:
                self.__loc_tk.title(title)
            else:
                err, s = (_tc.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            return self
        
        @property
        def getTk(self):
            """
            \\@since 0.3.26a3
            ```
            "property" in class YamiTk
            ```
            Return `tkinter.Tk` instance within the class
            """
            if self.__loc_tk is None:
                err, s = (_tc.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            return self.__loc_tk
        
        @property
        def getFrame(self):
            """
            \\@since 0.3.26a3
            ```
            "property" in class YamiTk
            ```
            Return `tkinter.Frame` instance within the class
            """
            if self.__loc_frame is None:
                err, s = (_tc.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            return self.__loc_frame
        
        def setFrame(self, frame: _tkinter.Frame, /):
            """
            \\@since 0.3.26a3
            ```
            "method" in class YamiTk
            ```
            Overwrite current `tkinter.Frame` instance
            """
            if self.__loc_frame is None:
                err, s = (_tc.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            elif not isinstance(frame, _tkinter.Frame):
                err, s = (TypeError, "Parameter 'frame' is not of instance 'tkinter.Frame'.")
                raise err(s)
            else:
                self.__loc_frame = frame
            return self
        
        def setLabel(self, label: _tkinter.Label, /):
            """
            \\@since 0.3.26a3
            ```
            "method" in class YamiTk
            ```
            Overwrite current `tkinter.Label` instance or set a new value
            """
            if self.__loc_frame is None:
                err, s = (_tc.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            elif not isinstance(label, _tkinter.Label):
                err, s = (TypeError, "Parameter 'label' is not of instance 'tkinter.Label'.")
                raise err(s)
            else:
                self.__loc_label = label
            return self

# not for export
del RAM, _RAM

__all__ = sorted([n for n in globals() if n[:1] != "_"])
__dir__ = __all__

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error