"""Auto-generated file, do not edit by hand. DZ metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_DZ = PhoneMetadata(id='DZ', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='[17]\\d{1,3}', possible_length=(2, 3, 4)),
    toll_free=PhoneNumberDesc(national_number_pattern='1(?:12|[47]|54\\d)', example_number='14', possible_length=(2, 3, 4)),
    emergency=PhoneNumberDesc(national_number_pattern='1(?:12|[47])', example_number='14', possible_length=(2, 3)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:055|12|[47]|548)|730', example_number='14', possible_length=(2, 3, 4)),
    carrier_specific=PhoneNumberDesc(national_number_pattern='730', example_number='730', possible_length=(3,)),
    sms_services=PhoneNumberDesc(national_number_pattern='730', example_number='730', possible_length=(3,)),
    short_data=True)
