"""Auto-generated file, do not edit by hand. CU metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_CU = PhoneMetadata(id='CU', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='[12]\\d\\d(?:\\d{3,4})?', possible_length=(3, 6, 7)),
    toll_free=PhoneNumberDesc(national_number_pattern='10[4-7]|(?:116|204\\d)\\d{3}', example_number='104', possible_length=(3, 6, 7)),
    emergency=PhoneNumberDesc(national_number_pattern='10[4-6]', example_number='104', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:0[4-7]|1(?:6111|8)|40)|2045252', example_number='104', possible_length=(3, 6, 7)),
    short_data=True)
