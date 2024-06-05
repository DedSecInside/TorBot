"""Auto-generated file, do not edit by hand. JO metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_JO = PhoneMetadata(id='JO', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='[19]\\d\\d(?:\\d{2})?', possible_length=(3, 5)),
    toll_free=PhoneNumberDesc(national_number_pattern='1(?:0[235]|1[2-6]|9[127])|911', example_number='102', possible_length=(3,)),
    premium_rate=PhoneNumberDesc(national_number_pattern='9[0-4689]\\d{3}', example_number='90000', possible_length=(5,)),
    emergency=PhoneNumberDesc(national_number_pattern='1(?:12|9[127])|911', example_number='112', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:0[2359]|1[0-68]|9[0-24-79])|9[0-4689]\\d{3}|911', example_number='102', possible_length=(3, 5)),
    carrier_specific=PhoneNumberDesc(national_number_pattern='9[0-4689]\\d{3}', example_number='90000', possible_length=(5,)),
    sms_services=PhoneNumberDesc(national_number_pattern='9[0-4689]\\d{3}', example_number='90000', possible_length=(5,)),
    short_data=True)
