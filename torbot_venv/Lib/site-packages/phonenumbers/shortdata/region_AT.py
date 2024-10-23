"""Auto-generated file, do not edit by hand. AT metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_AT = PhoneMetadata(id='AT', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='[168]\\d\\d(?:\\d(?:\\d{2})?)?', possible_length=(3, 4, 6)),
    toll_free=PhoneNumberDesc(national_number_pattern='1(?:12|2[0238]|3[03]|4[0-247])|1(?:16\\d\\d|4[58])\\d', example_number='112', possible_length=(3, 4, 6)),
    emergency=PhoneNumberDesc(national_number_pattern='1(?:[12]2|33|44)', example_number='112', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:1(?:2|6(?:00[06]|1(?:17|23)))|2[0238]|3[03]|4(?:[0-247]|5[05]|84))|(?:61|8108[1-3])0', example_number='112', possible_length=(3, 4, 6)),
    carrier_specific=PhoneNumberDesc(national_number_pattern='610|810\\d{3}', example_number='610', possible_length=(3, 6)),
    short_data=True)
