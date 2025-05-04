"""
**AveyTense Internal Abroad Types** \n
\\@since 0.3.29 \\
© 2023-Present Aveyzan // License: MIT
```ts
module tense._abroad
```
This internal module has been established to extend possibilities of `abroad()` \\
function and its variations, put many abroad types there.
"""

import collections as _collections
import copy as _copy
import tkinter as _tkinter
import typing as _typing

from . import _init_types as _types
from . import _abc

__module__ = "tense"
_var = _types.TypeVar

_T = _var("_T")
_V1 = _var("_V1")
_V2 = _var("_V2")
_M = _var("_M")

ReckonType = _types.Union[
        # dict[_T], # removed 0.3.27a5 (inherits from MutableMapping)
        # list[_T], # removed 0.3.27a5 (inherits from MutableSequence)
        # tuple[_T, ...], # removed 0.3.27a5 (inherits from Sequence)
        # str, # removed 0.3.27a5 (inherits from Sequence)
        # ct.deque[_T], # removed 0.3.27a5 (inherits from MutableSequence)
        # set[_T], # removed 0.3.27a5 (inherits from MutableSet)
        # bytes, # removed 0.3.27a5 (inherits from Sequence)
        # bytearray, # removed 0.3.27a5 (inherits from MutableSequence)
        # memoryview, # removed 0.3.27a5 (inherits from Sequence)
        # range, # removed 0.3.27a5 (inherits from Sequence)
        # mmap, # removed 0.3.27a5 (inherits from Sized)
        # array[_T], # removed 0.3.27a5 (inherits from MutableSequence)
        # enumerate[_T], # removed 0.3.27a5 (inherits from Iterator -> Iterable)
        # frozenset[_T], # removed 0.3.27a5 (inherits from AbstractSet)
        # ct.Counter[_T], # removed 0.3.27a5 (inherits from dict -> MutableMapping)
        # ct.defaultdict[_T], # removed 0.3.27a5 (inherits from dict -> MutableMapping)
        # io.TextIOWrapper, # removed 0.3.27a5 (inherits from IO)
        ### LOG: since 0.3.24
        # io.FileIO, # removed 0.3.27a5 (inherits from IO)
        # io.BufferedWriter, # removed 0.3.27a5 (inherits from IO)
        # io.BufferedRandom, # removed 0.3.27a5 (inherits from IO)
        # io.BufferedReader, # removed 0.3.27a5 (inherits from IO)
        _typing.IO[_types.Any],
        # LOG: since 0.3.25
        # tp.TextIO, # removed 0.3.27a5 (inherits from IO)
        # tp.BinaryIO, # removed 0.3.27a5 (inherits from IO)
        # io.StringIO, # removed 0.3.27a5 (inherits from IO)
        # io.BufferedRWPair, # removed 0.3.27a5 (inherits from IO)
        # tp.Sequence[_T], # removed 0.3.27a5 (inherits from Iterable)
        # tp.MutableSequence[_T], # removed 0.3.27a5 (inherits from Sequence)
        # io.BytesIO, # removed 0.3.27a5 (inherits from IO)
        # io.BufferedIOBase, # removed 0.3.27a5 (unneeded)
        # tp.Mapping[_T, Any], # removed 0.3.27a5 (inherits from Iterable)
        # tp.MutableMapping[_T, Any], # removed 0.3.27a5 (inherits from Mapping)
        # tp.MutableSet[_T], # removed 0.3.27a5 (inherits from AbstractSet)
        # tp.AbstractSet[_T], # removed 0.3.27a5 (inherits from Iterable)
        _abc.Iterable[_T], 
        # ct.ChainMap[_T], # removed 0.3.27a5 (inherits from MutableMapping)
        # ct.OrderedDict[_T], # removed 0.3.27a5 (inherits from dict -> MutableMapping)
        ### LOG: 0.3.26b3
        # tp.AsyncIterable[_T], # removed 0.3.27a5 (inherits from Iterable)
        ### LOG: 0.3.26c1
        _abc.ReckonOperable,
        # _tkinter.StringVar, # remove support on 0.3.36 (support removed on 0.3.39)
        # LOG: 0.3.27a5
        _abc.Sizeable
]
"""
\\@since 0.3.25 \\
\\@author Aveyzan
```
in module tense.types_collection # to 0.3.26b3 in module tense.types
```
Package of types, which are considered countable and satisfy type requirement \\
for function `reckon()`. To 0.3.26b3 also known as `SupportsCountables`.
"""
ReckonNGT = _types.Union[
        # dict[_T], # removed 0.3.27a5 (inherits from MutableMapping)
        # list[_T], # removed 0.3.27a5 (inherits from MutableSequence)
        # tuple[_T, ...], # removed 0.3.27a5 (inherits from Sequence)
        # str, # removed 0.3.27a5 (inherits from Sequence)
        # ct.deque[_T], # removed 0.3.27a5 (inherits from MutableSequence)
        # set[_T], # removed 0.3.27a5 (inherits from MutableSet)
        # bytes, # removed 0.3.27a5 (inherits from Sequence)
        # bytearray, # removed 0.3.27a5 (inherits from MutableSequence)
        # memoryview, # removed 0.3.27a5 (inherits from Sequence)
        # range, # removed 0.3.27a5 (inherits from Sequence)
        # mmap, # removed 0.3.27a5 (inherits from Sized)
        # array[_T], # removed 0.3.27a5 (inherits from MutableSequence)
        # enumerate[_T], # removed 0.3.27a5 (inherits from Iterator -> Iterable)
        # frozenset[_T], # removed 0.3.27a5 (inherits from AbstractSet)
        # ct.Counter[_T], # removed 0.3.27a5 (inherits from dict -> MutableMapping)
        # ct.defaultdict[_T], # removed 0.3.27a5 (inherits from dict -> MutableMapping)
        # io.TextIOWrapper, # removed 0.3.27a5 (inherits from IO)
        ### LOG: since 0.3.24
        # io.FileIO, # removed 0.3.27a5 (inherits from IO)
        # io.BufferedWriter, # removed 0.3.27a5 (inherits from IO)
        # io.BufferedRandom, # removed 0.3.27a5 (inherits from IO)
        # io.BufferedReader, # removed 0.3.27a5 (inherits from IO)
        _typing.IO,
        # LOG: since 0.3.25
        # tp.TextIO, # removed 0.3.27a5 (inherits from IO)
        # tp.BinaryIO, # removed 0.3.27a5 (inherits from IO)
        # io.StringIO, # removed 0.3.27a5 (inherits from IO)
        # io.BufferedRWPair, # removed 0.3.27a5 (inherits from IO)
        # tp.Sequence[_T], # removed 0.3.27a5 (inherits from Iterable)
        # tp.MutableSequence[_T], # removed 0.3.27a5 (inherits from Sequence)
        # io.BytesIO, # removed 0.3.27a5 (inherits from IO)
        # io.BufferedIOBase, # removed 0.3.27a5 (unneeded)
        # tp.Mapping[_T, Any], # removed 0.3.27a5 (inherits from Iterable)
        # tp.MutableMapping[_T, Any], # removed 0.3.27a5 (inherits from Mapping)
        # tp.MutableSet[_T], # removed 0.3.27a5 (inherits from AbstractSet)
        # tp.AbstractSet[_T], # removed 0.3.27a5 (inherits from Iterable)
        _abc.Iterable, 
        # ct.ChainMap[_T], # removed 0.3.27a5 (inherits from MutableMapping)
        # ct.OrderedDict[_T], # removed 0.3.27a5 (inherits from dict -> MutableMapping)
        ### LOG: 0.3.26b3
        # tp.AsyncIterable[_T], # removed 0.3.27a5 (inherits from Iterable)
        ### LOG: 0.3.26c1
        _abc.ReckonOperable,
        # _tkinter.StringVar, # remove support on 0.3.36 (support removed on 0.3.39)
        # LOG: 0.3.27a5
        _abc.Sizeable
] # since 0.3.25, renamed from SupportsCountablesLackOfGeneric (0.3.26b3)

AbroadValue1 = _types.Union[int, float, complex, ReckonType[_T]] # since 0.3.25, renamed from SupportsAbroadValue1 (0.3.26b3)
AbroadValue2 = _types.Union[int, float, bool, ReckonType[_T]] # since 0.3.25, renamed from SupportsAbroadValue2 (0.3.26b3)
AbroadModifier = _types.Optional[AbroadValue1[_T]] # since 0.3.25, renamed from SupportsAbroadModifier (0.3.26b3)
AbroadPackType = _types.Union[list[_T], tuple[_T, ...], _collections.deque[_T], set[_T], enumerate[_T], frozenset[_T]] # since 0.3.25, lose of dict and defaultdict support, added frozenset, renamed from SupportsAbroadPackValues (0.3.26b3)
AbroadConvectType = AbroadValue1[_T] # since 0.3.25, renamed from SupportsAbroadConvectValues (0.3.26b3)
AbroadLiveType = AbroadConvectType[_T] # since 0.3.25, renamed from SupportsAbroadLiveValues (0.3.26b3)
AbroadVividType = _types.Union[tuple[AbroadValue1[_V1]], tuple[AbroadValue1[_V1], AbroadValue2[_V2]], tuple[AbroadValue1[_V1], AbroadValue2[_V2], AbroadModifier[_M]]] # since 0.3.25, renamed from SupportsAbroadVividValues (0.3.26)
AbroadInitializer = list[_T] # since 0.3.25
AbroadMultiInitializer = list[list[_T]] # since 0.3.25

class _AbroadUnknownInitializer(_types.Generic[_T]):
    """\\@since 0.3.29"""
    
    def __init__(self, seq: _abc.Iterable[_T], v1: int, v2: int, m: int, /):
        
        self.__l = list(seq)
        self.__p = (v1, v2, m)
        
    def __iter__(self):
        
        return iter(self.__l)
    
    def __reversed__(self):
        """\\@since 0.3.32"""
        
        return reversed(self.__l)
    
    def __str__(self):
        
        if len(self.__l) == 0:
            return "abroad( <empty> )"
        
        else:
            
            if self.__p == (0, 0, 0):
                return "abroad( <mixed> )"
            
            return "abroad({})".format(", ".join([str(e) for e in self.__p]))
            
    def __repr__(self):
        
        return "<{}.{} object: {}>".format(__module__, type(self).__name__, self.__str__())
    
    def __pos__(self):
        """
        \\@since 0.3.28
        
        Returns sequence as a list. `+` can be claimed as "allow to change any items, this sequence can be updated"
        """
        return self.__l
    
    def __neg__(self):
        """
        \\@since 0.3.28
        
        Returns sequence as a tuple. `-` can be claimed as "do not change any items, this sequence cannot be updated"
        """
        return tuple(self.__l)
    
    def __invert__(self):
        """
        \\@since 0.3.28
        
        Returns sequence as a set. `~` can be claimed as "allow to change any items, this sequence can be updated, BUT items must be unique"
        """
        return set(self.__l)
    
    def __getitem__(self, key: int):
        """
        \\@since 0.3.29. `self[key]`
        """
        try:
            return self.__l[key]
        
        except IndexError:
            error = IndexError("sequence out of range")
            raise error
        
    def __contains__(self, item: _T):
        """
        \\@since 0.3.32. `item in self`
        """
        return item in self.__l
    
    def __add__(self, other: _types.Union[_abc.Iterable[_T], _types.Self]):
        """
        \\@since 0.3.32. `self + other`
        """
        if not isinstance(other, (_abc.Iterable, type(self))):
            error = TypeError("expected an iterable or abroad() function result as a right operand")
            raise error
        
        # 1st statement: obvious certificate that this class has the __iter__
        # method, so it satisfies requirement for list constructor
        if (isinstance(other, type(self)) and len(list(other)) == 0) or (isinstance(other, _abc.Iterable) and len(other) == 0):
            return self
        
        # this notation seems ugly since there is double invocation, but
        # necessary in case of inheritance, so code will type hint subclasses
        # objects as returned results. this notation is also here due to
        # refraining from using base class as a role of constructor - type
        # hinted will be object of base class, what might not be a good idea
        return type(self)(self.__l + [e for e in other], 0, 0, 0) 
    
    def __radd__(self, other: _types.Union[_abc.Iterable[_T], _types.Self]):
        """
        \\@since 0.3.32. `other + self`
        """
        if not isinstance(other, (_abc.Iterable, type(self))):
            error = TypeError("expected an iterable or abroad() function result as a left operand")
            raise error
        
        if (isinstance(other, type(self)) and len(list(other)) == 0) or (isinstance(other, _abc.Iterable) and len(other) == 0):
            return self
        
        return type(self)([e for e in other] + self.__l, 0, 0, 0)
    
    def __mul__(self, other: int):
        """
        \\@since 0.3.32. `self * other`
        """
        if not isinstance(other, int) or (isinstance(other, int) and other < 1):
            error = TypeError("expected a non-negative integer as a right operand")
            raise error
        
        return type(self)(self.__l * other, self.__p[0], self.__p[1], self.__p[2])
    
    def __rmul__(self, other: int):
        """
        \\@since 0.3.32. `other * self`
        """
        if not isinstance(other, int) or (isinstance(other, int) and other < 1):
            error = TypeError("expected a non-negative integer as a left operand")
            raise error
        
        return type(self)(self.__l * other, self.__p[0], self.__p[1], self.__p[2])
    
    def __copy__(self):
        """
        \\@since 0.3.34
        
        Returns shallow copy
        """
        return _copy.copy(self)
    
    def __deepcopy__(self):
        """
        \\@since 0.3.34
        
        Returns deep copy
        """
        return _copy.deepcopy(self)
       
    @property
    def params(self):
        """
        \\@since 0.3.29
        
        Returns parameters as integers
        """
        return self.__p
    
    @params.getter
    def params(self):
        return self.__p
    
    @params.deleter
    def params(self):
        error = TypeError("cannot delete property 'params'")
        raise error
    
    @params.setter
    def params(self, value):
        error = TypeError("cannot set new value to property 'params'")
        raise error
    
class AbroadInitializer(_AbroadUnknownInitializer[int]): ... # since 0.3.28
class AbroadStringInitializer(_AbroadUnknownInitializer[str]): ... # since 0.3.29
class AbroadFloatyInitializer(_AbroadUnknownInitializer[float]): ... # since 0.3.29