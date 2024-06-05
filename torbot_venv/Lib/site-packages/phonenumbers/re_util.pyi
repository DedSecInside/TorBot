from re import Match
from re import Pattern

def fullmatch(pattern: Pattern[str], string: str, flags: int = ...) -> Match[str] | None: ...
