"""Auto-generated file, do not edit by hand. GR metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_GR = PhoneMetadata(id='GR', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='1\\d\\d(?:\\d{2,3})?', possible_length=(3, 5, 6)),
    toll_free=PhoneNumberDesc(national_number_pattern='1(?:0[089]|1(?:2|6\\d{3})|66|99)', example_number='100', possible_length=(3, 6)),
    emergency=PhoneNumberDesc(national_number_pattern='1(?:00|12|66|99)', example_number='100', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:0[089]|1(?:2|320|6(?:000|1(?:1[17]|23)))|(?:389|9)9|66)', example_number='100', possible_length=(3, 5, 6)),
    standard_rate=PhoneNumberDesc(national_number_pattern='113\\d\\d', example_number='11300', possible_length=(5,)),
    short_data=True)
