"""Auto-generated file, do not edit by hand. JP metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_JP = PhoneMetadata(id='JP', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='[01]\\d\\d(?:\\d{7})?', possible_length=(3, 10)),
    toll_free=PhoneNumberDesc(national_number_pattern='11[089]', example_number='110', possible_length=(3,)),
    emergency=PhoneNumberDesc(national_number_pattern='11[09]', example_number='110', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='000[259]\\d{6}|1(?:0[24]|1[089]|44|89)', example_number='102', possible_length=(3, 10)),
    sms_services=PhoneNumberDesc(national_number_pattern='000[259]\\d{6}', example_number='0002000000', possible_length=(10,)),
    short_data=True)
