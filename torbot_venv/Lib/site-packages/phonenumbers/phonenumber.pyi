from typing import overload

from .util import ImmutableMixin
from .util import UnicodeMixin

class CountryCodeSource:
    UNSPECIFIED: int
    FROM_NUMBER_WITH_PLUS_SIGN: int
    FROM_NUMBER_WITH_IDD: int
    FROM_NUMBER_WITHOUT_PLUS_SIGN: int
    FROM_DEFAULT_COUNTRY: int
    @classmethod
    def to_string(cls, val: int) -> str: ...

class PhoneNumber(UnicodeMixin):
    country_code: int | None
    national_number: int | None
    extension: str | None
    italian_leading_zero: bool | None
    number_of_leading_zeros: int | None
    raw_input: str | None
    country_code_source: int
    preferred_domestic_carrier_code: str | None
    def __init__(
        self,
        country_code: int | None = ...,
        national_number: int | None = ...,
        extension: str | None = ...,
        italian_leading_zero: bool | None = ...,
        number_of_leading_zeros: int | None = ...,
        raw_input: str | None = ...,
        country_code_source: int = ...,
        preferred_domestic_carrier_code: str | None = ...,
    ) -> None: ...
    def clear(self) -> None: ...
    def merge_from(self, other: PhoneNumber) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __unicode__(self) -> str: ...

class FrozenPhoneNumber(PhoneNumber, ImmutableMixin):
    @overload
    def __init__(self, numobj: PhoneNumber) -> None: ...
    @overload
    def __init__(
        self,
        country_code: int | None = ...,
        national_number: int | None = ...,
        extension: str | None = ...,
        italian_leading_zero: bool | None = ...,
        number_of_leading_zeros: int | None = ...,
        raw_input: str | None = ...,
        country_code_source: int = ...,
        preferred_domestic_carrier_code: str | None = ...,
    ) -> None: ...
    def __hash__(self) -> int: ...
