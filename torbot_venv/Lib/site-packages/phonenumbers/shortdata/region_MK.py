"""Auto-generated file, do not edit by hand. MK metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_MK = PhoneMetadata(id='MK', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='1\\d\\d(?:\\d(?:\\d{2})?)?', possible_length=(3, 4, 6)),
    toll_free=PhoneNumberDesc(national_number_pattern='1(?:1(?:2|6\\d{3})|9[2-4])', example_number='112', possible_length=(3, 6)),
    emergency=PhoneNumberDesc(national_number_pattern='1(?:12|9[2-4])', example_number='112', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:1(?:2|8\\d)|3\\d|9[2-4])|1(?:16|2\\d)\\d{3}', example_number='112', possible_length=(3, 4, 6)),
    short_data=True)
