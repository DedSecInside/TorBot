"""Auto-generated file, do not edit by hand. OM metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_OM = PhoneMetadata(id='OM', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='[19]\\d{3}', possible_length=(4,)),
    toll_free=PhoneNumberDesc(national_number_pattern='1444|999\\d', example_number='1444', possible_length=(4,)),
    emergency=PhoneNumberDesc(national_number_pattern='1444|9999', example_number='1444', possible_length=(4,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:111|222|4(?:4[0-5]|50|66|7[7-9])|51[0-8])|9999|1(?:2[3-5]|3[0-2]|50)\\d', example_number='1111', possible_length=(4,)),
    short_data=True)
