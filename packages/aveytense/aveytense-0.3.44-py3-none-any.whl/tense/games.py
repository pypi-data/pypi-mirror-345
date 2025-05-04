
from aveytense import *
from ._init_types import (
    TypeVar as _var,
    Union as _uni,
    Optional as _opt,
    Literal as _lit
)

from .types_collection import (
    FileType as _FileType,
    EnchantedBookQuantity as _EnchantedBookQuantity
)

import re as _re

_cm = classmethod
_TicTacToeBoard = list[list[str]]

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

def owoify(s: str, /):
    """
    \\@since 0.3.9 \\
    \\@lifetime ≥ 0.3.9; < 0.3.24; ≥ 0.3.25
    ```
    "class method" in class Tense
    ```
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
    ```
    "class method" in class Tense
    ```
    Strict since 0.3.35; same version - moved from `tense.Tense.uwuify()`
    
    Alias to `Tense.owoify()`
    """
    return _owoify_init(s)

def aeify(s: str, /):
    """
    \\@since 0.3.9 \\
    \\@lifetime ≥ 0.3.9; < 0.3.24; ≥ 0.3.26a4
    ```
    "class method" in class Tense
    ```
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
    
    MC_ENCHANTS = 42
    """
    \\@since 0.3.25 \\
    \\@author Aveyzan
    ```
    // created 18.07.2024
    const in class Games
    ```
    Returns amount of enchantments as for Minecraft 1.21. \\
    It does not include max enchantment level sum.
    """
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
    
    @classmethod
    def mcEnchBook(
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
        \\@modified 0.3.31 (cancelled `StringVar` and `BooleanVar` Tkinter types support + shortened code)
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
        
        _params = [k for k in self.mcEnchBook.__annotations__ if k not in ("self", "return")][:5]
        
        # 'target' must be a string
        if not Tense.isString(target):
            error = TypeError("expected parameter '{}' to be of type 'str'".format(_params[0]))
            raise error
        
        # /give minecraft command begins
        _result = "/give "
        _target = target
        
        # ensure 'target' belongs to one of selectors or matches a-zA-Z0-9_ (player name possible characters)
        _selectors = ("@a", "@s", "@p", "@r")
        
        
        if _target.lower() in _selectors or _re.search(r"[^a-zA-Z0-9_]", _target) is None:
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
                
        del _params
        
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
        _enchantments = [k for k in self.mcEnchBook.__annotations__][5:]
        
        _level_1_tuple = (1, True, False)
        _level_2_tuple = (1, 2)
        _level_3_tuple = (1, 2, 3)
        _level_4_tuple = (1, 2, 3, 4)
        _level_5_tuple = (1, 2, 3, 4, 5)
        
        # same can be done with invocation of eval() function in this case, but used is this
        # version to deduce united type of all enchantments
        # 0.3.34: changeover there
        
        if True:
            _params = [True] + [0] + [None] # deducing type of list this way (instead of type annotation)
            _params.clear()
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
            return _result[:-1] if Tense.any([name, lore], lambda x: Tense.isNone(x)) else _result
        
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
                    
            
            
        
            
        
    
    O = "o"
    X = "x"
    __ttBoard = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
    __ttPlayerChar = X
    __ttPlayerId = 1
    __ttPlayerChar1 = "x"
    __ttPlayerChar2 = "o"
    
    @classmethod
    def isBoardFilled(self):
        """
        \\@since 0.3.7 \\
        \\@lifetime ≥ 0.3.7; < 0.3.24; ≥ 0.3.25
        ```
        "class method" in class Games
        ```
        (Tic-Tac-Toe) Determine whether the whole board is filled, but there is no winner
        """
        return (self.__ttBoard[0][0] != self.ttEmptyField() and self.__ttBoard[0][1] != self.ttEmptyField() and self.__ttBoard[0][2] != self.ttEmptyField() and
                self.__ttBoard[1][0] != self.ttEmptyField() and self.__ttBoard[1][1] != self.ttEmptyField() and self.__ttBoard[1][2] != self.ttEmptyField() and
                self.__ttBoard[2][0] != self.ttEmptyField() and self.__ttBoard[2][1] != self.ttEmptyField() and self.__ttBoard[2][2] != self.ttEmptyField())
    @_cm
    def isLineMatched(self):
        """
        \\@since 0.3.7 \\
        \\@lifetime ≥ 0.3.7; < 0.3.24; ≥ 0.3.25
        ```
        "class method" in class Games
        ```
        (Tic-Tac-Toe) Determine whether a line is matched on the board
        """
        return ((
            # horizontal match
            self.__ttBoard[0][0] == self.__ttPlayerChar and self.__ttBoard[0][1] == self.__ttPlayerChar and self.__ttBoard[0][2] == self.__ttPlayerChar) or (
            self.__ttBoard[1][0] == self.__ttPlayerChar and self.__ttBoard[1][1] == self.__ttPlayerChar and self.__ttBoard[1][2] == self.__ttPlayerChar) or (
            self.__ttBoard[2][0] == self.__ttPlayerChar and self.__ttBoard[2][1] == self.__ttPlayerChar and self.__ttBoard[2][2] == self.__ttPlayerChar) or (
            
            # vertical match
            self.__ttBoard[0][0] == self.__ttPlayerChar and self.__ttBoard[1][0] == self.__ttPlayerChar and self.__ttBoard[2][0] == self.__ttPlayerChar) or (
            self.__ttBoard[0][1] == self.__ttPlayerChar and self.__ttBoard[1][1] == self.__ttPlayerChar and self.__ttBoard[2][1] == self.__ttPlayerChar) or (
            self.__ttBoard[0][2] == self.__ttPlayerChar and self.__ttBoard[1][2] == self.__ttPlayerChar and self.__ttBoard[2][2] == self.__ttPlayerChar) or (
            
            # cursive match
            self.__ttBoard[0][0] == self.__ttPlayerChar and self.__ttBoard[1][1] == self.__ttPlayerChar and self.__ttBoard[2][2] == self.__ttPlayerChar) or (
            self.__ttBoard[2][0] == self.__ttPlayerChar and self.__ttBoard[1][1] == self.__ttPlayerChar and self.__ttBoard[0][2] == self.__ttPlayerChar
        ))
    @_cm
    def ttEmptyField(self):
        """
        \\@since 0.3.7 \\
        \\@lifetime ≥ 0.3.7; < 0.3.24; ≥ 0.3.25
        ```
        "class method" in class Games
        ```
        Returns empty field for tic-tac-toe game.
        """
        return " "
    @_cm
    def ttBoardGenerate(self) -> _TicTacToeBoard:
        """
        \\@since 0.3.7 \\
        \\@lifetime ≥ 0.3.7; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25
        ```
        "class method" in class Games
        ```
        Generates a new tic-tac-toe board.
        Content: `list->list(3)->str(3)` (brackets: amount of strings `" "`)
        """
        return Tense.repeat(Tense.repeat(" ", 3), 3)
    @_cm
    def ttIndexCheck(self, input: int, /):
        """
        \\@since 0.3.6 \\
        \\@lifetime ≥ 0.3.6; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25
        ```
        "class method" in class Games
        ```
        . : Tic-Tac-Toe (Tense 0.3.6) : . \n
        To return `True`, number must be in in range 1-9. There \\
        is template below. Number 0 exits program.

        `1 | 2 | 3` \\
        `4 | 5 | 6` \\
        `7 | 8 | 9` \n
        """
        if input == 0:
            Tense.print("Exitting...")
            exit()
        elif input >= 1 and input <= 9:
            check = " "
            if input == 1: check = self.__ttBoard[0][0]
            elif input == 2: check = self.__ttBoard[0][1]
            elif input == 3: check = self.__ttBoard[0][2]
            elif input == 4: check = self.__ttBoard[1][0]
            elif input == 5: check = self.__ttBoard[1][1]
            elif input == 6: check = self.__ttBoard[1][2]
            elif input == 7: check = self.__ttBoard[2][0]
            elif input == 8: check = self.__ttBoard[2][1]
            else: check = self.__ttBoard[2][2]

            if check != self.__ttPlayerChar1 and check != self.__ttPlayerChar2: return True
        return False
    
    @_cm
    def ttFirstPlayer(self):
        """
        \\@since 0.3.6 \\
        \\@lifetime ≥ 0.3.6; < 0.3.24; ≥ 0.3.25 \\
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
        self.__ttPlayerId = Tense.pick((1, 2))
        self.__ttPlayerChar = ""
        if self.__ttPlayerId == 1: self.__ttPlayerChar = self.__ttPlayerChar1
        else: self.__ttPlayerChar = self.__ttPlayerChar2
        return self
    @_cm
    def ttNextPlayer(self):
        """
        \\@since 0.3.6 \\
        \\@lifetime ≥ 0.3.6; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25
        ```
        "class method" in class Games
        ```
        . : Tic-Tac-Toe (Tense 0.3.6) : . \n
        Swaps the player turn to its concurrent (aka other player) \n
        """
        if self.__ttPlayerId == 1:
            self.__ttPlayerId = 2
            self.__ttPlayerChar = self.__ttPlayerChar2
        else:
            self.__ttPlayerId = 1
            self.__ttPlayerChar = self.__ttPlayerChar1
        return self
    @_cm
    def ttBoardDisplay(self):
        """
        \\@since 0.3.6 \\
        \\@lifetime ≥ 0.3.6; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25
        ```
        "class method" in class Games
        ```
        . : Tic-Tac-Toe (Tense 0.3.6) : . \\
        Allows to display the board after modifications, either clearing or placing another char \n
        """
        print(self.__ttBoard[0][0] + " | " + self.__ttBoard[0][1] + " | " + self.__ttBoard[0][2])
        print(self.__ttBoard[1][0] + " | " + self.__ttBoard[1][1] + " | " + self.__ttBoard[1][2])
        print(self.__ttBoard[2][0] + " | " + self.__ttBoard[2][1] + " | " + self.__ttBoard[2][2])
        return self
    @_cm
    def ttBoardLocationSet(self, _input: int):
        """
        \\@since 0.3.7 \\
        \\@lifetime ≥ 0.3.7; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25
        ```
        "class method" in class Games
        ```
        This method places a char on the specified index on the board
        """
        while not self.ttIndexCheck(_input):
            _input = int(input())
        print("Location set! Modifying the board: \n\n")
        if _input == 1: self.__ttBoard[0][0] = self.__ttPlayerChar
        elif _input == 2: self.__ttBoard[0][1] = self.__ttPlayerChar
        elif _input == 3: self.__ttBoard[0][2] = self.__ttPlayerChar
        elif _input == 4: self.__ttBoard[1][0] = self.__ttPlayerChar
        elif _input == 5: self.__ttBoard[1][1] = self.__ttPlayerChar
        elif _input == 6: self.__ttBoard[1][2] = self.__ttPlayerChar
        elif _input == 7: self.__ttBoard[2][0] = self.__ttPlayerChar
        elif _input == 8: self.__ttBoard[2][1] = self.__ttPlayerChar
        else: self.__ttBoard[2][2] = self.__ttPlayerChar
        self.ttBoardDisplay()
        return self
    @_cm
    def ttBoardClear(self):
        """
        \\@since 0.3.6 \\
        \\@lifetime ≥ 0.3.6; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25
        ```
        "class method" in class Games
        ```
        Clears the tic-tac-toe board. It is ready for another game
        """
        self.__ttBoard = self.ttBoardGenerate()
        return self
    @_cm
    def ttBoardSyntax(self):
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
    @_cm
    def ttLineMatch(self, messageIfLineDetected: str = "Line detected! Player " + str(__ttPlayerId) + " wins!", messageIfBoardFilled: str = "Looks like we have a draw! Nice gameplay!"):
        """
        \\@since 0.3.6 \\
        \\@lifetime ≥ 0.3.6; < 0.3.24; ≥ 0.3.25 \\
        \\@modified 0.3.25
        ```
        "class method" in class Games
        ```
        Matches a line found in the board. Please ensure that the game has started. \\
        Returned values:
        - `0`, when a player matched a line in the board with his character. Game ends after.
        - `1`, when there is a draw - board got utterly filled. Game ends with no winner.
        - `2`, game didn't end, it's still going (message for this case isnt sent, because it can disturb during the game).

        """
        if self.isLineMatched():
            Tense.print(messageIfLineDetected)
            return 0
        elif self.isBoardFilled():
            Tense.print(messageIfBoardFilled)
            return 1
        else: return 2

    @_cm
    def ttChangeChars(self, char1: str = "x", char2: str = "o", /):
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
        if reckon(char1) == 1: self.__ttPlayerChar1 = char1
        else: self.__ttPlayerChar1 = char1[0]
        if reckon(char2) == 1: self.__ttPlayerChar2 = char2
        else: self.__ttPlayerChar2 = char2[0]
        return self