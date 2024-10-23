"""Auto-generated file, do not edit by hand. SV metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_SV = PhoneMetadata(id='SV', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='[149]\\d\\d(?:\\d{2,3})?', possible_length=(3, 5, 6)),
    toll_free=PhoneNumberDesc(national_number_pattern='116\\d{3}|911', example_number='911', possible_length=(3, 6)),
    emergency=PhoneNumberDesc(national_number_pattern='91[13]', example_number='911', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:1(?:2|6111)|2[136-8]|3[0-6]|9[05])|40404|9(?:1\\d|29)', example_number='112', possible_length=(3, 5, 6)),
    carrier_specific=PhoneNumberDesc(national_number_pattern='404\\d\\d', example_number='40400', possible_length=(5,)),
    sms_services=PhoneNumberDesc(national_number_pattern='404\\d\\d', example_number='40400', possible_length=(5,)),
    short_data=True)
