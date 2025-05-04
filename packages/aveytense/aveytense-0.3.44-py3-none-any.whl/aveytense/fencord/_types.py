"""
**AveyTense Fencord Types** \n
\\@since 0.3.26rc3 \\
© 2023-Present Aveyzan // License: MIT
```ts
module aveytense.fencord._types
```
Types wrapper for TensePy Fencord.
"""

from __future__ import annotations
import sys as _sys

if _sys.version_info < (3, 9):
    err, s = (RuntimeError, "Not allowed to import this module when having Python version least than 3.9.")
    raise err(s)

import datetime as _datetime
import subprocess as sb
import typing as _typing

from .. import _abc as _ta
from .. import _init_types as _tt

try:
    import discord as _discord
    
except (NameError, ModuleNotFoundError, ImportError):
    
    sb.run([_sys.executable, "-m", "pip", "install", "discord"])
    
import discord as _discord

from discord import abc as abc # 0.3.27a1
from discord import app_commands as app_commands # 0.3.27a1
from discord import ui as ui # 0.3.27a1
from discord import utils as utils # 0.3.27a1
from discord.app_commands import transformers as transformers # 0.3.27a1
from discord.app_commands import translator as translator # 0.3.27a1

_var = _tt.TypeVar
_par = _tt.ParamSpec

if _typing.TYPE_CHECKING:
    T_client = _var("T_client", bound = _discord.Client, covariant = True, default = _discord.Client)
else:
    T_client = _var("T_client", bound = _discord.Client, covariant = True)

_P = _par("_P")
_T = _var("_T")
_L = _var("_L", bound = transformers.TranslationContextLocation)
"\\@since 0.3.27a1"

MISSING = _discord.abc.MISSING
"\\@since 0.3.26rc3"

T_coroutine = _var("T_coroutine", bound = _tt.Callable[..., _ta.Coroutine[_tt.Any, _tt.Any, list[app_commands.AppCommand]]])
"""
Bound to `(...) -> Coroutine[Any, Any, discord.app_commands.AppCommand]`. \\
Required for `Fencord.event()` decorator. Equivalent to Discord.py's `CoroT`
"""