"""Auto-generated file, do not edit by hand. RW metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_RW = PhoneMetadata(id='RW', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='[14]\\d\\d', possible_length=(3,)),
    toll_free=PhoneNumberDesc(national_number_pattern='11[1245]', example_number='111', possible_length=(3,)),
    emergency=PhoneNumberDesc(national_number_pattern='11[12]', example_number='111', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:0[0-2]|1[0-24-6]|2[13]|70|99)|456', example_number='100', possible_length=(3,)),
    short_data=True)
