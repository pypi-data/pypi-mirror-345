from __future__ import annotations

from aveytense import *

from aveytense import (
    _Color
)

from ._ᴧv_collection._types import (
    TypeVar as _var,
    Union as _uni,
    Optional as _opt,
    Literal as _lit,
    Sequence as _Sequence
)

from .types_collection import (
    FileType as _FileType,
    EnchantedBookQuantity as _EnchantedBookQuantity
)

from . import util as _util
import re as _re

def _owoify_init(s: str, /) -> str:
    "\\@since 0.3.26b1"
    
    if not Tense.isString(s):
        
        error = ValueError("expected a string")
        raise error
    
    _s = s
    _s = _re.sub(r"\s{2}", " UrU ", _s, flags = _re.M)
    _s = _re.sub(r"XD", "UrU", _s, flags = _re.M | _re.I)
    _s = _re.sub(r":D", "UrU", _s, flags = _re.M)
    _s = _re.sub(r"lenny face", "OwO", _s, flags = _re.M | _re.I)
    _s = _re.sub(r":O", "OwO", _s, flags = _re.M | _re.I)
    _s = _re.sub(r":\)", ":3", _s, flags = _re.M)
    _s = _re.sub(r"\?", " uwu?", _s, flags = _re.M) # ? is a metachar
    _s = _re.sub(r"!", " owo!", _s, flags = _re.M)
    _s = _re.sub(r"; ", "~ ", _s, flags = _re.M)
    _s = _re.sub(r", ", "~ ", _s, flags = _re.M)
    _s = _re.sub(r"you are", "chu is", _s, flags = _re.M)
    _s = _re.sub(r"You are", "chu is".capitalize(), _s, flags = _re.M)
    _s = _re.sub(r"You Are", "chu is".title(), _s, flags = _re.M)
    _s = _re.sub(r"YOU ARE", "chu is".upper(), _s, flags = _re.M)
    _s = _re.sub(r"wat's this", "OwO what's this", _s, flags = _re.M)
    _s = _re.sub(r"Wat's [Tt]his", "OwO What's this", _s, flags = _re.M)
    _s = _re.sub(r"WAT'S THIS", "OwO what's this".upper(), _s, flags = _re.M)
    _s = _re.sub(r"old person", "greymuzzle", _s, flags = _re.M)
    _s = _re.sub(r"Old [Pp]erson", "greymuzzle".capitalize(), _s, flags = _re.M)
    _s = _re.sub(r"OLD PERSON", "greymuzzle".upper(), _s, flags = _re.M)
    _s = _re.sub(r"forgive me father, I have sinned", "sowwy daddy~ I have been naughty", _s, flags = _re.M)
    _s = _re.sub(r"Forgive me father, I have sinned", "sowwy daddy~ I have been naughty".capitalize(), _s, flags = _re.M)
    _s = _re.sub(r"FORGIVE ME FATHER, I HAVE SINNED", "sowwy daddy~ I have been naughty".upper(), _s, flags = _re.M)
    _s = _re.sub(r"your ", "ur ", _s, flags = _re.M)
    _s = _re.sub(r"Your ", "Ur ", _s, flags = _re.M)
    _s = _re.sub(r"YOUR ", "UR ", _s, flags = _re.M)
    _s = _re.sub(r" your", " ur", _s, flags = _re.M)
    _s = _re.sub(r" Your", " Ur", _s, flags = _re.M)
    _s = _re.sub(r" YOUR", " UR", _s, flags = _re.M)
    _s = _re.sub(r"(^your)| your", "ur", _s, flags = _re.M)
    _s = _re.sub(r"(^Your)| Your", "Ur", _s, flags = _re.M)
    _s = _re.sub(r"(^YOUR)| YOUR", "UR", _s, flags = _re.M)
    _s = _re.sub(r"you", "chu", _s, flags = _re.M)
    _s = _re.sub(r"You", "Chu", _s, flags = _re.M)
    _s = _re.sub(r"YOU", "CHU", _s, flags = _re.M)
    _s = _re.sub(r"with ", "wif ", _s, flags = _re.M)
    _s = _re.sub(r"With ", "Wif ", _s, flags = _re.M)
    _s = _re.sub(r"wITH ", "wIF ", _s, flags = _re.M)
    _s = _re.sub(r"what", "wat", _s, flags = _re.M)
    _s = _re.sub(r"What", "Wat", _s, flags = _re.M)
    _s = _re.sub(r"WHAT", "WAT", _s, flags = _re.M)
    _s = _re.sub(r"toe", "toe bean", _s, flags = _re.M)
    _s = _re.sub(r"Toe", "Toe Bean", _s, flags = _re.M)
    _s = _re.sub(r"TOE", "TOE BEAN", _s, flags = _re.M)
    _s = _re.sub(r"this", "dis", _s, flags = _re.M)
    _s = _re.sub(r"This", "Dis", _s, flags = _re.M)
    _s = _re.sub(r"THIS", "DIS", _s, flags = _re.M)
    _s = _re.sub(r"(?!hell\w+)hell", "hecc", _s, flags = _re.M)
    _s = _re.sub(r"(?!Hell\w+)Hell", "Hecc", _s, flags = _re.M)
    _s = _re.sub(r"(?!HELL\w+)HELL", "HECC", _s, flags = _re.M)
    _s = _re.sub(r"the ", "teh ", _s, flags = _re.M)
    _s = _re.sub(r"^the$", "teh", _s, flags = _re.M)
    _s = _re.sub(r"The ", "Teh ", _s, flags = _re.M)
    _s = _re.sub(r"^The$", "Teh", _s, flags = _re.M)
    _s = _re.sub(r"THE ", "TEH ", _s, flags = _re.M)
    _s = _re.sub(r"^THE$", "TEH", _s, flags = _re.M)
    _s = _re.sub(r"tare", "tail", _s, flags = _re.M)
    _s = _re.sub(r"Tare", "Tail", _s, flags = _re.M)
    _s = _re.sub(r"TARE", "TAIL", _s, flags = _re.M)
    _s = _re.sub(r"straight", "gay", _s, flags = _re.M)
    _s = _re.sub(r"Straight", "Gay", _s, flags = _re.M)
    _s = _re.sub(r"STRAIGHT", "GAY", _s, flags = _re.M)
    _s = _re.sub(r"source", "sauce", _s, flags = _re.M)
    _s = _re.sub(r"Source", "Sauce", _s, flags = _re.M)
    _s = _re.sub(r"SOURCE", "SAUCE", _s, flags = _re.M)
    _s = _re.sub(r"(?!slut\w+)slut", "fox", _s, flags = _re.M)
    _s = _re.sub(r"(?!Slut\w+)Slut", "Fox", _s, flags = _re.M)
    _s = _re.sub(r"(?!SLUT\w+)SLUT", "FOX", _s, flags = _re.M)
    _s = _re.sub(r"shout", "awoo", _s, flags = _re.M)
    _s = _re.sub(r"Shout", "Awoo", _s, flags = _re.M)
    _s = _re.sub(r"SHOUT", "AWOO", _s, flags = _re.M)
    _s = _re.sub(r"roar", "rawr", _s, flags = _re.M)
    _s = _re.sub(r"Roar", "Rawr", _s, flags = _re.M)
    _s = _re.sub(r"ROAR", "RAWR", _s, flags = _re.M)
    _s = _re.sub(r"pawlice department", "paw patrol", _s, flags = _re.M)
    _s = _re.sub(r"Paw[Ll]ice [Dd]epartment", "Paw Patrol", _s, flags = _re.M)
    _s = _re.sub(r"PAWLICE DEPARTMENT", "PAW PATROL", _s, flags = _re.M)
    _s = _re.sub(r"police", "pawlice", _s, flags = _re.M)
    _s = _re.sub(r"Police", "Pawlice", _s, flags = _re.M)
    _s = _re.sub(r"POLICE", "PAWLICE", _s, flags = _re.M)
    _s = _re.sub(r"pervert", "furvert", _s, flags = _re.M)
    _s = _re.sub(r"Pervert", "Furvert", _s, flags = _re.M)
    _s = _re.sub(r"PERVERT", "FURVERT", _s, flags = _re.M)
    _s = _re.sub(r"persona", "fursona", _s, flags = _re.M)
    _s = _re.sub(r"Persona", "Fursona", _s, flags = _re.M)
    _s = _re.sub(r"PERSONA", "FURSONA", _s, flags = _re.M)
    _s = _re.sub(r"perfect", "purrfect", _s, flags = _re.M)
    _s = _re.sub(r"Perfect", "Purrfect", _s, flags = _re.M)
    _s = _re.sub(r"PERFECT", "PURRFECT", _s, flags = _re.M)
    _s = _re.sub(r"(?!not\w+)not", "nawt", _s, flags = _re.M)
    _s = _re.sub(r"(?!Not\w+)Not", "Nawt", _s, flags = _re.M)
    _s = _re.sub(r"(?!NOT\w+)NOT", "NAWT", _s, flags = _re.M)
    _s = _re.sub(r"naughty", "nawt", _s, flags = _re.M)
    _s = _re.sub(r"Naughty", "Nawt", _s, flags = _re.M)
    _s = _re.sub(r"NAUGHTY", "NAWT", _s, flags = _re.M)
    _s = _re.sub(r"name", "nyame", _s, flags = _re.M)
    _s = _re.sub(r"Name", "Nyame", _s, flags = _re.M)
    _s = _re.sub(r"NAME", "NYAME", _s, flags = _re.M)
    _s = _re.sub(r"mouth", "maw", _s, flags = _re.M)
    _s = _re.sub(r"Mouth", "Maw", _s, flags = _re.M)
    _s = _re.sub(r"MOUTH", "MAW", _s, flags = _re.M)
    _s = _re.sub(r"love", "luv", _s, flags = _re.M)
    _s = _re.sub(r"Love", "Luv", _s, flags = _re.M)
    _s = _re.sub(r"LOVE", "LUV", _s, flags = _re.M)
    _s = _re.sub(r"lol", "waw", _s, flags = _re.M)
    _s = _re.sub(r"Lol", "Waw", _s, flags = _re.M)
    _s = _re.sub(r"LOL", "WAW", _s, flags = _re.M)
    _s = _re.sub(r"lmao", "hehe~", _s, flags = _re.M)
    _s = _re.sub(r"Lmao", "Hehe~", _s, flags = _re.M)
    _s = _re.sub(r"LMAO", "HEHE~", _s, flags = _re.M)
    _s = _re.sub(r"kiss", "lick", _s, flags = _re.M)
    _s = _re.sub(r"Kiss", "Lick", _s, flags = _re.M)
    _s = _re.sub(r"KISS", "LICK", _s, flags = _re.M)
    _s = _re.sub(r"lmao", "hehe~", _s, flags = _re.M)
    _s = _re.sub(r"Lmao", "Hehe~", _s, flags = _re.M)
    _s = _re.sub(r"LMAO", "HEHE~", _s, flags = _re.M)
    _s = _re.sub(r"hyena", "yeen", _s, flags = _re.M)
    _s = _re.sub(r"Hyena", "Yeen", _s, flags = _re.M)
    _s = _re.sub(r"HYENA", "YEEN", _s, flags = _re.M)
    _s = _re.sub(r"^hi$", "hai", _s, flags = _re.M)
    _s = _re.sub(r" hi ", " hai~ ", _s, flags = _re.M)
    _s = _re.sub(r"hi(,| )", "hai~ ", _s, flags = _re.M)
    _s = _re.sub(r"hi!", "hai!", _s, flags = _re.M)
    _s = _re.sub(r"hi\?", "hai?", _s, flags = _re.M)
    _s = _re.sub(r"^Hi$", "Hai", _s, flags = _re.M)
    _s = _re.sub(r" Hi ", " Hai~ ", _s, flags = _re.M)
    _s = _re.sub(r"Hi(,| )", "Hai~ ", _s, flags = _re.M)
    _s = _re.sub(r"Hi!", "Hai!", _s, flags = _re.M)
    _s = _re.sub(r"Hi\?", "Hai?", _s, flags = _re.M)
    _s = _re.sub(r"^HI$", "HAI", _s, flags = _re.M)
    _s = _re.sub(r" HI ", " HAI~ ", _s, flags = _re.M)
    _s = _re.sub(r"HI(,| )", "HAI~ ", _s, flags = _re.M)
    _s = _re.sub(r"HI!", "HAI!", _s, flags = _re.M)
    _s = _re.sub(r"HI\?", "HAI?", _s, flags = _re.M)
    _s = _re.sub(r"(?!handy)hand", "paw", _s, flags = _re.M)
    _s = _re.sub(r"(?!Handy)Hand", "Paw", _s, flags = _re.M)
    _s = _re.sub(r"(?!HANDY)HAND", "PAW", _s, flags = _re.M)
    _s = _re.sub(r"handy", "pawi", _s, flags = _re.M)
    _s = _re.sub(r"Handy", "Pawi", _s, flags = _re.M)
    _s = _re.sub(r"HANDY", "PAWI", _s, flags = _re.M)
    _s = _re.sub(r"for", "fur", _s, flags = _re.M)
    _s = _re.sub(r"For", "Fur", _s, flags = _re.M)
    _s = _re.sub(r"FOR", "FUR", _s, flags = _re.M)
    _s = _re.sub(r"foot", "footpaw", _s, flags = _re.M)
    _s = _re.sub(r"Foot", "Footpaw", _s, flags = _re.M)
    _s = _re.sub(r"FOOT", "FOOTPAW", _s, flags = _re.M)
    _s = _re.sub(r"father", "daddy", _s, flags = _re.M)
    _s = _re.sub(r"Father", "Daddy", _s, flags = _re.M)
    _s = _re.sub(r"FATHER", "DADDY", _s, flags = _re.M)
    _s = _re.sub(r"fuck", "fluff", _s, flags = _re.M)
    _s = _re.sub(r"Fuck", "Fluff", _s, flags = _re.M)
    _s = _re.sub(r"FUCK", "FLUFF", _s, flags = _re.M)
    _s = _re.sub(r"dragon", "derg", _s, flags = _re.M)
    _s = _re.sub(r"Dragon", "Derg", _s, flags = _re.M)
    _s = _re.sub(r"DRAGON", "DERG", _s, flags = _re.M)
    _s = _re.sub(r"(?!doggy)dog", "good boi", _s, flags = _re.M)
    _s = _re.sub(r"(?!Doggy)Dog", "Good boi", _s, flags = _re.M)
    _s = _re.sub(r"(?!DOGGY)DOG", "GOOD BOI", _s, flags = _re.M)
    _s = _re.sub(r"disease", "pathOwOgen", _s, flags = _re.M)
    _s = _re.sub(r"Disease", "PathOwOgen", _s, flags = _re.M)
    _s = _re.sub(r"DISEASE", "PATHOWOGEN", _s, flags = _re.M)
    _s = _re.sub(r"cyborg|robot|computer", "protogen", _s, flags = _re.M)
    _s = _re.sub(r"Cyborg|Robot|Computer", "Protogen", _s, flags = _re.M)
    _s = _re.sub(r"CYBORG|ROBOT|COMPUTER", "PROTOGEN", _s, flags = _re.M)
    _s = _re.sub(r"(?!children)child", "cub", _s, flags = _re.M)
    _s = _re.sub(r"(?!Children)Child", "Cub", _s, flags = _re.M)
    _s = _re.sub(r"(?!CHILDREN)CHILD", "CUB", _s, flags = _re.M)
    _s = _re.sub(r"(?!cheese[ds])cheese", "sergal", _s, flags = _re.M)
    _s = _re.sub(r"(?!Cheese[ds])Cheese", "Sergal", _s, flags = _re.M)
    _s = _re.sub(r"(?!CHEESE[DS])CHEESE", "SERGAL", _s, flags = _re.M)
    _s = _re.sub(r"celebrity", "popufur", _s, flags = _re.M)
    _s = _re.sub(r"Celebrity", "Popufur", _s, flags = _re.M)
    _s = _re.sub(r"CELEBRITY", "POPUFUR", _s, flags = _re.M)
    _s = _re.sub(r"bye", "bai", _s, flags = _re.M)
    _s = _re.sub(r"Bye", "Bai", _s, flags = _re.M)
    _s = _re.sub(r"BYE", "BAI", _s, flags = _re.M)
    _s = _re.sub(r"butthole", "tailhole", _s, flags = _re.M)
    _s = _re.sub(r"Butthole", "Tailhole", _s, flags = _re.M)
    _s = _re.sub(r"BUTTHOLE", "TAILHOLE", _s, flags = _re.M)
    _s = _re.sub(r"bulge", "bulgy-wulgy", _s, flags = _re.M)
    _s = _re.sub(r"Bulge", "Bulgy-wulgy", _s, flags = _re.M)
    _s = _re.sub(r"BULGE", "BULGY-WULGY", _s, flags = _re.M)
    _s = _re.sub(r"bite", "nom", _s, flags = _re.M)
    _s = _re.sub(r"Bite", "Nom", _s, flags = _re.M)
    _s = _re.sub(r"BITE", "NOM", _s, flags = _re.M)
    _s = _re.sub(r"awful", "pawful", _s, flags = _re.M)
    _s = _re.sub(r"Awful", "Pawful", _s, flags = _re.M)
    _s = _re.sub(r"AWFUL", "PAWFUL", _s, flags = _re.M)
    _s = _re.sub(r"awesome", "pawsome", _s, flags = _re.M)
    _s = _re.sub(r"Awesome", "Pawsome", _s, flags = _re.M)
    _s = _re.sub(r"AWESOME", "PAWSOME", _s, flags = _re.M)
    _s = _re.sub(r"(?!ahh(h)+)ahh", "murr", _s, flags = _re.M)
    _s = _re.sub(r"(?!Ahh[Hh]+)Ahh", "Murr", _s, flags = _re.M)
    _s = _re.sub(r"(?!AHH(H)+)AHH", "MURR", _s, flags = _re.M)
    _s = _re.sub(r"(?![Gg]reymuzzle|[Tt]ail(hole)?|[Pp]aw [Pp]atrol|[Pp]awlice|luv|lick|[Ff]luff|[Ss]ergal|[Pp]awful)l", "w", _s, flags = _re.M)
    _s = _re.sub(r"(?!GREYMUZZLE|TAIL(HOLE)?|PAW PATROL|PAWLICE|L(uv|UV)|L(ick|ICK)|FLUFF|SERGAL|PAWFUL)L", "W", _s, flags = _re.M)
    _s = _re.sub(r"(?![Gg]reymuzzle|ur|[Rr]awr|[Ff]ur(sona|vert)?|[Pp]urrfect|[Vv]ore|[Dd]erg|[Pp]rotogen|[Ss]ergal|[Pp]opufur|[Mm]urr)r", "w", _s, flags = _re.M)
    _s = _re.sub(r"(?!GREYMUZZLE|UR|RAWR|FUR(SONA|VERT)?|PURRFECT|VORE|DERG|PROTOGEN|SERGAL|POPUFUR|MURR)R", "W", _s, flags = _re.M)
    # above: 0.3.26a3, below: 0.3.26b1
    _s = _re.sub(r"gweymuzzwe", "greymuzzle", _s, flags = _re.M)
    _s = _re.sub(r"Gweymuzzwe", "Greymuzzle", _s, flags = _re.M)
    _s = _re.sub(r"GWEYMUZZWE", "GREYMUZZLE", _s, flags = _re.M)
    _s = _re.sub(r"taiwhowe", "tailhole", _s, flags = _re.M)
    _s = _re.sub(r"Taiwhowe", "Tailhole", _s, flags = _re.M)
    _s = _re.sub(r"TAIWHOWE", "TAILHOLE", _s, flags = _re.M)
    _s = _re.sub(r"paw patwow", "paw patrol", _s, flags = _re.M)
    _s = _re.sub(r"Paw Patwow", "Paw Patrol", _s, flags = _re.M)
    _s = _re.sub(r"PAW PATWOW", "PAW PATROL", _s, flags = _re.M)
    _s = _re.sub(r"pawwice", "pawlice", _s, flags = _re.M)
    _s = _re.sub(r"Pawwice", "Pawlice", _s, flags = _re.M)
    _s = _re.sub(r"PAWWICE", "PAWLICE", _s, flags = _re.M)
    _s = _re.sub(r"wuv", "luv", _s, flags = _re.M)
    _s = _re.sub(r"Wuv", "Luv", _s, flags = _re.M)
    _s = _re.sub(r"WUV", "LUV", _s, flags = _re.M)
    _s = _re.sub(r"wick", "lick", _s, flags = _re.M)
    _s = _re.sub(r"Wick", "Lick", _s, flags = _re.M)
    _s = _re.sub(r"WICK", "LICK", _s, flags = _re.M)
    _s = _re.sub(r"fwuff", "fluff", _s, flags = _re.M)
    _s = _re.sub(r"Fwuff", "Fluff", _s, flags = _re.M)
    _s = _re.sub(r"FWUFF", "FLUFF", _s, flags = _re.M)
    _s = _re.sub(r"sewgaw", "sergal", _s, flags = _re.M)
    _s = _re.sub(r"Sewgaw", "Sergal", _s, flags = _re.M)
    _s = _re.sub(r"SEWGAW", "SERGAL", _s, flags = _re.M)
    _s = _re.sub(r"pawfuw", "pawful", _s, flags = _re.M)
    _s = _re.sub(r"Pawfuw", "Pawful", _s, flags = _re.M)
    _s = _re.sub(r"PAWFUW", "PAWFUL", _s, flags = _re.M)
    _s = _re.sub(r"(?!uwu)uw", "ur", _s, flags = _re.M)
    _s = _re.sub(r"(?!Uwu)Uw", "Ur", _s, flags = _re.M)
    _s = _re.sub(r"(?!UWU)UW", "UR", _s, flags = _re.M)
    _s = _re.sub(r"waww", "rawr", _s, flags = _re.M)
    _s = _re.sub(r"Waww", "Rawr", _s, flags = _re.M)
    _s = _re.sub(r"WAWW", "RAWR", _s, flags = _re.M)
    _s = _re.sub(r"fuw", "fur", _s, flags = _re.M)
    _s = _re.sub(r"Fuw", "Fur", _s, flags = _re.M)
    _s = _re.sub(r"FUW", "FUR", _s, flags = _re.M)
    _s = _re.sub(r"furvewt", "furvert", _s, flags = _re.M)
    _s = _re.sub(r"Furvewt", "Furvert", _s, flags = _re.M)
    _s = _re.sub(r"FURVEWT", "FURVERT", _s, flags = _re.M)
    _s = _re.sub(r"puwwfect", "purrfect", _s, flags = _re.M)
    _s = _re.sub(r"Puwwfect", "Purrfect", _s, flags = _re.M)
    _s = _re.sub(r"PUWWFECT", "PURRFECT", _s, flags = _re.M)
    _s = _re.sub(r"vowe", "vore", _s, flags = _re.M)
    _s = _re.sub(r"Vowe", "Vore", _s, flags = _re.M)
    _s = _re.sub(r"VOWE", "VORE", _s, flags = _re.M)
    _s = _re.sub(r"dewg", "derg", _s, flags = _re.M)
    _s = _re.sub(r"Dewg", "Derg", _s, flags = _re.M)
    _s = _re.sub(r"DEWG", "DERG", _s, flags = _re.M)
    _s = _re.sub(r"pwotogen", "protogen", _s, flags = _re.M)
    _s = _re.sub(r"Pwotogen", "Protogen", _s, flags = _re.M)
    _s = _re.sub(r"PWOTOGEN", "PROTOGEN", _s, flags = _re.M)
    _s = _re.sub(r"popufuw", "popufur", _s, flags = _re.M)
    _s = _re.sub(r"Popufuw", "Popufur", _s, flags = _re.M)
    _s = _re.sub(r"POPUFUW", "POPUFUR", _s, flags = _re.M)
    _s = _re.sub(r"muww", "murr", _s, flags = _re.M)
    _s = _re.sub(r"Muww", "Murr", _s, flags = _re.M)
    _s = _re.sub(r"MUWW", "MURR", _s, flags = _re.M)
    # end 0.3.26b1; start 0.3.26rc2
    _s = _re.sub(r"furwy", "fuwwy", _s, flags = _re.M)
    _s = _re.sub(r"Furwy", "Fuwwy", _s, flags = _re.M)
    _s = _re.sub(r"FURWY", "FUWWY", _s, flags = _re.M)
    _s = _re.sub(r"UrU", "UwU", _s, flags = _re.M)
    _s = _re.sub(r"Uru", "Uwu", _s, flags = _re.M)
    _s = _re.sub(r"uru", "uwu", _s, flags = _re.M)
    _s = _re.sub(r"URU", "UWU", _s, flags = _re.M)
    _s = _re.sub(r"femboy", "femboi", _s, flags = _re.M)
    _s = _re.sub(r"Femboy", "Femboi", _s, flags = _re.M)
    _s = _re.sub(r"FEMBOY", "FEMBOI", _s, flags = _re.M)
    _s = _re.sub(r":<", "x3", _s, flags = _re.M)
    # end 0.3.26rc2; start 0.3.26
    _s = _re.sub(r"ding", "beep", _s, flags = _re.M)
    _s = _re.sub(r"Ding", "Beep", _s, flags = _re.M)
    _s = _re.sub(r"DING", "BEEP", _s, flags = _re.M)
    _s = _re.sub(r"shourd", "shouwd", _s, flags = _re.M)
    _s = _re.sub(r"Shourd", "Shouwd", _s, flags = _re.M)
    _s = _re.sub(r"SHOURD", "SHOUWD", _s, flags = _re.M)
    _s = _re.sub(r"course", "couwse", _s, flags = _re.M)
    _s = _re.sub(r"Course", "Couwse", _s, flags = _re.M)
    _s = _re.sub(r"COURSE", "COUWSE", _s, flags = _re.M)
    
    return _s

class _MinecraftDurability:
    """
    \\@since 0.3.37
    
    A class with a list of final properties. \\
    Suffix `_j` means item in Java version. \\
    Suffix `_b` means item in Bedrock version.
    """
    def __init__(self):
        pass
    
    @util.finalproperty
    def helmet_turtleShell(self):
        return 275
    
    @util.finalproperty
    def helmet_leather(self):
        return 55
    
    @util.finalproperty
    def helmet_golden(self):
        return 77
    
    @util.finalproperty
    def helmet_chainmail(self):
        return 165
    
    @util.finalproperty
    def helmet_iron(self):
        return 165
    
    @util.finalproperty
    def helmet_diamond(self):
        return 363
    
    @util.finalproperty
    def helmet_netherite(self):
        return 407
    
    @util.finalproperty
    def chestplate_leather(self):
        return 80
    
    @util.finalproperty
    def chestplate_golden(self):
        return 112
    
    @util.finalproperty
    def chestplate_chainmail(self):
        return 240
    
    @util.finalproperty
    def chestplate_iron(self):
        return 240
    
    @util.finalproperty
    def chestplate_diamond(self):
        return 528
    
    @util.finalproperty
    def chestplate_netherite(self):
        return 592
    
    @util.finalproperty
    def leggings_leather(self):
        return 75
    
    @util.finalproperty
    def leggings_golden(self):
        return 105
    
    @util.finalproperty
    def leggings_chainmail(self):
        return 225
    
    @util.finalproperty
    def leggings_iron(self):
        return 225
    
    @util.finalproperty
    def leggings_diamond(self):
        return 495
    
    @util.finalproperty
    def leggings_netherite(self):
        return 555
    
    @util.finalproperty
    def boots_leather(self):
        return 65
    
    @util.finalproperty
    def boots_golden(self):
        return 91
    
    @util.finalproperty
    def boots_chainmail(self):
        return 195
    
    @util.finalproperty
    def boots_iron(self):
        return 195
    
    @util.finalproperty
    def boots_diamond(self):
        return 429
    
    @util.finalproperty
    def boots_netherite(self):
        return 481
    
    @util.finalproperty
    def bow(self):
        return 384
    
    @util.finalproperty
    def shield(self):
        return 336
    
    @util.finalproperty
    def trident(self):
        return 250
    
    @util.finalproperty
    def elytra(self):
        return 432
    
    @util.finalproperty
    def crossbow_j(self):
        return 465
    
    @util.finalproperty
    def crossbow_b(self):
        return 464
    
    @util.finalproperty
    def brush(self):
        return 64
    
    @util.finalproperty
    def fishingRod_j(self):
        return 64
    
    @util.finalproperty
    def fishingRod_b(self):
        return 384
    
    @util.finalproperty
    def flintAndSteel(self):
        return 64
    
    @util.finalproperty
    def carrotOnStick(self):
        return 25
    
    @util.finalproperty
    def warpedFungusOnStick(self):
        return 100
    
    @util.finalproperty
    def sparkler_b(self):
        return 100
    
    @util.finalproperty
    def glowStick_b(self):
        return 64
    
    @util.finalproperty
    def tool_gold(self):
        return 32
    
    @util.finalproperty
    def tool_wood(self):
        return 65
    
    @util.finalproperty
    def tool_stone(self):
        return 131
    
    @util.finalproperty
    def tool_iron(self):
        return 250
    
    @util.finalproperty
    def tool_diamond(self):
        return 1561
    
    @util.finalproperty
    def tool_netherite(self):
        return 2031
    
    __all__ = [k for k in locals() if not k.startswith("_")]

def owoify(s: str, /):
    """
    \\@since 0.3.9 \\
    \\@lifetime ≥ 0.3.9; < 0.3.24; ≥ 0.3.25
    
    Strict since 0.3.35; same version - moved from `tense.Tense.owoify()`
    
    Joke method translating a string to furry equivalent. \\
    Basing on https://lingojam.com/FurryTalk. Several words \\
    aren't included normally (0.3.26a3, 0.3.26b1, 0.3.26rc2, \\
    0.3.26), still, most are, several have different translations
    """
    return _owoify_init(s)

def uwuify(s: str, /):
    """
    \\@since 0.3.27b2 \\
    \\@lifetime ≥ 0.3.27b2
    
    Strict since 0.3.35; same version - moved from `tense.Tense.uwuify()`
    
    Alias to `~.games.owoify()`
    """
    return _owoify_init(s)

def aeify(s: str, /):
    """
    \\@since 0.3.9 \\
    \\@lifetime ≥ 0.3.9; < 0.3.24; ≥ 0.3.26a4
    
    Strict since 0.3.35; same version - moved from `tense.Tense.aeify()`
    
    Joke method which converts every a and e into \u00E6. Ensure your \\
    compiler reads characters from ISO/IEC 8859-1 encoding, because \\
    without it you might meet question marks instead
    """
    if not Tense.isString(s):
        
        error = ValueError("expected a string")
        raise error
    
    _s, _ae = ("", ["\u00C6", "\u00E6"]) # left - upper, right - lower
    
    for c in s:
        
        if c in "AE":
            _s += _ae[0]
            
        elif c in "ae":
            _s += _ae[1]
            
        else:
            _s += c
            
    return _s

def oeify(s: str, /):
    """
    \\@since 0.3.9 \\
    \\@lifetime ≥ 0.3.9; < 0.3.24; ≥ 0.3.26a4
    ```
    "class method" in class Tense
    ```
    Strict since 0.3.35; same version - moved from `tense.Tense.oeify()`
    
    Joke method which converts every o and e into \u0153. Ensure your \\
    compiler reads characters from ISO/IEC 8859-1 encoding, because \\
    without it you might meet question marks instead
    """
    if not Tense.isString(s):
        
        error = ValueError("expected a string")
        raise error
    
    _s, _oe = ("", ["\u0152", "\u0153"]) # left - upper, right - lower
    
    for c in s:
        
        if c in "OE":
            _s += _oe[0]
            
        elif c in "oe":
            _s += _oe[1]
            
        else:
            _s += c
        
    return _s

class Games:
    """
    \\@since 0.3.25 \\
    \\@author Aveyzan
    ```
    # created 15.07.2024
    in module tense # in tense.games module since 0.3.31
    ```
    Class being a deputy of class `Tense08Games`.
    """
    
    def __init__(self):
        pass
    
    SMASH_HIT_CHECKPOINTS = 13
    """
    \\@since 0.3.26a2 \\
    \\@author Aveyzan
    ```
    // created 20.07.2024
    const in class Games
    ```
    Returns amount of checkpoints in Smash Hit. \\
    12 + endless (1) = 13 (12, because 0-11)
    """
    
    if False: # in code since 0.3.36; unfinished
    
        @classmethod
        def blackjack(self, bet: _opt[int] = None, player = "you"):
            
            _clist = [c for c in "23456789JQKA"] + ["10"]
            _suit = "\u2661 \u2662 \u2664 \u2667".split()
            _hidden = +Color("\u2588\u2588", 8, 249)
            
            _deck = [c1 + c2 for c1 in _clist for c2 in _suit]
            _deck_placeholder = Tense.shuffle(_deck)
            
            def _value(card: str, /):
                    
                if reckon(card) == 3 or card[0] in "J Q K".split():
                    
                    return 10
                
                elif card[0] == "A":
                    
                    return 11
                
                else:
                    
                    return int(card[0])
                
            _phand = [_deck_placeholder.pop(), _deck_placeholder.pop()]
            _dhand = [_deck_placeholder.pop(), _deck_placeholder.pop()]
            
            _pscore = sum(_value(card) for card in _phand)
            _dscore = sum(_value(card) for card in _dhand)
            
            if player.lower() == "you" or reckon(player) == 0:
                _pname = "You"
                
            else:
                _pname = player.capitalize()
            
            if not Tense.isNone(bet) and bet > 0:
                print(Color("{} placed a bet of ${}".format(_pname, bet), 8, 69) % Color.BOLD_ITALIC, "\n")
                
            if _pname == "You":
                print("Your cards: {}".format(" ".join(_phand)))
                print("Your value: {}".format(_pscore), "\n")
                
            else:
                print("{}'s cards: {}".format(" ".join(_phand)))
                print("{}'s value: {}".format(_pscore), "\n")
                
            if _pscore == 21 and _dscore == 21: 
                
                print("Dealer's hand: {}".format(" ".join(_dhand)))
                print("Dealer's score: 21", "\n")
                
                print("Cards left: {}".format(reckon(_deck_placeholder)))
                
            # we cant give entire score for dealer, because we can win more easily
            print("Dealer's hand: {}".format(" ".join(_dhand[0], _hidden)))
            print("Dealer's score: {}".format(_value(_dhand[0])), "\n")
            
                
            if _pscore == 21:
                
                if _pname == "You":
                    print(Color("Congratulations, you got blackjack!", 8, 69) % Color.BOLD_ITALIC)
                    
                    if not Tense.isNone(bet) and bet > 0:
                        print(Color("You won ${}".format(bet * 1.5), 8, 69) % Color.BOLD_ITALIC)
                        
                        
            elif _dscore == 21: ...   
    
class Minesweeper:
    """
    \\@since 0.3.41 (2nd March 2025) https://aveyzan.glitch.me/tense#aveytense.games.Minesweeper
    
    Class featuring minesweeper components. Reference from Windows 7 Minesweeper.
    """
    BEGINNER = (9, 9, 10)
    INTERMEDIATE = (16, 16, 40)
    ADVANCED = (16, 30, 99)
    
    def __init__(self, height = ADVANCED[0], width = ADVANCED[1], mines = ADVANCED[2]):
        
        class _MinesweeperValues(types_collection.Enum): # 0.3.41
            NO_MINE = 0
            MINE = 1
        
        if not Tense.all([e for e in (height, width, mines)], lambda x: Tense.isInteger(x) and Math.isPositive(x)):
            error = TypeError("expected all parameters to have positive integer values")
            raise error
        
        if not (Math.isInRange(height, 9, 24) or Math.isInRange(width, 9, 30) or Math.isInRange(mines, 10, 668)):
            error = ValueError("expected all parameters satisfy following integer value requirements: 'height' -> 9-24, 'width' -> 9-24, 'mines' -> 10-668")
            raise error
            
        if mines > height * width - 12:
            error = ValueError("mines amount cannot be greater than size of the board minus 12")
            raise error
        
        M = _MinesweeperValues
        _mines_left = mines
            
        def _create_new():
            
            nonlocal _mines_left
            
            _table = [M.NO_MINE]
            Tense.clear(_table)
            
            for _ in abroad(width):
                _table.append(Tense.probability2(M.MINE, M.NO_MINE, length = 5))
                
            _mines_left -= Tense.occurrences(_table, M.MINE)
            
            if _mines_left < 0:
                
                for i in abroad(_table):
                    
                    if _table[i] == M.MINE:
                        _table[i] = M.NO_MINE
            
            return _table
        
        def _get_value(x: _MinesweeperValues, /):
            return 9 if x == M.MINE else 0
        
        self.__height = height
        self.__width = width
        self.__mines = mines
        self.__board = [[0]]
        Tense.clear(self.__board)
        
        for _ in abroad(height):
            self.__board.append([_get_value(e) for e in _create_new()])
            
        self.__board = Tense.shuffle(self.__board)    
        
        # enumerate() really helps there!
        for lineI, line in enumerate(self.__board):
            
            for cellI, cell in enumerate(line):
                
                if cell == 0:
                    
                    # north-western corner
                    if lineI == 0 and cellI == 0:
                        
                        _tmp = [
                            self.__board[lineI][cellI + 1],
                            self.__board[lineI + 1][cellI],
                            self.__board[lineI + 1][cellI + 1]
                        ]
                        
                    # north-eastern corner
                    elif lineI == 0 and cellI == reckon(line) - 1:
                        
                        _tmp = [
                            self.__board[lineI][cellI - 1],
                            self.__board[lineI + 1][cellI - 1],
                            self.__board[lineI + 1][cellI]
                        ]
                        
                    # south-western corner
                    elif lineI == reckon(self.__board) - 1 and cellI == 0:
                        
                        _tmp = [
                            self.__board[lineI - 1][cellI],
                            self.__board[lineI - 1][cellI + 1],
                            self.__board[lineI][cellI + 1]
                        ]
                        
                    # south-eastern corner
                    elif lineI == reckon(self.__board) - 1 and cellI == reckon(line) - 1:
                        
                        _tmp = [
                            self.__board[lineI - 1][cellI - 1],
                            self.__board[lineI - 1][cellI],
                            self.__board[lineI][cellI - 1]
                        ]
                    
                    # first row excluding corners
                    elif lineI == 0 and Math.isInRange(cellI, 1, reckon(line) - 2):
                        
                        _tmp = [
                            self.__board[lineI][cellI - 1],
                            self.__board[lineI][cellI + 1],
                            self.__board[lineI + 1][cellI - 1],
                            self.__board[lineI + 1][cellI],
                            self.__board[lineI + 1][cellI + 1]
                        ]
    
                    # last row excluding corners
                    elif lineI == reckon(self.__board) - 1 and Math.isInRange(cellI, 1, reckon(line) - 2):
                        
                        _tmp = [
                            self.__board[lineI - 1][cellI - 1],
                            self.__board[lineI - 1][cellI],
                            self.__board[lineI - 1][cellI + 1],
                            self.__board[lineI][cellI - 1],
                            self.__board[lineI][cellI + 1]
                        ]
                        
                    # first column excluding corners
                    elif Math.isInRange(lineI, 1, reckon(self.__board) - 2) and cellI == 0:
                        
                        _tmp = [
                            self.__board[lineI - 1][cellI],
                            self.__board[lineI - 1][cellI + 1],
                            self.__board[lineI][cellI + 1],
                            self.__board[lineI + 1][cellI],
                            self.__board[lineI + 1][cellI + 1]
                        ]
                        
                    # last column excluding corners
                    elif Math.isInRange(lineI, 1, reckon(self.__board) - 2) and cellI == reckon(line) - 1:
                        
                        _tmp = [
                            self.__board[lineI - 1][cellI - 1],
                            self.__board[lineI - 1][cellI],
                            self.__board[lineI][cellI - 1],
                            self.__board[lineI + 1][cellI - 1],
                            self.__board[lineI + 1][cellI]
                        ]
                    
                    # center; no edge of the game
                    elif Math.isInRange(lineI, 1, reckon(self.__board) - 2) and Math.isInRange(cellI, 1, reckon(line) - 2):
                        
                        _tmp = [
                            self.__board[lineI - 1][cellI - 1],
                            self.__board[lineI - 1][cellI],
                            self.__board[lineI - 1][cellI + 1],
                            self.__board[lineI][cellI - 1],
                            self.__board[lineI][cellI + 1],
                            self.__board[lineI + 1][cellI - 1],
                            self.__board[lineI + 1][cellI],
                            self.__board[lineI + 1][cellI + 1]
                        ]
                        
                    else:
                        _tmp = [0]
                        Tense.clear(_tmp)
                        
                    for e in _tmp:
                        
                        if e == 9:
                            self.__board[lineI][cellI] += 1
    
    @_util.finalproperty
    def board(self):
        """
        \\@since 0.3.41 https://aveyzan.glitch.me/tense#aveytense.games.Minesweeper.board
        
        Returns minesweeper board, as a string nested list.
        
        Possible values: 0-8 and X in strings. 'X' means mine, '0' means empty field
        """
        
        r = [[""]]
        Tense.clear(r)
        
        def _get_value(x: int, /):
            return "X" if x == 9 else str(x)
        
        for line in self.__board:
            
            r.append([_get_value(cell) for cell in line])
                    
        return r
    
    @_util.finalproperty
    def mines(self):
        """
        \\@since 0.3.41 https://aveyzan.glitch.me/tense#aveytense.games.Minesweeper.mines
        
        Returns amount of mines included in the constructor.
        """
        return self.__mines
    
    @_util.finalproperty
    def height(self):
        """
        \\@since 0.3.41 https://aveyzan.glitch.me/tense#aveytense.games.Minesweeper.height
        
        Returns amount of rows (height) included in the costructor.
        """
        return self.__height
    
    @_util.finalproperty
    def width(self):
        """
        \\@since 0.3.41 https://aveyzan.glitch.me/tense#aveytense.games.Minesweeper.width
        
        Returns amount of columns (width) included in the constructor.
        """
        return self.__width
    
    
    def displayBoard(self, colorize = False):
        """
        \\@since 0.3.41 https://aveyzan.glitch.me/tense#aveytense.games.Minesweeper.displayBoard
        
        Displays the minesweeper board. When `colorize` is `True`, prints colorized version \\
        of the board, however, it will bind with longer time waiting.
        """
        
        from time import time
        s, b, c = "", [[""]], time()
        Tense.clear(b)
        b.extend(self.getBoard())
        
        if colorize:
            
            for lineI, line in enumerate(b):
                
                for cellI, cell in enumerate(line):
                    
                    if cell == "0":
                        b[lineI][cellI] = str(Color("0", 8, 249))
                        
                    elif cell == "1":
                        b[lineI][cellI] = str(Color("1", 8, 33))
                        
                    elif cell == "2":
                        b[lineI][cellI] = str(Color("2", 8, 46))
                        
                    elif cell == "3":
                        b[lineI][cellI] = str(Color("3", 8, 196))
                        
                    elif cell == "4":
                        b[lineI][cellI] = str(Color("4", 8, 21))
                        
                    elif cell == "5":
                        b[lineI][cellI] = str(Color("5", 8, 124))
                        
                    elif cell == "6":
                        b[lineI][cellI] = str(Color("6", 8, 51))
                        
                    elif cell == "7":
                        b[lineI][cellI] = str(Color("7", 8, 69))
                        
                    elif cell == "8":
                        b[lineI][cellI] = str(Color("8", 8, 63))    
        
        for line in b:
            s += " ".join(line) + "\n"
    
        print(s)
        print("Execution Time: {}".format(time() - c))
        print("Mines: {} / Height: {} / Width: {}".format(self.__mines, self.__height, self.__width))
        return self
    
    __all__ = [k for k in locals() if k[:1] != "_"]


class Minecraft:
    """@since 0.3.41"""
    
    @util.finalproperty
    def durability(self):
        """
        \\@since 0.3.26?

        To 0.3.37 this constant was a dictionary holding keys being items, and their values being their durabilities. \\
        Since 0.3.37 this constants is object of a local class holding final properties representing items in Minecraft. \\
        To 0.3.42 it was a part of `aveytense.constants` as `MC_DURABILITY`

        If no suffix, item is universal (both Java and Bedrock), suffix `_j` means an item is only on Java, and suffix `_b` \\
        means an item is only on Bedrock version of Minecraft.
        
        """
        return _MinecraftDurability()
    
    
    class potionData(types_collection.Enum): # 0.3.42
        """
        @since 0.3.42
        
        For `~.Minecraft.potion()`
        """
        
        # regular
        water = 0
        mundane = 1
        thick = 2
        awkward = 3
        nightVision = 4
        invisibility = 5
        leaping = 6
        fireResistance = 7
        swiftness = 8
        slowness = 9
        waterBreathing = 10
        healing = 11
        harming = 12
        poison = 13
        regeneration = 14
        strength = 15
        weakness = 16
        luck = 17
        turtleMaster = 18
        slowFalling = 19
        infested = 20
        oozing = 21
        weaving = 22
        windCharged = 23
        
        # level 2
        strongLeaping = 106
        strongSwiftness = 108
        strongSlowness = 109
        strongHealing = 111
        strongHarming = 112
        strongPoison = 113
        strongRegeneration = 114
        strongStrength = 115
        strongTurtleMaster = 118
        
        # extended+
        longNightVision = 204
        longInvisibility = 205
        longLeaping = 206
        longFireResistance = 207
        longSwiftness = 208
        longSlowness = 209
        longWaterBreathing = 210
        longPoison = 213
        longRegeneration = 214
        longStrenth = 215
        longTurtleMaster = 218
        longSlowFalling = 219
    
    @util.finalproperty
    def enchantments(self):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```
        # created 18.07.2024
        ```
        Returns amount of enchantments as for Minecraft 1.21. \\
        It does not include max enchantment level sum.
        
        To 0.3.41 `MC_ENCHANTS` in class `~.games.Games`, and to 0.3.42 `ENCHANTS`. \\
        In the same version removed `MC_ENCHANTS` on `aveytense.constants`
        """
        return 42
    
    @classmethod
    def enchBook(
        self,
        target: str = "@p",
        /, # <- 0.3.26rc2
        quantity: _EnchantedBookQuantity = 1,
        name: _opt[str] = None,
        lore: _opt[str] = None,
        file: _uni[_FileType, None] = None,
        *,
        aquaAffinity: _uni[bool, _lit[1, None]] = None,
        baneOfArthropods: _lit[1, 2, 3, 4, 5, None] = None,
        blastProtection: _lit[1, 2, 3, 4, None] = None,
        breach: _lit[1, 2, 3, 4, None] = None,
        channeling: _uni[bool, _lit[1, None]] = None,
        curseOfBinding: _uni[bool, _lit[1, None]] = None,
        curseOfVanishing: _uni[bool, _lit[1, None]] = None,
        density: _lit[1, 2, 3, 4, 5, None] = None,
        depthStrider: _lit[1, 2, 3, None] = None,
        efficiency: _lit[1, 2, 3, 4, 5, None] = None,
        featherFalling: _lit[1, 2, 3, 4, None] = None,
        fireAspect: _lit[1, 2, None] = None,
        fireProtection: _lit[1, 2, 3, 4, None] = None,
        flame: _uni[bool, _lit[1, None]] = None,
        fortune: _lit[1, 2, 3, None] = None,
        frostWalker: _lit[1, 2, None] = None,
        impaling: _lit[1, 2, 3, 4, 5, None] = None,
        infinity: _uni[bool, _lit[1, None]] = None,
        knockback: _lit[1, 2, None] = None,
        looting: _lit[1, 2, 3, None] = None,
        loyalty: _lit[1, 2, 3, None] = None,
        luckOfTheSea: _lit[1, 2, 3, None] = None,
        lure: _lit[1, 2, 3, None] = None,
        mending: _uni[bool, _lit[1, None]] = None,
        multishot: _uni[bool, _lit[1, None]] = None,
        piercing: _lit[1, 2, 3, 4, None] = None,
        power: _lit[1, 2, 3, 4, 5, None] = None,
        projectileProtection: _lit[1, 2, 3, 4, None] = None,
        protection: _lit[1, 2, 3, 4, None] = None,
        punch: _lit[1, 2, None] = None,
        quickCharge: _lit[1, 2, 3, None] = None,
        respiration: _lit[1, 2, 3, None] = None,
        riptide: _lit[1, 2, 3, None] = None,
        sharpness: _lit[1, 2, 3, 4, 5, None] = None,
        silkTouch: _uni[bool, _lit[1, None]] = None,
        smite: _lit[1, 2, 3, 4, 5, None] = None,
        soulSpeed: _lit[1, 2, 3, None] = None,
        sweepingEdge: _lit[1, 2, 3, None] = None,
        swiftSneak: _lit[1, 2, 3, None] = None,
        thorns: _lit[1, 2, 3, None] = None,
        unbreaking: _lit[1, 2, 3, None] = None,
        windBurst: _lit[1, 2, 3, None] = None
    ):
        """
        \\@since 0.3.25 \\
        \\@modified 0.3.31 (cancelled `StringVar` and `BooleanVar` Tkinter types support + shortened code), 0.3.41 (moved to class `~.Minecraft`)
        https://aveyzan.glitch.me/tense/py/method.mcEnchBook.html
        ```
        # created 18.07.2024
        "class method" in class Games
        ```
        Minecraft `/give <target> ...` command generator for specific enchanted books.
        Basing on https://www.digminecraft.com/generators/give_enchanted_book.php.
        
        Parameters (all are optional):
        - `target` - registered player name or one of special identifiers: `@p` (closest player), \\
        `@a` (all players), `@r` (random player), `@s` (entity running command; will not work in \\
        command blocks). Defaults to `@p`
        - `quantity` - amount of enchanted books to give to the target. Due to fact that enchanted \\
        books aren't stackable, there is restriction put to 36 (total inventory slots, excluding left hand) \\
        instead of 64 maximum. Defaults to 1
        - `name` - name of the enchanted book. Does not affect enchants; it is like putting that book \\
        to anvil and simply renaming. Defaults to `None`
        - `lore` - lore of the enchanted book. Totally I don't know what it does. Defaults to `None`
        - `file` - file to write the command into. This operation will be only done, when command has \\
        been prepared and will be about to be returned. This file will be open in `wt` mode. If file \\
        does not exist, code will attempt to create it. Highly recommended to use file with `.txt` \\
        extension. Defaults to `None`

        Next parameters are enchants. For these having level 1 only, a boolean value can be passed: \\
        in this case `False` will be counterpart of default value `None` of each, `True` means 1.
        """
        
        from aveytense import _get_all_params
        
        # 0.3.41: replaced with __annotations__
        # 0.3.42: using internal function without using 'inspect' components
        _params = _get_all_params(self.enchBook)[:5]
        
        # 'target' must be a string
        if not Tense.isString(target):
            error = TypeError("expected parameter '{}' to be of type 'str'".format(_params[0]))
            raise error
        
        # /give minecraft command begins
        _result = "/give "
        _target = target
        
        # ensure 'target' belongs to one of selectors or matches a-zA-Z0-9_ (player name possible characters)
        _selectors = ("@a", "@s", "@p", "@r")
        
        
        if _target.lower() in _selectors or Tense.test(_target, r"[^a-zA-Z0-9_]"):
            _result += _target
        
        else:
            error = ValueError("parameter '{}' has invalid value, either selector or player name. Possible selectors: {}. Player name may only have chars from ranges: a-z, A-Z, 0-9 and underscores (_)".format(_params[0], ", ".join(_selectors)))
            raise error
        
        # next is adding the 'enchanted_book' item
        _result += " enchanted_book["
        
        if not Tense.isInteger(quantity):
            error = TypeError("expected parameter '{}' to be an integer".format(_params[1]))
            raise error
        
        elif quantity not in abroad(1, 36.1):
            error = ValueError("expected parameter '{}' value to be in range 1-36".format(_params[1]))
            raise error
        
        if not Tense.isNone(name):
            
            if not Tense.isString(name):
                error = TypeError("expected parameter '{}' to be a string or 'None'".format(_params[2]))
                raise error
            
            else:
                _result += "custom_name={}, ".format("{\"text\": \"" + name + "\"}")
        
        if not Tense.isNone(lore):
            
            if not Tense.isString(lore):
                error = TypeError("expected parameter '{}' to be a string or 'None'".format(_params[3]))
                raise error
            
            else:
                _result += "lore=[{}], ".format("{\"text\": \"" + lore + "\"}")
        
        def _fix_name(s: str, /):
            """
            @since 0.3.31
            
            Internal function used to deputize name using CamelCase naming convention \\
            to one, which Python uses in PEP 8 (as well as Minecraft; with _).
            """
    
            _s = ""
            
            for i in abroad(s):
                
                if s[i].isupper():
                    _s += "_" + s[i].lower()
                    
                else:
                    _s += s[i]
                    
            return _s
        
        # instead of using 'inspect.signature()' function, which would include string extraction, and this extraction might take long time
        # 0.3.41: replaced with __annotations__
        # 0.3.42: using internal function without using 'inspect' components
        _enchantments = _get_all_params(self.enchBook)[5:]
        
        _level_1_tuple = (1, True, False)
        _level_2_tuple = (1, 2)
        _level_3_tuple = (1, 2, 3)
        _level_4_tuple = (1, 2, 3, 4)
        _level_5_tuple = (1, 2, 3, 4, 5)
        
        # same can be done with invocation of eval() function in this case, but used is this
        # version to deduce united type of all enchantments
        # 0.3.34: changeover there
        if True:
            _params = Tense.append([0], None, True) # deducing type of list this way (instead of type annotation)
            Tense.clear(_params)
            _params.extend([Tense.eval(e, locals()) for e in _enchantments])
            
        else:
            _params = [p for p in (
                aquaAffinity, baneOfArthropods, blastProtection, breach, channeling, curseOfBinding, curseOfVanishing, density, depthStrider, efficiency, featherFalling, flame, fireAspect, fireProtection, fortune,
                frostWalker, impaling, infinity, knockback, looting, loyalty, luckOfTheSea, lure, mending, multishot, piercing, power, projectileProtection, protection, punch, quickCharge, respiration, riptide,
                sharpness, silkTouch, smite, soulSpeed, sweepingEdge, swiftSneak, thorns, unbreaking, windBurst
            )]
        
        # excluding 'None', it will be inspected later
        # these variables are there to provide changes easier,
        # if there were ones concerning the enchantments' levels
        _required_params = (
            _level_1_tuple, # aqua affinity
            _level_5_tuple, # bane of arthropods
            _level_4_tuple, # blast protection
            _level_4_tuple, # breach
            _level_1_tuple, # channeling
            _level_1_tuple, # curse of binding
            _level_1_tuple, # curse of vanishing
            _level_5_tuple, # density
            _level_3_tuple, # depth strider
            _level_5_tuple, # efficiency
            _level_4_tuple, # feather falling
            _level_2_tuple, # fire aspect
            _level_4_tuple, # fire protection
            _level_1_tuple, # flame
            _level_3_tuple, # fortune
            _level_2_tuple, # frost walker
            _level_5_tuple, # impaling
            _level_1_tuple, # infinity
            _level_2_tuple, # knockback
            _level_3_tuple, # looting
            _level_3_tuple, # loyalty
            _level_3_tuple, # luck of the sea
            _level_3_tuple, # lure
            _level_1_tuple, # mending
            _level_1_tuple, # multishot
            _level_4_tuple, # piercing
            _level_5_tuple, # power
            _level_4_tuple, # projectile protection
            _level_4_tuple, # protection
            _level_2_tuple, # punch
            _level_3_tuple, # quick charge
            _level_3_tuple, # respiration
            _level_3_tuple, # riptide
            _level_5_tuple, # sharpness
            _level_1_tuple, # silk touch
            _level_5_tuple, # smite
            _level_3_tuple, # soul speed
            _level_3_tuple, # sweeping edge
            _level_3_tuple, # swift sneak
            _level_3_tuple, # thorns
            _level_3_tuple, # unbreaking
            _level_3_tuple, # wind burst
        )
        
        _enchantslack = 0
        
        # this dictionary led to error once it occured in following way: {_params[i]: (_enchantments[i], _required_params[i]) for i in abroad(_params)},
        # because there were only 2 pairs and completely unintentional was overriding key values; only changed order of _params and _enchantments went
        # successful (there used assertion statement to figure it out)
        _build = {_enchantments[i]: (_params[i], _required_params[i]) for i in abroad(_params)}
        
        # first inspection before we append 'stored_enchantments' inside squared, unclosed bracket
        for k in _build:
            
            if Tense.isNone(_build[k][0]):
                _enchantslack += 1
        
        # every enchantment has value 'None', what means we can clear the squared bracket
        # ONLY if 'name' and 'lore' have value 'None'
        if _enchantslack == reckon(_enchantments):
            return _result[:-1] if Tense.all([name, lore], lambda x: Tense.isNone(x)) else _result
        
        else:
            _result += "stored_enchantments={"
        
        # further inspection and finalizing the resulted string
        for k in _build:
            
            # skip whether 'None'
            if not Tense.isNone(_build[k][0]):
                
                if _build[k][0] not in _build[k][1]:
                    
                    error = ValueError("expected parameter '{}' to have integer value".format(k) + (" in range 1-{}".format(_build[k][1][-1]) if _build[k][1] != _level_1_tuple else " 1 or boolean value, either 'True' or 'False'"))
                    raise error
                
                if Tense.isBoolean(_build[k][0]):
                    
                    # skip whether 'False'
                    if _build[k][0] is True:
                        _result += "\"{}\": 1, ".format(_fix_name(k))
                        
                elif Tense.isInteger(_build[k][0]):
                    
                    _result += "\"{}\": {}, ".format(_fix_name(k), _build[k][0])
            
            else:
                _enchantslack += 1
        
        # missing closing curly and squared brackets, replace with last comma
        _result = _re.sub(r", $", "}] ", _result) + str(quantity)
        
        if not Tense.isNone(file):
            
            if not isinstance(file, _FileType):
                error = TypeError("parameter 'file' has incorrect file name or type")
                raise error
            
            try:
                f = open(file, "x")
                
            except FileExistsError:
                f = open(file, "wt")
            
            f.write(_result)
            f.close()
            
        return _result
    
    
    if False: # >= 19.03.2025
        
        @classmethod
        def potion(
            self,
            target = "@p",
            /,
            quantity = 1,
            name: _opt[str] = None,
            lore: _opt[str] = None,
            file: _uni[_FileType, None] = None,
            type: potionData = None,
            color: _Color = None,
            duration = 150
        ):
            """
            @since 0.3.42
            
            A potion give command generator. Referring to https://www.gamergeeks.net/apps/minecraft/give-command-generator/potions
            """
            
            from aveytense import _get_all_params
            
            _params = _get_all_params(self.potion)
            
            # 'target' must be a string
            if not Tense.isString(target):
                error = TypeError("expected parameter '{}' to be a string".format(_params[0]))
                raise error
            
            if not Tense.isString(_type):
                error = TypeError("expected parameter '{}' to be a string".format(_params[5]))
                raise error
            
            # /give minecraft command begins
            _result = "/give "
            _target = target
            _type = type.lower()
            
            # ensure 'target' belongs to one of selectors or matches a-zA-Z0-9_ (player name possible characters)
            _selectors = ("@a", "@s", "@p", "@r")
            
            
            if _target.lower() in _selectors or _re.search(r"[^a-zA-Z0-9_]", _target) is None:
                _result += _target
            
            else:
                error = ValueError("parameter '{}' has invalid value, either selector or player name. Possible selectors: {}. Player name may only have chars from ranges: a-z, A-Z, 0-9 and underscores (_)".format(_params[0], ", ".join(_selectors)))
                raise error
            
            
            # we are following latest pattern; previous signatures were using curly brackets after the item name
            if Tense.test(_type, r"^ominous[1-5]?$"):
                _result += " ominous_bottle["
                
            else:
                _result += " potion["
            
            if not Tense.isInteger(quantity):
                error = TypeError("expected parameter '{}' to be an integer".format(_params[1]))
                raise error
            
            elif quantity not in abroad(1, 36.1):
                error = ValueError("expected parameter '{}' value to be in range 1-36".format(_params[1]))
                raise error
            
            if not Tense.isNone(name):
                
                if not Tense.isString(name):
                    error = TypeError("expected parameter '{}' to be a string or 'None'".format(_params[2]))
                    raise error
                
                else:
                    _result += "custom_name={}, ".format("{\"text\": \"" + name + "\"}")
            
            if not Tense.isNone(lore):
                
                if not Tense.isString(lore):
                    error = TypeError("expected parameter '{}' to be a string or 'None'".format(_params[3]))
                    raise error
                
                else:
                    _result += "lore=[{}], ".format("{\"text\": \"" + lore + "\"}")
            
            return _result
    
class Cards:
    """
    @since 0.3.41
    
    Represents gaming cards. A deck makes 52 cards.
    """
    
    def __init__(self, colored = False, ascii_only = False):
            
        _heart = "\u2665" if not ascii_only else "h"
        _diamond = "\u2666" if not ascii_only else "d"
        _spade = "\u2663" if not ascii_only else "s"
        _club = "\u2660" if not ascii_only else "c"
        
        _suits = (_heart, _diamond, _spade, _club)
        _values = [c for c in "123456789JQKA"] + ["10"]
        
        self.__colored = colored
        self.__cards = [v + s for v in _values for s in _suits]
        self.__colored_cards = (
            [Color(v + s, 8, 196) % Color.ITALIC for v in _values for s in _suits if s in (_heart, _diamond)] +
            [Color(v + s, 8, 255) % Color.ITALIC for v in _values for s in _suits if s in (_spade, _club)]
        )
        
    def getCards(self):
        """
        @since 0.3.41
        
        Receive cards
        """
        if self.__colored:
            return self.__colored_cards
        
        else:
            return self.__cards
        
    def shuffle(self):
        """
        @since 0.3.41
        
        Shuffle cards in deck and return reference to this class.
        """
        
        if reckon(self.__cards) == 0:
            error = IndexError("cannot shuffle the deck if it is empty")
            raise error
        
        self.__cards = Tense.shuffle(self.__cards)
        Tense.clear(self.__colored_cards)
        
        for card in self.__cards:
            
            if card.endswith((("\u2665", "\u2666"))):
                self.__colored_cards.append(Color(card, 8, 196) % Color.ITALIC)
                
            else:
                self.__colored_cards.append(Color(card, 8, 255) % Color.ITALIC)
        
        return self
    
    def pick(self):
        """
        @since 0.3.41
        
        Pick a random card from deck.
        """
        if reckon(self.__cards) == 0:
            error = IndexError("cannot pick a card from an empty deck")
            raise error
        
        if self.__colored:
            return Tense.pick(self.__colored_cards)
        
        else:
            return Tense.pick(self.__cards)
        
    def discard(self):
        """
        @since 0.3.41
        
        Removes last card from the deck and returns it.
        """
        if reckon(self.__cards) == 0:
            
            error = IndexError("cannot remove a card from an empty deck")
            raise error
        
        _last = self.__cards.pop(), self.__colored_cards.pop()
        return _last[0] if not self.__colored else _last[1]
    
    def restore(self, colored = False, ascii_only = False):
        """
        @since 0.3.41
        
        Restores the deck.
        """
        _heart = "\u2665" if not ascii_only else "h"
        _diamond = "\u2666" if not ascii_only else "d"
        _spade = "\u2663" if not ascii_only else "s"
        _club = "\u2660" if not ascii_only else "c"
        
        _suits = (_heart, _diamond, _spade, _club)
        _values = [c for c in "23456789JQKA"] + ["10"]
        
        self.__colored = colored
        self.__cards = [v + s for v in _values for s in _suits]
        self.__colored_cards = (
            [Color(v + s, 8, 196) % Color.ITALIC for v in _values for s in _suits if s in (_heart, _diamond)] +
            [Color(v + s, 8, 255) % Color.ITALIC for v in _values for s in _suits if s in (_spade, _club)]
        )
        
        return self
        
    def displayCards(self):
        """
        @since 0.3.41
        
        Allows to display all cards.
        """
        
        from time import time
        
        _s, c = "", time()
        _cards = self.__cards if not self.__colored else self.__colored_cards
        
        for i, card in enumerate(_cards):
            
            if i % 13 == 0:
                
                _s += "\n"
                
            _s += "{} ".format(card)
        
        print(_s)
        print("Execution Time: {}".format(time() - c))
        print("Cards amount: {}".format(reckon(self.__cards)) + "\n")
        
        return self
    
class Sudoku:
    """
    @since 0.3.41
    
    Represents crossword game with numbers.
    
    It is a game where numbers (usually 1-9) cannot repeat in a:
    - square
    - horizontal and vertical lines
    
    Less numbers hinted makes sudoku less possible to solve.
    """
    
    def __init__(self):
        
        from random import sample
        
        _base = 3
        _side = _base ** 2
        _table = (_side, _side) # that can be changed, like 12x12 or 16x16
        _pattern = lambda r = 0, c = 0: (_base * (r % _base) + r // _base + c) % _side
        
        def _shuffle(s: types_collection.Sequence[int], /):
            return sample(s, reckon(s))
        
        _rows = [g * _base + r for g in _shuffle(+abroad(_base)) for r in _shuffle(+abroad(_base))]
        _columns = [g * _base + c for g in _shuffle(+abroad(_base)) for c in _shuffle(+abroad(_base))]
        _numbers = _shuffle(+abroad(1, _side + 1))
        
        self.__board = [[_numbers[_pattern(r, c)] for c in _columns] for r in _rows]
        self.__boardstr = [[str(cell) for cell in row] for row in self.__board]
        self.__base = _base
        self.__side = _side
        self.__format = "{}x{}".format(_table[0], _table[1])
    
    def displayBoard(self):
        """
        @since 0.3.41
        
        Displays the sudoku board, as 9x9
        """
        
        from time import time
        
        _s, c = "\n", time()
        
        for rowI, row in enumerate(self.__boardstr):
            
            if rowI % self.__base == 0:
                
                _s += ((" -" * 3).join("+ ") * 3).rstrip() + " +\n"
            
            for cellI, cell in enumerate(row):
                
                if cellI % self.__base == 0:
                    
                    _s += "| "
                
                _s += "{} ".format(cell)
                
                if cellI == reckon(row) - 1:
                    
                    _s += "| "
                
            _s += "\n"

        _s += ((" -" * 3).join("+ ") * 3).rstrip() + " +\n"
        
        print(_s)
        print("Execution Time: {}".format(time() - c))
        print("Format: {}".format(self.__format))
        
        return self
    
    def cover(self, scheme = 0):
        """
        @since 0.3.41
        
        Allows to cover majority of tiles, replacing them to `.`
        """
        
        if not Tense.isInteger(scheme):
            error = TypeError("expected an integer")
            raise error
        
        # these can change if we dealt with differently formatted board, such as 16x16 and 12x12
        if scheme == 1:
            
            _scheme = [
                (0, 0), (0, 2), (0, 6), (0, 8),
                (1, 1), (1, 7),
                (2, 0), (2, 2), (2, 6), (2, 8),
                (3, 3), (3, 5),
                (4, 4),
                (5, 3), (5, 5),
                (6, 0), (6, 2), (6, 6), (6, 8),
                (7, 1), (7, 7),
                (8, 0), (8, 2), (8, 6), (8, 8)
            ]
            
        elif scheme == 2:
            
            _scheme = [
                (0, 1), (0, 7),
                (1, 0), (1, 2), (1, 6), (1, 8),
                (2, 1), (2, 7),
                (3, 4),
                (4, 3), (4, 5),
                (5, 4),
                (6, 1), (6, 7),
                (7, 0), (7, 2), (7, 6), (7, 8),
                (8, 1), (8, 7)
            ]
            
        elif scheme == 3:
            
            _scheme = [
                (0, 0), (0, 1), (0, 2),
                (1, 3), (1, 4), (1, 5),
                (2, 6), (2, 7), (2, 8),
                (4, 4),
                (6, 0), (6, 1), (6, 2),
                (7, 3), (7, 4), (7, 5),
                (8, 6), (8, 7), (8, 8)
            ]
            
        elif scheme == 4:
            
            _scheme = [
                (0, 0), (0, 2), (0, 6), (0, 8),
                (1, 1), (1, 3), (1, 4), (1, 5), (1, 7),
                (2, 0), (2, 8),
                (3, 1), (3, 7),
                (4, 1), (4, 4), (4, 7),
                (5, 1), (5, 7),
                (6, 0), (6, 8),
                (7, 1), (7, 3), (7, 4), (7, 5), (7, 7),
                (8, 0), (8, 2), (8, 6), (8, 8)
            ]
            
        elif scheme == 5:
            
            _scheme = [
                *tuple([(j, i) for i in abroad(self.__board[0]) for j in (0, 8)]),
                *tuple([(j, i) for i in (0, 8) for j in abroad(1, reckon(self.__board[0]) - 1)]),
                (3, 4), (4, 3), (4, 5), (5, 4)
            ]
            
        elif scheme == 6:
            
            _scheme = [
                (0, 2), (0, 6),
                (1, 1), (1, 3), (1, 4), (1, 5), (1, 7),
                (2, 0), (2, 8),
                (3, 1), (3, 7),
                (4, 1), (4, 4), (4, 7),
                (5, 1), (5, 7),
                (6, 0), (6, 8),
                (7, 1), (7, 3), (7, 4), (7, 5), (7, 7),
                (8, 2), (8, 6),
            ]
            
        elif scheme == 10:
            
            _scheme = [
                (0, 6), (1, 7), (2, 8),
                (0, 3), (1, 4), (2, 5), (3, 6), (4, 7), (5, 8),
                (0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8),
                (3, 0), (4, 1), (5, 2), (6, 3), (7, 4), (8, 5),
                (6, 0), (7, 1), (8, 2)
            ]
            
        elif scheme == 11:
            
            _scheme = [
                (0, 2), (1, 1), (2, 0),
                (0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0),
                (0, 8), (1, 7), (2, 6), (3, 5), (4, 4), (5, 3), (6, 2), (7, 1), (8, 0),
                (3, 8), (4, 7), (5, 6), (6, 5), (7, 4), (8, 3),
                (6, 8), (7, 7), (8, 6)
            ]
            
        elif scheme == 12:
            
            _scheme = [ *tuple([(Tense.random(0, 8), Tense.random(0, 8)) for _ in abroad(30)]) ]
            
        else:
            return self
        
        self.__boardstr = [[("." if (rowI, cellI) not in _scheme else cell) for cellI, cell in enumerate(row)] for rowI, row in enumerate(self.__boardstr)]
            
        return self
    
    def getBoard(self):
        """
        @since 0.3.41
        
        Returns the board as a duodimensional string list
        """
        
        return self.__boardstr
    
    __all__ = [k for k in locals() if not k.startswith("_")]

class TicTacToe:
    """\\@since 0.3.41"""
    
    EMPTY = " "
    O = "o"
    X = "x"
    
    def __init__(self, p1c = X, p2c = O, firstPlayer: _opt[_lit[1, 2]] = None):
        
        if not Tense.isString(p1c, p2c, mode = "or") or Tense.any([p1c.strip(), p2c.strip()], lambda x: not Math.isInRange(reckon(x), 1, 5)) or reckon(p1c) != reckon(p2c):
            error = TypeError("expected chars of same size")
            raise error
        
        if firstPlayer not in (1, 2, None):
            error = TypeError("expected 1, 2 or None in parameter 'firstPlayer'")
            raise error
        
        self.__board = [[self.EMPTY for _ in abroad(3)] for _ in abroad(3)]
        self.__p1c = p1c # player 1 char
        self.__p2c = p2c # player 2 char
        
        if firstPlayer is None:
            _select_first = Tense.pick((1, 2))
            
        else:
            _select_first = firstPlayer
        
        if _select_first == 1:
            self.__pchar = p1c # current player char
            self.__pid = 1 # current player id
            
        else:
            self.__pchar = p2c
            self.__pid = 2
    
    def isBoardFilled(self): # no change in 0.3.41
        """
        \\@since 0.3.7 \\
        \\@lifetime ≥ 0.3.7; < 0.3.24; ≥ 0.3.25
        
        Determine whether the whole board is filled, but there is no winner
        """
        return Tense.all(self.__board, lambda x: Tense.all(x, lambda y: y != self.EMPTY))
    
    def isLineMatched(self): # no change in 0.3.41
        """
        \\@since 0.3.7 \\
        \\@lifetime ≥ 0.3.7; < 0.3.24; ≥ 0.3.25
        
        Determine whether a line is matched on the board
        """
        return ((
            # horizontal match
            Tense.all(self.__board[0], lambda x: x == self.__pchar)) or (
            Tense.all(self.__board[1], lambda x: x == self.__pchar)) or (
            Tense.all(self.__board[2], lambda x: x == self.__pchar)) or (
            
            # vertical match
            Tense.all(self.__board, lambda x: x[0] == self.__pchar)) or (
            Tense.all(self.__board, lambda x: x[1] == self.__pchar)) or (
            Tense.all(self.__board, lambda x: x[2] == self.__pchar)) or (
            
            # cursive match
            Tense.all([self.__board[i][i] for i in abroad(self.__board)], lambda x: x == self.__pchar)) or (
            Tense.all([self.__board[reckon(self.__board) - i - 1][i] for i in abroad(self.__board)], lambda x: x == self.__pchar)
        ))
    
    def clear(self): # Games.ttBoardGenerate (< 0.3.41)
        """
        \\@since 0.3.7 \\
        \\@lifetime ≥ 0.3.7; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25, 0.3.41
        
        Clears the board.
        """
        self.__board = [[self.EMPTY for _ in abroad(3)] for _ in abroad(3)]
        return self
    
    
    def check(self, input: int, /): # Games.ttIndexCheck (< 0.3.41)
        """
        \\@since 0.3.6 \\
        \\@lifetime ≥ 0.3.6; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25, 0.3.41
        
        \\. \\: Tic-Tac-Toe (Tense 0.3.6) \\: \\.
        
        To return `True`, number must be in in range 1-9. There \\
        is template below. Number 0 exits program.

        `1 | 2 | 3` \\
        `4 | 5 | 6` \\
        `7 | 8 | 9` \n
        """
        if type(input) is not str:
            error = TypeError("expected an integer input")
            raise error
        
        
        if input == 0:
            Tense.print("Exitting...")
            exit()
            
        elif Math.isInRange(input, 1, 9):
            
            check = " "
            if input == 1: check = self.__board[0][0]
            elif input == 2: check = self.__board[0][1]
            elif input == 3: check = self.__board[0][2]
            elif input == 4: check = self.__board[1][0]
            elif input == 5: check = self.__board[1][1]
            elif input == 6: check = self.__board[1][2]
            elif input == 7: check = self.__board[2][0]
            elif input == 8: check = self.__board[2][1]
            else: check = self.__board[2][2]

            if check not in (self.__p1c, self.__p2c):
                return True
            
        return False
    
    if False: # Games.ttFirstPlayer (< 0.3.41); removed 0.3.41
        def firstPlayer(self):
            """
            \\@since 0.3.6 \\
            \\@lifetime ≥ 0.3.6; < 0.3.24; ≥ 0.3.25; < 0.3.41 \\
            \\@modified 0.3.25
            ```
            "class method" in class Games
            ```
            . : Tic-Tac-Toe (Tense 0.3.6) : . \n
            Selects first player to start the tic-tac-toe game. \n
            First parameter will take either number 1 or 2, meanwhile second -
            \"x\" or \"o\" (by default). This setting can be changed via `ttChangeChars()` method \n
            **Warning:** do not use `ttChangeChars()` method during the game, do it before, as since you can mistaken other player \n
            Same case goes to this method. Preferably, encase whole game in `while self.ttLineMatch() == 2:` loop
            """
            self.__playerId = Tense.pick((1, 2))
            self.__pchar = ""
            if self.__playerId == 1: self.__pchar = self.__p1c
            else: self.__pchar = self.__p2c
            return self
    
    def nextPlayer(self): # Games.ttNextPlayer (< 0.3.41)
        """
        \\@since 0.3.6 \\
        \\@lifetime ≥ 0.3.6; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25, 0.3.41
        ```
        "class method" in class Games
        ```
        . : Tic-Tac-Toe (Tense 0.3.6) : . \n
        Swaps the player turn to its concurrent (aka other player) \n
        """
        if self.__pid == 1:
            self.__pid = 2
            self.__pchar = self.__p2c
            
        else:
            self.__pid = 1
            self.__pchar = self.__p1c
            
        return self
    
    def displayBoard(self): # Games.ttBoardDisplay (< 0.3.41)
        """
        \\@since 0.3.6 \\
        \\@lifetime ≥ 0.3.6; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25, 0.3.41
        ```
        "class method" in class Games
        ```
        . : Tic-Tac-Toe (Tense 0.3.6) : . \\
        Allows to display the board after modifications, either clearing or placing another char \n
        """
        
        for i in abroad(self.__board):
            print(" | ".join(self.__board[i]))
            
        return self
    
    def set(self, _input: int): # Games.ttBoardLocationSet (< 0.3.41)
        """
        \\@since 0.3.7 \\
        \\@lifetime ≥ 0.3.7; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25, 0.3.41
        ```
        "class method" in class Games
        ```
        This method places a char on the specified index on the board
        """
        while not self.check(_input):
            _input = int(input())
            
        print("Location set! Modifying the board: \n\n")
        if _input == 1: self.__board[0][0] = self.__pchar
        elif _input == 2: self.__board[0][1] = self.__pchar
        elif _input == 3: self.__board[0][2] = self.__pchar
        elif _input == 4: self.__board[1][0] = self.__pchar
        elif _input == 5: self.__board[1][1] = self.__pchar
        elif _input == 6: self.__board[1][2] = self.__pchar
        elif _input == 7: self.__board[2][0] = self.__pchar
        elif _input == 8: self.__board[2][1] = self.__pchar
        else: self.__board[2][2] = self.__pchar
        self.displayBoard()
        return self
    
    if False: # Games.ttBoardClear (< 0.3.41)
        def clearBoard(self): 
            """
            \\@since 0.3.6 \\
            \\@lifetime ≥ 0.3.6; < 0.3.24; ≥ 0.3.25 \\
            \\@modified 0.3.25
            ```
            "class method" in class Games
            ```
            Clears the tic-tac-toe board. It is ready for another game
            """
            self.__board = self.clear()
            return self
    
    def syntax(self): # Games.ttBoardSyntax (< 0.3.41)
        """
        \\@since 0.3.7 \\
        \\@lifetime ≥ 0.3.7; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25
        ```
        "class method" in class Games
        ```
        Displays tic-tac-toe board syntax
        """
        print("""
        1 | 2 | 3
        4 | 5 | 6
        7 | 8 | 9
        """)
        return self
    
    @classmethod
    def match(self, messageIfLineDetected: str = ..., messageIfBoardFilled: str = ...): # Games.ttLineMatch (< 0.3.41)
        """
        \\@since 0.3.6 \\
        \\@lifetime ≥ 0.3.6; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25, 0.3.41
        ```
        "class method" in class Games
        ```
        Matches a line found in the board. Please ensure that the game has started. \\
        Returned values:
        - `0`, when a player matched a line in the board with his character. Game ends after.
        - `1`, when there is a draw - board got utterly filled. Game ends with no winner.
        - `2`, game didn't end, it's still going (message for this case isnt sent, because it can disturb during the game).

        """
        if Tense.any([messageIfLineDetected, messageIfBoardFilled], lambda x: not Tense.isString(x) and not Tense.isEllipsis(x)):
            error = TypeError("expected message(s) to be strings or ellipses")
            raise error
        
        _m1 = "Line detected! Player " + str(self.__pid) + " wins!" if Tense.isEllipsis(messageIfLineDetected) else messageIfLineDetected
        _m2 = "Looks like we have a draw! Nice gameplay!" if Tense.isEllipsis(messageIfBoardFilled) else messageIfBoardFilled
        
        if self.isLineMatched():
            Tense.print(_m1)
            return 0
        
        elif self.isBoardFilled():
            Tense.print(_m2)
            return 1
        
        else:
            return 2

    if False: # Games.ttChangeChars (< 0.3.41); removed 0.3.41
        def change(self, char1: str = "x", char2: str = "o", /):
            """
            \\@since 0.3.7 \\
            \\@lifetime ≥ 0.3.7; < 0.3.24; ≥ 0.3.25 \\
            \\@modified 0.3.25
            ```
            "class method" in class Games
            ```
            Allows to replace x and o chars with different char. \\
            If string is longer than one char, first char of that string is selected \\
            Do it BEFORE starting a tic-tac-toe game
            """
            if reckon(char1) == 1: self.__p1c = char1
            else: self.__p1c = char1[0]
            if reckon(char2) == 1: self.__p2c = char2
            else: self.__p2c = char2[0]
            return self
        
    __all__ = [k for k in locals() if not k.startswith("_")]
    
minecraft = Minecraft()

# _MinecraftDurability = _util.abstract(_MinecraftDurability)
    
__all__ = sorted([k for k in globals() if not k.startswith("_")])

__all_deprecated__ = sorted([n for n in globals() if hasattr(globals()[n], "__deprecated__")])
"""
@since 0.3.41

Returns all deprecated declarations within this module.
"""

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error