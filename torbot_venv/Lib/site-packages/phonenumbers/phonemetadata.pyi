from collections.abc import Callable
import threading

from .util import ImmutableMixin
from .util import UnicodeMixin

REGION_CODE_FOR_NON_GEO_ENTITY: str

class NumberFormat(UnicodeMixin, ImmutableMixin):
    pattern: str | None
    format: str | None
    leading_digits_pattern: list[str]
    national_prefix_formatting_rule: str | None
    national_prefix_optional_when_formatting: bool | None
    domestic_carrier_code_formatting_rule: str | None
    def __init__(
        self,
        pattern: str | None = ...,
        format: str | None = ...,
        leading_digits_pattern: list[str] | None = ...,
        national_prefix_formatting_rule: str | None = ...,
        national_prefix_optional_when_formatting: bool | None = ...,
        domestic_carrier_code_formatting_rule: str | None = ...,
    ) -> None: ...
    def merge_from(self, other: NumberFormat) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __unicode__(self) -> str: ...

class PhoneNumberDesc(UnicodeMixin, ImmutableMixin):
    national_number_pattern: str | None
    example_number: str | None
    possible_length: tuple[int, ...]
    possible_length_local_only: tuple[int, ...]
    def __init__(
        self,
        national_number_pattern: str | None = ...,
        example_number: str | None = ...,
        possible_length: tuple[int, ...] | None = ...,
        possible_length_local_only: tuple[int, ...] | None = ...,
    ) -> None: ...
    def merge_from(self, other: PhoneNumberDesc) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __unicode__(self) -> str: ...

def _same_pattern(left: PhoneNumberDesc | None, right: PhoneNumberDesc | None) -> bool: ...

class PhoneMetadata(UnicodeMixin, ImmutableMixin):
    _metadata_lock: threading.Lock
    _region_available: dict[str, Callable[[str], None] | None]
    _short_region_available: dict[str, Callable[[str], None] | None]
    _country_code_available: dict[int, Callable[[int], None] | None]
    _region_metadata: dict[str, PhoneMetadata]
    _short_region_metadata: dict[str, PhoneMetadata]
    _country_code_metadata: dict[int, PhoneMetadata]
    general_desc: PhoneNumberDesc | None
    fixed_line: PhoneNumberDesc | None
    mobile: PhoneNumberDesc | None
    toll_free: PhoneNumberDesc | None
    premium_rate: PhoneNumberDesc | None
    shared_cost: PhoneNumberDesc | None
    personal_number: PhoneNumberDesc | None
    voip: PhoneNumberDesc | None
    pager: PhoneNumberDesc | None
    uan: PhoneNumberDesc | None
    emergency: PhoneNumberDesc | None
    voicemail: PhoneNumberDesc | None
    short_code: PhoneNumberDesc | None
    standard_rate: PhoneNumberDesc | None
    carrier_specific: PhoneNumberDesc | None
    sms_services: PhoneNumberDesc | None
    no_international_dialling: PhoneNumberDesc | None
    id: str
    country_code: int | None
    international_prefix: str | None
    preferred_international_prefix: str | None
    national_prefix: str | None
    preferred_extn_prefix: str | None
    national_prefix_for_parsing: str | None
    national_prefix_transform_rule: str | None
    same_mobile_and_fixed_line_pattern: bool
    number_format: list[NumberFormat]
    intl_number_format: list[NumberFormat]
    main_country_for_code: bool
    leading_digits: str | None
    leading_zero_possible: bool
    mobile_number_portable_region: bool
    short_data: bool
    @classmethod
    def metadata_for_region(cls, region_code: str, default: PhoneMetadata | None = ...) -> PhoneMetadata | None: ...
    @classmethod
    def short_metadata_for_region(cls, region_code: str, default: PhoneMetadata | None = ...) -> PhoneMetadata | None: ...
    @classmethod
    def metadata_for_nongeo_region(cls, country_code: int, default: PhoneMetadata | None = ...) -> PhoneMetadata | None: ...
    @classmethod
    def metadata_for_region_or_calling_code(cls, country_calling_code: int, region_code: str) -> PhoneMetadata | None: ...
    @classmethod
    def register_region_loader(cls, region_code: str, loader: Callable[[str], None]) -> None: ...
    @classmethod
    def register_short_region_loader(cls, region_code: str, loader: Callable[[str], None]) -> None: ...
    @classmethod
    def register_nongeo_region_loader(cls, country_code: int, loader: Callable[[int], None]) -> None: ...
    @classmethod
    def load_all(cls) -> None: ...
    def __init__(
        self,
        id: str,
        general_desc: PhoneNumberDesc | None = ...,
        fixed_line: PhoneNumberDesc | None = ...,
        mobile: PhoneNumberDesc | None = ...,
        toll_free: PhoneNumberDesc | None = ...,
        premium_rate: PhoneNumberDesc | None = ...,
        shared_cost: PhoneNumberDesc | None = ...,
        personal_number: PhoneNumberDesc | None = ...,
        voip: PhoneNumberDesc | None = ...,
        pager: PhoneNumberDesc | None = ...,
        uan: PhoneNumberDesc | None = ...,
        emergency: PhoneNumberDesc | None = ...,
        voicemail: PhoneNumberDesc | None = ...,
        short_code: PhoneNumberDesc | None = ...,
        standard_rate: PhoneNumberDesc | None = ...,
        carrier_specific: PhoneNumberDesc | None = ...,
        sms_services: PhoneNumberDesc | None = ...,
        no_international_dialling: PhoneNumberDesc | None = ...,
        country_code: int | None = ...,
        international_prefix: str | None = ...,
        preferred_international_prefix: str | None = ...,
        national_prefix: str | None = ...,
        preferred_extn_prefix: str | None = ...,
        national_prefix_for_parsing: str | None = ...,
        national_prefix_transform_rule: str | None = ...,
        number_format: list[NumberFormat] | None = ...,
        intl_number_format: list[NumberFormat] | None = ...,
        main_country_for_code: bool = ...,
        leading_digits: str | None = ...,
        leading_zero_possible: bool = ...,
        mobile_number_portable_region: bool = ...,
        short_data: bool = ...,
        register: bool = ...,
    ) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __unicode__(self) -> str: ...
