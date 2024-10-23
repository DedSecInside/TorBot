"""Auto-generated file, do not edit by hand. HU metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_HU = PhoneMetadata(id='HU', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='1\\d{2,5}', possible_length=(3, 4, 5, 6)),
    toll_free=PhoneNumberDesc(national_number_pattern='1(?:0[457]|12|4[0-4]\\d)|1(?:16\\d|37|45)\\d\\d', example_number='104', possible_length=(3, 4, 5, 6)),
    emergency=PhoneNumberDesc(national_number_pattern='1(?:0[457]|12)', example_number='104', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:0[457]|1(?:2|6(?:000|1(?:11|23))|800)|2(?:0[0-4]|1[013489]|2[0-5]|3[0-46]|4[0-24-68]|5[0-2568]|6[06]|7[0-25-7]|8[028]|9[08])|37(?:00|37|7[07])|4(?:0[0-5]|1[013-8]|2[034]|3[23]|4[02-9]|5(?:00|41|67))|777|8(?:1[27-9]|2[04]|40|[589]))', example_number='104', possible_length=(3, 4, 5, 6)),
    carrier_specific=PhoneNumberDesc(national_number_pattern='1(?:4[0-4]|77)\\d|1(?:18|2|45)\\d\\d', example_number='1200', possible_length=(4, 5)),
    sms_services=PhoneNumberDesc(national_number_pattern='184\\d', example_number='1840', possible_length=(4,)),
    short_data=True)
