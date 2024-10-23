from .util import U_EMPTY_STRING, U_PLUS
from .phonenumber import PhoneNumber

_LOCALE_NORMALIZATION_MAP: dict[str, str]

def _may_fall_back_to_english(lang: str) -> bool: ...
def _full_locale(lang: str, script: str | None, region: str | None) -> str: ...
def _find_lang(langdict: dict[str, str], lang: str, script: str | None, region: str | None) -> str | None: ...
def _prefix_description_for_number(
    data: dict[str, dict[str, str]],
    longest_prefix: int,
    numobj: PhoneNumber,
    lang: str,
    script: str | None = ...,
    region: str | None = ...,
) -> str: ...
