"""Auto-generated file, do not edit by hand. NP metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_NP = PhoneMetadata(id='NP', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='1\\d{2,3}', possible_length=(3, 4)),
    toll_free=PhoneNumberDesc(national_number_pattern='1(?:0[0-36]|12)|1(?:09|11)\\d', example_number='100', possible_length=(3, 4)),
    emergency=PhoneNumberDesc(national_number_pattern='1(?:0[0-3]|12)', example_number='100', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:0(?:[0-36]|98)|1(?:1[1-4]|2))', example_number='100', possible_length=(3, 4)),
    short_data=True)
