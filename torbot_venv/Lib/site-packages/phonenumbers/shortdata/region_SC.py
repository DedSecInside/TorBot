"""Auto-generated file, do not edit by hand. SC metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_SC = PhoneMetadata(id='SC', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='[19]\\d{2,3}', possible_length=(3, 4)),
    toll_free=PhoneNumberDesc(national_number_pattern='1(?:1[1468]|60)|999', example_number='111', possible_length=(3,)),
    emergency=PhoneNumberDesc(national_number_pattern='999', example_number='999', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:[06]\\d|1[0-246-8]|2[0-8]|3[13]|4[0-2]|5[15]|7[124-6]|8[158]|9[015])|9(?:6\\d\\d|99)', example_number='100', possible_length=(3, 4)),
    short_data=True)
