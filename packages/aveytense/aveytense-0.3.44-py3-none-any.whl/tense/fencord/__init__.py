"""
**Tense Fencord** \n
\\@since 0.3.24 \\
\\@modified 0.3.25 \\
© 2023-Present Aveyzan // License: MIT
```ts
module _tense.fencord
```
Since 0.3.25 this module is called `_tense.fencord` instead of `_tense.core`. \\
Import this module only, if:
- you have Python 3.9 or above
- you have discord.py via `pip install discord`

This Tense module features `Fencord` class.
"""
import sys as _sys

if _sys.version_info < (3, 9):
    err, s = (RuntimeError, "Not allowed to import this module when having Python version least than 3.9.")
    raise err(s)

import collections as _collections
import inspect as _inspect
import re as _re
import subprocess as _subprocess
import warnings as _warnings

from .._primal import (
    reckon as _reckon
)
from .. import _abc as _ta
from .. import _init_types as _tt
from ._types import (
    abc as _abc,
    app_commands as _app_commands,
    translator as _translator,
    ui as _ui,
    T_coroutine as _T_coroutine
)

try:
    import discord as _discord
    
except:
    _subprocess.run([_sys.executable, "-m", "pip", "install", "discord"])
    
import discord as _discord

from aveytense import (
    Tense as _Tense,
    FencordOptions as _FencordOptions
)

# between @since and @author there is unnecessarily long line spacing
# hence this warning is being thrown; it is being disabled.
_warnings.filterwarnings("ignore", category = SyntaxWarning)

_var = _tt.TypeVar
# _spec = tc.SpecVar

_T = _var("_T")
# _P = _spec("_P")


class LocaleString:
    "\\@since 0.3.26rc3; class since 0.3.27a1. Since 0.3.27a4 in module `tense.fencord`"
    
    def __new__(cls, message: str, /, **extras: _tt.Any):
        
        return _translator.locale_str(message, kwargs = extras)

if False: # experiments since 0.3.27
    class Servers:
        """
        \\@since 0.3.27a4
        ```
        in module _tense.fencord
        ```
        Alternative type for `servers` parameter in `Fencord.slashCommand()` callback
        """
        import discord as __dc
        from .. import types_collection as __tc
        __objs = None

        def __init__(self, *ids: int):
            if _reckon(ids) == 0:
                err, s = (ValueError, "Expected at least one integer value")
                raise err(s)
            a = [_discord.Object(ids[0], type = _discord.Guild)]
            a.clear()
            for e in ids:
                # haven't tested yet! this has to affirm that id refers to a guild/server
                # if _discord.Object(e).type != _discord.Guild:
                #    err, s = (ValueError, f"Invalid Discord guild/server ID: '{e}'")
                #    raise err(s)
                if not _Tense.isInteger(e):
                    err, s = (TypeError, "Expected every value to be integers")
                    raise err(s)
                else:
                    a.append(_discord.Object(e, type = _discord.Guild))
            self.__objs = a
        
        @property
        def list(self): # marking the returned type isn't actually necessary. 'Object' instances have 'id' attribute
            """
            \\@since 0.3.27a4
            ```
            "property" in class Servers
            ```
            Only used in `Fencord.slashCommand()` for `servers` parameter. \\
            In overall you shouldn't use this property. It returns list of \\
            `discord.Object` class instances.
            """
            if _Tense.isNone(self.__objs):
                err, s = (self.__tt.NotInitializedError, "Class wasn't initialized")
                raise err(s)
            return self.__objs
                
    Guilds = Servers # 0.3.27a4

_SlashCommandServers = _tt.Union[_ta.Sequence[_T], _T, None] # 0.3.25
_EmbedType = _tt.Literal['rich', 'image', 'video', 'gifv', 'article', 'link'] # 0.3.26


class _FontStyles(_tt.Enum):
    """
    \\@since 0.3.27
    
    Internal class for font styles of discord
    """
    
    ### 1x
    # Non-mixed styles
    NORMAL = 0
    BOLD = 1
    ITALIC = 2
    UNDERLINE = 3
    STRIKE = 4
    CODE = 5
    BIG = 6
    MEDIUM = 7
    SMALL = 8
    SMALLER = 9
    QUOTE = 10
    SPOILER = 11
    URL = 12
    SILENT = 13
    
    if False: # leave for later (0.3.27)
        ### 2x
        # usually to prevent more parameters
        BOLD_ITALIC = 20
        BOLD_UNDERLINE = 21
        BOLD_STRIKE = 22
        BOLD_CODE = 23
        BOLD_SMALLER = 24
        BOLD_QUOTE = 25
        BOLD_SPOILER = 26
        BOLD_URL = 27
        BOLD_SILENT = 28
        
        ITALIC_UNDERLINE = 30
        ITALIC_STRIKE = 31
        ITALIC_CODE = 32
        ITALIC_BIG = 33
        ITALIC_MEDIUM = 34
        ITALIC_SMALL = 35
        ITALIC_SMALLER = 36
        ITALIC_QUOTE = 37
        ITALIC_SPOILER = 38
        ITALIC_URL = 39
        ITALIC_SILENT = 40
        
        UNDERLINE_STRIKE = 45
        UNDERLINE_CODE = 46
        UNDERLINE_BIG = 47
        UNDERLINE_MEDIUM = 48
        UNDERLINE_SMALL = 49
        UNDERLINE_SMALLER = 50
        UNDERLINE_QUOTE = 51
        UNDERLINE_SPOILER = 52
        UNDERLINE_URL = 53
        UNDERLINE_SILENT = 54
        
        STRIKE_CODE = 60
        STRIKE_BIG = 61
        STRIKE_MEDIUM = 62
        STRIKE_SMALL = 63
        STRIKE_SMALLER = 64
        STRIKE_QUOTE = 65
        STRIKE_SPOILER = 66
        STRIKE_URL = 67
        STRIKE_SILENT = 68
        
        CODE_BIG = 70
        CODE_SMALL = 71
        CODE_SMALLER = 72
        CODE_QUOTE = 73
        CODE_SPOILER = 74
        CODE_URL = 75
        CODE_SILENT = 76
        
        BIG_QUOTE = 80
        BIG_SPOILER = 81
        BIG_URL = 82
        BIG_SILENT = 83
        
        MEDIUM_QUOTE = 90
        MEDIUM_SPOILER = 91
        MEDIUM_URL = 92
        MEDIUM_SILENT = 93
        
        SMALL_QUOTE = 100
        SMALL_SPOILER = 101
        SMALL_URL = 102
        SMALL_SILENT = 103
        
        SMALLER_QUOTE = 110
        SMALLER_SPOILER = 111
        SMALLER_URL = 112
        SMALLER_SILENT = 113
        
        QUOTE_SPOILER = 120
        QUOTE_URL = 121
        QUOTE_SILENT = 122
        
        SPOILER_URL = 125
        SPOILER_SILENT = 126
        
        URL_SILENT = 129
        
        # duplicates
        ITALIC_BOLD = BOLD_ITALIC
        UNDERLINE_BOLD = BOLD_UNDERLINE
        UNDERLINE_ITALIC = ITALIC_UNDERLINE
        STRIKE_BOLD = BOLD_STRIKE
        STRIKE_ITALIC = ITALIC_STRIKE
        STRIKE_UNDERLINE = UNDERLINE_STRIKE
        CODE_BOLD = BOLD_CODE
        CODE_ITALIC = ITALIC_CODE
        CODE_UNDERLINE = UNDERLINE_CODE
        CODE_STRIKE = STRIKE_CODE
    

class FontStyler:
    """
    \\@since 0.3.27a1
    ```
    in module _tense.fencord
    ```
    Proving font styles from Discord
    """
    
    NORMAL = _FontStyles.NORMAL
    BOLD = _FontStyles.BOLD
    ITALIC = _FontStyles.ITALIC
    UNDERLINE = _FontStyles.UNDERLINE
    STRIKE = _FontStyles.STRIKE
    CODE = _FontStyles.CODE
    BIG = _FontStyles.BIG
    MEDIUM = _FontStyles.MEDIUM
    SMALL = _FontStyles.SMALL
    SMALLER = _FontStyles.SMALLER
    QUOTE = _FontStyles.QUOTE
    SPOILER = _FontStyles.SPOILER
    URL = _FontStyles.URL
    SILENT = _FontStyles.SILENT
    
    __mode = None
    __text = ""
    
    def __init__(self, text: _tt.Union[str, _ta.StringConvertible], style: _FontStyles = _FontStyles.NORMAL, value: _tt.Optional[str] = None, visible: bool = True, /):
        """
        \\@since 0.3.27
        
        Append entry text along with styling
        """
        _text = str(text) if not isinstance(text, str) else text
        
        if _reckon(_text) == 0:
            error = ValueError("expected a non-empty string in parameter 'text'")
            raise error
        
        if style == self.NORMAL:
            self.__text = _text
            
        elif style == self.BOLD:
            self.__text = "**{}**".format(_text)
            
        elif style == self.ITALIC:
            self.__text = "*{}*".format(_text)
            
        elif style == self.UNDERLINE:
            self.__text = "__{}__".format(_text)
            
        elif style == self.STRIKE:
            self.__text = "~~{}~~".format(_text)
            
        elif style == self.CODE:
            if not _Tense.isNone(value):
                self.__text = """```{}
                {}
                ```""".format(value, _text)
            else:
                self.__text = "`{}`".format(_text)
                
        elif style == self.BIG:
            self.__text = "# {}".format(_text)
            
        elif style == self.MEDIUM:
            self.__text = "## {}".format(_text)
            
        elif style == self.SMALL:
            self.__text = "### {}".format(_text)
            
        elif style == self.SMALLER:
            self.__text = "-# {}".format(_text)
            
        elif style == self.QUOTE:
            self.__text = "> {}".format(_text)
            
        elif style == self.SPOILER:
            self.__text = "||{}||".format(_text)
            
        elif style == self.URL:
            if not _Tense.isNone(value):
                self.__text = "[{}]({})".format(value, _text) if visible else "[{}](<{}>)".format(value, _text)
            else:
                err, s = (ValueError, "expected a link in a string in parameter 'value'")
                
        elif style == self.SILENT:
            self.__text = "@silent {}".format(_text)
            
        else:
            err, s = (TypeError, "expected a valid font style")
            raise err(s)
        
    def __str__(self):
        """
        \\@since 0.3.27
        
        Return styled string
        """
        return self.__text
    
    @staticmethod
    def bold(text: str, /):
        """
        \\@since 0.3.25
        ```
        "class method" in class FontStyles
        ```
        On Discord: make text bold
        """
        return f"**{text}**"
    
    @staticmethod
    def italic(text: str, /):
        """
        \\@since 0.3.25
        ```
        "class method" in class FontStyles
        ```
        On Discord: make text italic
        """
        return f"*{text}*"
    
    @staticmethod
    def underline(text: str, /):
        """
        \\@since 0.3.25
        ```
        "class method" in class FontStyles
        ```
        On Discord: make text underlined
        """
        return f"__{text}__"
    
    @staticmethod
    def code(text: str, language: _tt.Optional[str] = None, /):
        """
        \\@since 0.3.25
        ```
        "class method" in class FontStyles
        ```
        On Discord: coded text
        """
        if language is None:
            return f"`{text}`"
        
        else:
            return f"```{language}\n{text}\n```"
        
    @staticmethod
    def big(text: str, /):
        """
        \\@since 0.3.25
        ```
        "class method" in class FontStyles
        ```
        On Discord: make text big
        """
        return f"# {text}"
    
    @staticmethod
    def medium(text: str, /):
        """
        \\@since 0.3.25
        ```
        "class method" in class FontStyles
        ```
        On Discord: make text medium
        """
        return f"## {text}"
    
    @staticmethod
    def small(text: str, /):
        """
        \\@since 0.3.25
        ```
        "class method" in class FontStyles
        ```
        On Discord: make text small
        """
        return f"### {text}"
    
    @staticmethod
    def smaller(text: str, /):
        """
        \\@since 0.3.25
        ```
        "class method" in class FontStyles
        ```
        On Discord: make text smaller
        """
        return f"-# {text}"
    
    @staticmethod
    def quote(text: str, /):
        """
        \\@since 0.3.25
        ```
        "class method" in class FontStyles
        ```
        On Discord: transform text to quote
        """
        return f"> {text}"
    
    @staticmethod
    def spoiler(text: str, /):
        """
        \\@since 0.3.25
        ```
        "class method" in class FontStyles
        ```
        On Discord: make text spoiled
        """
        return f"||{text}||"
    
    @staticmethod
    def textUrl(text: str, url: str, hideEmbed = True):
        """
        \\@since 0.3.26a2
        ```
        "class method" in class FontStyles
        ```
        On Discord: make text become hyperlink, leading to specified URL
        """
        return f"[{text}](<{url}>)" if hideEmbed else f"[{text}]({url})"
    
    @staticmethod
    def silent(text: str):
        """
        \\@since 0.3.26a3
        ```
        "class method" in class FontStyles
        ```
        Make a message silent. Usable for Direct Messages. \\
        As a tip, refer `@silent` as `> ` (quote), and message \\
        MUST be prefixed with `@silent`.
        """
        return f"@silent {text}"

class Fencord:
    """
    Fencord
    +++++++
    \\@since 0.3.24 (before 0.3.25 as `DC`)
    ```ts
    in module _tense.fencord
    ```
    Providing methods to help integrating with Discord.

    During 0.3.24 - 0.3.26 this class was final. Since 0.3.27a1 \\
    this class can be subclassed
    """
    
    __commandtree = None
    __client = None
    __intents = None
    __synccorountine = None
    
    @property
    def user(self):
        """
        \\@since 0.3.25
        ```ts
        "property" in class Fencord
        ```
        Returns user of this client. The `None` type is deduced \\
        only if class wasn't initialized.
        """
        return self.__client.user
    
    @property
    def servers(self):
        """
        \\@since 0.3.25
        ```ts
        "property" in class Fencord
        ```
        Returns servers/guilds tuple in which client is
        """
        return tuple([x for x in self.__client.guilds])

    if False: # removed 0.3.27
        @property
        @_tt.deprecated("Deprecated since 0.3.27a2, consider using 'Fencord.client' property instead")
        def getClient(self):
            """
            \\@since 0.3.25 \\
            \\@deprecated 0.3.27a2
            ```ts
            "property" in class Fencord
            ```
            Returns reference to `Client` instance inside the class. \\
            The `None` type is deduced only if class wasn't initialized.
            """
            return self.__client
        
    @property
    def client(self):
        """
        \\@since 0.3.27a2
        ```ts
        "property" in class Fencord
        ```
        Returns reference to `Client` instance inside the class. \\
        The `None` type is deduced only if class wasn't initialized.
        """
        return self.__client
    
    if False: # removed 0.3.27
        @property
        @_tt.deprecated("Deprecated since 0.3.27a2, consider using 'Fencord.tree' property instead")
        def getTree(self):
            """
            \\@since 0.3.25 \\
            \\@deprecated 0.3.27a2
            ```ts
            "property" in class Fencord
            ```
            Returns reference to `CommandTree` instance inside the class.

            This might be needed to invoke decorator `CommandTree.command()` \\
            for slash/application commands, and `CommandTree.sync()` method \\
            in `on_ready()` event. `None` is returned only whether class wasn't \\
            initialized.
            """
            return self.__commandtree
        
    @property
    def tree(self):
        """
        \\@since 0.3.27a2
        ```ts
        "property" in class Fencord
        ```
        Returns reference to `CommandTree` instance inside the class.

        This might be needed to invoke decorator `CommandTree.command()` \\
        for slash/application commands, and `CommandTree.sync()` method \\
        in `on_ready()` event. `None` is returned only whether class wasn't \\
        initialized.
        """
        return self.__commandtree
    
    @property
    def latency(self):
        """
        \\@since 0.3.26rc3
        ```ts
        "property" in class Fencord
        ```
        Returns ping of a client; factual description: \\
        Measures latency between a HEARTBEAT and a HEARTBEAT_ACK in seconds.
        """
        return self.__client.latency
    
    @property
    def id(self):
        """
        \\@since 0.3.27a2
        ```ts
        "property" in class Fencord
        ```
        Returns id of the client
        """
        return self.__client.user.id
    
    @property
    def display(self):
        """
        \\@since 0.3.27a2
        ```ts
        "property" in class Fencord
        ```
        Returns display name of the client
        """
        return self.__client.user.display_name
    
    @property
    def style(self):
        """
        \\@since 0.3.27a4
        ```ts
        "property" in class Fencord
        ```
        Return reference to class `FontStyles`
        """
        return FontStyler

    def __init__(self, intents: _discord.Intents = ..., presences: bool = False, members: bool = False, messageContent: bool = True):
        """
        Fencord
        +++++++
        \\@since 0.3.24 (before 0.3.25 as `DC`)
        ```ts
        in module _tense.fencord
        ```
        Providing methods to help integrating with Discord.
        Parameters:
        - `intents` - Instance of `discord.Intents`.
        - `messageContent` - When `True`, `client.message_content` setting is set to `True`, \\
        `False` otherwise. Defaults to `True`.
        """
        if not isinstance(intents, _discord.Intents) and not _Tense.isEllipsis(intents):
            error = TypeError("parameter 'intends' must have instance of class 'discord.Intents' or an ellipsis, instead received: '{}'".format(type(intents).__name__))
            raise error
        
        i = 0
        a = ("presences", "members", "messageContent")
        
        for e in (presences, members, messageContent):
            
            if not _Tense.isBoolean(e):
                error = TypeError("expected a boolean type in parameter '{}'".format(a[i]))
                raise error
            
            i += 1
            
        if not isinstance(messageContent, bool):
            error = TypeError("Parameter 'messageContent' must have boolean value, instead received: '{}'".format(type(intents).__name__))
            raise err(s)
        
        if _Tense.isEllipsis(intents):
            self.__intents = _discord.Intents.default()
            
        else:
            self.__intents = intents
        
        self.__intents.message_content = messageContent
        self.__intents.presences = presences
        self.__intents.members = members
        self.__client = _discord.Client(intents = self.__intents)
        self.__commandtree = _app_commands.CommandTree(self.__client)
        
        if _FencordOptions.initializationMessage is True:
            e = _Tense.fencordFormat()
            print(f"\33[1;90m{e}\33[1;36m INITIALIZATION\33[0m Class '{type(self).__name__}' was successfully initalized. Line {_inspect.currentframe().f_back.f_lineno}")
            
    @staticmethod
    def returnName(handler: _tt.Union[_discord.Interaction[_discord.Client], _discord.Message], /, target: _tt.Optional[_discord.Member] = None, mention: _tt.Optional[bool] = None, name: _tt.Optional[bool] = None):
        """
        \\@since 0.3.24
        ```ts
        "static method" in class Fencord
        ```
        Shorthand method for faciliating returning name: display name, mention or just username
        """
        m = ""
        if isinstance(target, _discord.Member):
            
            if mention is True:
                m = target.mention
                
            else:
                
                if name is True:
                    m = target.name
                    
                else:
                    m = target.display_name
        else:
            if isinstance(handler, _discord.Interaction):
                
                if mention is True:
                    m = handler.user.mention
                    
                else:
                    
                    if name is True:
                        m = handler.user.name
                        
                    else:
                        m = handler.user.display_name
            else:
                
                if mention is True:
                    m = handler.author.mention
                    
                else:
                    
                    if name is True:
                        m = handler.author.name
                        
                    else:
                        m = handler.author.display_name
        return m
    
    @staticmethod
    def initClient():
        """
        \\@since 0.3.24
        ```ts
        "static method" in class Fencord
        ```
        Shortcut to the following lines of code: 
        ```py \\
        intends = discord.Intends.default()
        intends.message_content = True
        client = discord.Client(intends = intends)
        ```
        Returned is new instance of `Client` class. \\
        It does not apply to variables inside this class.
        """
        intends = _discord.Intents.default()
        intends.message_content = True
        return _discord.Client(intents = intends)
    
    @staticmethod
    def commandInvoked(name: str, author: _tt.Union[_discord.Interaction, _discord.Message], /, parameters: _tt.Optional[dict[str, str]] = None, error: _tt.Optional[str] = None):
        """
        \\@since 0.3.24
        ```ts
        "static method" in class Fencord
        ```
        Prints `INVOCATION` to the console. If `error` is a string, it is returned as `INVOCATION ERROR`
        """
        e = _Tense.fencordFormat()
        if error is None:
            
            if isinstance(author, _discord.Message):
                t = f"\33[1;90m{e}\33[1;38;5;99m INVOCATION\33[0m Invoked message command '{name.lower()}' by '{Fencord.returnName(author, name = True)}'"
                
            else:
                t = f"\33[1;90m{e}\33[1;38;5;99m INVOCATION\33[0m Invoked slash command '{name.lower()}' by '{Fencord.returnName(author, name = True)}'"
            
        else:
            
            if isinstance(author, _discord.Message):
                t = f"\33[1;90m{e}\33[1;38;5;9m INVOCATION ERROR\33[0m Attempt to invoke message command '{name.lower()}' by '{Fencord.returnName(author, name = True)}'"
                
            else:
                t = f"\33[1;90m{e}\33[1;38;5;9m INVOCATION ERROR\33[0m Attempt to invoke slash command '{name.lower()}' by '{Fencord.returnName(author, name = True)}'"
            
        if parameters is not None:
            
            t += " with parameter values: "
            
            for e in parameters:
                t += f"'{e}' -> {parameters[e]}, "
                
            t = _re.sub(r", $", "", t)
            
        if error is not None: t += f"; \33[4m{error}\33[0m"
        return t
    
    @staticmethod
    def commandEquals(message: _discord.Message, *words: str):
        """
        \\@since 0.3.24
        ```ts
        "static method" in class Fencord
        ```
        In reality just string comparison operation; an auxiliary \\
        method for message commands. Case is insensitive
        """
        for string in words:
            if message.content.lower() == string: return True
        return False
    
    def slashCommand(
        
        self,
        name: _tt.Union[str, _translator.locale_str, None] = None,
        description: _tt.Union[str, _translator.locale_str, None] = None,
        nsfw: bool = False,
        parent: _tt.Optional[_app_commands.Group] = None,
        servers: _SlashCommandServers[_abc.Snowflake] = None,
        autoLocaleStrings: bool = True,
        extras: dict[_tt.Any, _tt.Any] = {},
        override: bool = False
        
    ) -> _tt.Callable[[_app_commands.commands.CommandCallback[_app_commands.Group]], _app_commands.Command[_app_commands.Group, ..., _tt.Any]]: # type: ignore # see scrap of code below for more information
        """
        \\@since 0.3.25 (experimental to 0.3.26rc2) \\
        https://aveyzan.glitch.me/tense/py/method.slashCommand.html
        ```ts
        "method" in class Fencord
        ```
        A decorator for slash/application commands. Typically a slight remake of `command()` decorator, but in reality \\
        it invokes method `add_command()`. `LocaleString` = `discord.app_commands.translator.locale_str`

        Parameters (all are optional):
        - `name` - The name of the command (string or instance of `locale_str`). If none provided, command name will \\
        be name of the callback, fully lowercased. If `name` was provided, method will convert the string to lowercase, \\
        if there is necessity. Defaults to `None`.
        - `description` - Description of the command (string or instance of `locale_str`). This shows up in the UI to describe \\
        the command. If not given, it defaults to the first line of the docstring of the callback shortened to 100 \\
        characters. Defaults to `None`.
        - `nsfw` - Indicate, whether this command is NSFW (Not Safe For Work) or not. Defaults to `False`.
        - `parent` (since 0.3.26rc3) - The parent application command. `None` if there isn't one. Defaults to `None`.
        - `servers` - single or many instances of `discord.Object` class in a sequence. These represent servers, \\
        to which restrict the command. If `None` given, command becomes global. Notice there **isn't** such parameter as \\
        `server`, because you can pass normal `discord.Object` class instance to this parameter. Defaults to `None`.
        - `autoLocaleStrings` - When it is `True`, then all translatable strings will implicitly be wrapped into `locale_str` \\
        rather than `str`. This could avoid some repetition and be more ergonomic for certain defaults such as default \\
        command names, command descriptions, and parameter names. Defaults to `True`.
        - `extras` - A dictionary that can be used to store additional data. The library will not touch any values or keys \\
        within this dictionary. Defaults to `None`.
        - `override` - If set to `True`, no exception is raised and command may be simply overwritten. Defaults to `False`.
        """
        if self.__commandtree is None:
            error = _ta.IncorrectValueError(f"since 0.3.25 the '{self!s}' class must be concretized and needs to take '{_discord.Client!s}' class argument.")
            raise error
        
        else:
            
            if isinstance(servers, _abc.Snowflake):
                _servers = tuple([servers])
            
            elif isinstance(servers, _ta.Sequence):
                _servers = tuple([n for n in servers])
            # elif isinstance(servers, Servers): # since 0.3.27a4 (0.3.27 - experimental)
            #    _servers = tuple(servers.list)
            else:
                _servers = None
                
            # suprisingly unexpected error: pylance said that we need 3 type parameters instead of 1
            # but compiler says we need only 1 instead of 3 (typing module TYPE_CHECKING value = true)
            # hence 'type: ignore' in there, still should work as intended
            def _decorator(f: _app_commands.commands.CommandCallback[_app_commands.Group]): # type: ignore
                
                nonlocal name, description, nsfw, parent, autoLocaleStrings, extras, override
                
                if not _inspect.iscoroutinefunction(f):
                    error = TypeError("expected command function to be a coroutine")
                    raise error
                
                cmd = _app_commands.Command(
                    name = name.lower() if _Tense.isString(name) and _reckon(name) > 0 else name if name is not None else f.__name__,
                    description = description if description is not None else "..." if f.__doc__ is None else f.__doc__[:100],
                    callback = f,
                    nsfw = nsfw,
                    parent = parent,
                    auto_locale_strings = autoLocaleStrings,
                    extras = extras if _reckon(extras) > 0 else _abc.MISSING
                )
                
                self.__commandtree.add_command(
                    cmd,
                    # finally came up with a solution with will merge these both parameters
                    # note it always throws an error except something what would bypass this problem
                    guild = _servers[0] if _servers is not None and _reckon(_servers) == 1 else None,
                    guilds = _servers if _servers is not None and _reckon(_servers) > 1 else _abc.MISSING,
                    override = override
                )
                return cmd
            
            return _decorator

    if False: # under experiments since 0.3.27
        @staticmethod
        def fixedEmbed(
            nameValue: __tt.Union[dict[str, str], __tt.Sequence[tuple[str, str]]],
            /,
            title: __tt.Optional[str] = None,
            color: __tt.Union[int, _discord.Color, None] = None,
            type: _EmbedType = "rich",
            url: __tt.Optional[str] = None,
            description: __tt.Optional[str] = None,
            timestamp: __tt.Optional[__dct.datetime] = None,
            inline: bool = True,
            footer: __tt.Optional[str] = None,
            footerUrl: __tt.Optional[str] = None,
            author: __tt.Optional[str] = None,
            authorUrl: __tt.Optional[str] = None,
            authorIconUrl: __tt.Optional[str] = None,
            imageUrl: __tt.Optional[str] = None,
            thumbnailUrl: __tt.Optional[str] = None
        ):
            """
            \\@since 0.3.26
            ```ts
            "static method" in class Fencord
            ```
            Create an `Embed` without 25-field overflow. Good practice for `/help` slash/application command, \\
            hereupon this method has auxiliary character. Amount of `Embed` instances in returned tuple depend \\
            on amount of pairs in `nameValue` parameter: for `(n * 25) + x`, where n ≥ 0 and x ∈ (0; 25) \\
            (assuming x ∈ N; in abridgement: x is integer in range 1-24, including both points) returned are `n` \\
            embed instances. For example: if there was one pair key-value dictionary or sequence with one tuple \\
            with 2 string items, returned will be only one embed, with field declared in parameter `nameValue`: \\
            first item becomes its name, and second - its value.

            :param nameValue: (Field attribute) Dictionary with string keys and string values, list or tuple (since 0.3.27a1 - any sequence)
                with tuples containing 2 string items. Required parameter
            :param title: Title of every embed (string). Defaults to `None`
            :param color: Color of every embed (integer or instance of `discord.Color`/`discord.Colour`). Defaults to `None`
            :param type: Type of every embed from following: 'rich', 'image', 'video', 'gifv', 'article', 'link'. Default is 'rich'.
            :param url: URL of every embed (string). Defaults to `None`
            :param description: Description of every embed (string). Max to 4096 characters. Defaults to `None`.
            :param timestamp: The timestamp of every embed content (instance of `datetime.datetime`). This is an aware datetime.
                If a naive datetime is passed, it is converted to an aware datetime with the local timezone. Defaults to `None`
            :param inline: (Field attribute) Whether the field should be displayed inline (boolean). Defaults to `True`
            :param footer: (Footer attribute) A footer text for every embed (string). If specified, method invokes `set_footer()`
                method, with value specified in the parameter below. Defaults to `None`
            :param footerUrl: (Footer attribute) Footer icon for every embed (string). Defaults to `None`
            :param author: (Author attribute) Author name (string). If specified, method invokes `set_author()` method, with values
                specified in 2 parameters below. Defaults to `None`
            :param authorUrl: (Author attribute) URL of the author (string). Defaults to `None`
            :param authorIconUrl: (Author attribute) URL of the author icon (string). Defaults to `None`
            :param imageUrl: The image URL (string). Defaults to `None`
            :param thumbnailUrl: The thumbnail URL (string). Defaults to `None`
            """
            from ..types_collection import Sequence
            embed = [Fencord.__dc.Embed(color = color, title = title, type = type, url = url, description = description, timestamp = timestamp)]
            i1 = i2 = 0
            if isinstance(nameValue, (Sequence, list, tuple, set, frozenset)):
                d = sorted([n for n in nameValue])
            else:
                d = sorted([(_k, _v) for _k, _v in nameValue.items()])
            if _reckon(d) == 0:
                err, s = (ValueError, "Expected 'nameValue' to be non-empty either dictionary or sequence with 2 string items")
                raise err(s)
            for k, v in d:
                if not _Tense.isString(k) or not _Tense.isString(v):
                    err, s = (TypeError, f"Lacking item or invalid type of a pair: '{k}' -> '{v}'")
                    raise err(s)
                if (i1 - 1) % 25 == 0:
                    embed.append(Fencord.__dc.Embed(color = color, title = title, type = type, url = url, description = description, timestamp = timestamp))
                    i2 += 1
                embed[i2].add_field(name = k, value = v, inline = inline)
                i1 += 1
            for e in embed:
                if not _Tense.isNone(author):
                    e.set_author(name = author, url = authorUrl, icon_url = authorIconUrl)
                if not _Tense.isNone(imageUrl):
                    e.set_image(url = imageUrl)
                if not _Tense.isNone(thumbnailUrl):
                    e.set_thumbnail(url = thumbnailUrl)
                if not _Tense.isNone(footer):
                    e.set_footer(text = footer, icon_url = footerUrl)
            return tuple(embed)
    
    def response(
        self,
        interaction: _discord.Interaction,
        /, # <- 0.3.32
        content: _tt.Optional[str] = None,
        embeds: _tt.Union[_discord.Embed, _ta.Sequence[_discord.Embed], None] = None,
        files: _tt.Union[_discord.File, _ta.Sequence[_discord.File], None] = None,
        view: _tt.Optional[_ui.View] = None,
        textToSpeech: bool = False,
        restricted: bool = False,
        allowedMentions: _tt.Optional[_discord.AllowedMentions] = None,
        suppressEmbeds: bool = False,
        silent: bool = False,
        deleteAfter: _tt.Optional[float] = None,
        poll: _tt.Optional[_discord.Poll] = None
    ):
        """
        \\@since 0.3.27a1 (renamed on 0.3.27a4 from `send()`)
        ```ts
        "method" in class Fencord
        ```
        Send a message via current client
        """
        if isinstance(embeds, _discord.Embed):
            _embeds = tuple([embeds])
        elif isinstance(embeds, _ta.Sequence):
            _embeds = tuple(embeds)
        else:
            _embeds = None
            
        if isinstance(files, _discord.File):
            _files = tuple([files])
            
        elif isinstance(files, _ta.Sequence):
            _files = tuple(files)
        else:
            _files = None
            
        return interaction.response.send_message(
            content = content,
            embed = _embeds[0] if _embeds is not None and _reckon(_embeds) == 1 else _abc.MISSING,
            embeds = _embeds if _embeds is not None and _reckon(_embeds) > 1 else _abc.MISSING,
            file = _files[0] if _files is not None and _reckon(_files) == 1 else _abc.MISSING,
            files = _files if _files is not None and _reckon(_files) > 1 else _abc.MISSING,
            view = view if view is not None else _abc.MISSING,
            tts = textToSpeech,
            ephemeral = restricted,
            allowed_mentions = allowedMentions if allowedMentions is not None else _abc.MISSING,
            suppress_embeds = suppressEmbeds,
            silent = silent,
            delete_after = deleteAfter, # no MISSING since 0.3.32
            poll = poll if poll is not None else _abc.MISSING
        )

    def sync(self, server: _tt.Optional[_abc.Snowflake] = None):
        """
        \\@since 0.3.25
        ```ts
        "method" in class Fencord
        ```
        Sync all slash/application commands, display them on Discord, and translate all strings to `locale_str`. \\
        Used for `on_ready()` event as `await fencord.sync(server?)`. If class wasn't initialized, thrown is error \\
        `_tense.tcs.NotInitializedError`.

        Parameters\\:
        - `server` (Optional) - The server/guild to sync the commands to. If `None` then it syncs all global commands \\
        instead.
        """
        if self.__commandtree is None:
            err, s  = (_ta.NotInitializedError, f"Since 0.3.25 the '{__class__.__name__}' class must be concretized.")
            raise err(s)
        else:
            self.__synccorountine = self.__commandtree.sync(guild = server)
            return self.__synccorountine
    
    def event(self, f: _T_coroutine, /):
        """
        \\@since 0.3.25
        ```ts
        "method" in class Fencord
        ```
        A decorator which defines an event for client to listen to.

        Function injected with this decorator must have valid name, \\
        those can be for example: `on_message()`, `on_ready()`
        """
        if self.__client is None:
            err, s = (_ta.NotInitializedError, f"Since 0.3.25 the '{__class__.__name__}' class must be concretized.")
            raise err(s)
        
        elif not _inspect.iscoroutinefunction(f):
            err, s = (TypeError, "Expected 'coroutine' parameter to be a coroutine.")
            raise err(s)
        
        else:
            return self.__client.event(f)

    if False: # removed 0.3.27
        @staticmethod
        @__tt.deprecated("Deprecated since 0.3.27a1, migrate to FontStyles.bold() method instead")
        def bold(text: str, /):
            """
            \\@since 0.3.25
            ```
            "static method" in class Fencord
            ```
            On Discord: make text bold
            """
            return f"**{text}**"
        @staticmethod
        @__tt.deprecated("Deprecated since 0.3.27a1, migrate to FontStyles.italic() method instead")
        def italic(text: str, /):
            """
            \\@since 0.3.25
            ```
            "static method" in class Fencord
            ```
            On Discord: make text italic
            """
            return f"*{text}*"
        @staticmethod
        @__tt.deprecated("Deprecated since 0.3.27a1, migrate to FontStyles.underline() method instead")
        def underline(text: str, /):
            """
            \\@since 0.3.25
            ```
            "static method" in class Fencord
            ```
            On Discord: make text underlined
            """
            return f"__{text}__"
        @staticmethod
        @__tt.deprecated("Deprecated since 0.3.27a1, migrate to FontStyles.code() method instead")
        def code(text: str, language: __tt.Optional[str] = None, /):
            """
            \\@since 0.3.25
            ```
            "static method" in class Fencord
            ```
            On Discord: coded text
            """
            if language is None:
                return f"`{text}`"
            else:
                return f"```{language}\n{text}\n```"
        @staticmethod
        @__tt.deprecated("Deprecated since 0.3.27a1, migrate to FontStyles.big() method instead")
        def big(text: str, /):
            """
            \\@since 0.3.25
            ```
            "static method" in class Fencord
            ```
            On Discord: make text big
            """
            return f"# {text}"
        @staticmethod
        @__tt.deprecated("Deprecated since 0.3.27a1, migrate to FontStyles.medium() method instead")
        def medium(text: str, /):
            """
            \\@since 0.3.25
            ```
            "static method" in class Fencord
            ```
            On Discord: make text medium
            """
            return f"## {text}"
        @staticmethod
        @__tt.deprecated("Deprecated since 0.3.27a1, migrate to FontStyles.small() method instead")
        def small(text: str, /):
            """
            \\@since 0.3.25
            ```
            "static method" in class Fencord
            ```
            On Discord: make text small
            """
            return f"### {text}"
        @staticmethod
        @__tt.deprecated("Deprecated since 0.3.27a1, migrate to FontStyles.smaller() method instead")
        def smaller(text: str, /):
            """
            \\@since 0.3.25
            ```
            "static method" in class Fencord
            ```
            On Discord: make text smaller
            """
            return f"-# {text}"
        @staticmethod
        @__tt.deprecated("Deprecated since 0.3.27a1, migrate to FontStyles.quote() method instead")
        def quote(text: str, /):
            """
            \\@since 0.3.25
            ```
            "static method" in class Fencord
            ```
            On Discord: transform text to quote
            """
            return f"> {text}"
        @staticmethod
        @__tt.deprecated("Deprecated since 0.3.27a1, migrate to FontStyles.spoiler() method instead")
        def spoiler(text: str, /):
            """
            \\@since 0.3.25
            ```
            "static method" in class Fencord
            ```
            On Discord: make text spoiled
            """
            return f"||{text}||"
        @staticmethod
        @__tt.deprecated("Deprecated since 0.3.27a1, migrate to FontStyles.textUrl() method instead")
        def textUrl(text: str, url: str, hideEmbed = True):
            """
            \\@since 0.3.26a2 \\
            ```
            "static method" in class Fencord
            ```
            On Discord: make text become hyperlink, leading to specified URL
            """
            return f"[{text}](<{url}>)" if hideEmbed else f"[{text}]({url})"
        @staticmethod
        @__tt.deprecated("Deprecated since 0.3.27a1, migrate to FontStyles.silent() method instead")
        def silent(text: str):
            """
            \\@since 0.3.26a3 \\
            ```
            "static method" in class Fencord
            ```
            Make a message silent. Usable for Direct Messages. \\
            As a tip, refer `@silent` as `> ` (quote), and message \\
            MUST be prefixed with `@silent`.
            """
            return f"@silent {text}"

    __all__ = [n for n in locals() if n[:1] != "_"]
    "\\@since 0.3.26rc2"
    __dir__ = lambda self: Fencord.__all__
    "\\@since 0.3.26rc2"

if __name__ == "__main__":
    err = RuntimeError
    s = "This file is not for compiling, consider importing it instead."
    raise err(s)