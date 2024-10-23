"""Auto-generated file, do not edit by hand. DK metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_DK = PhoneMetadata(id='DK', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='1\\d{2,5}', possible_length=(3, 4, 5, 6)),
    toll_free=PhoneNumberDesc(national_number_pattern='11(?:[24]|6\\d{3})', example_number='112', possible_length=(3, 6)),
    emergency=PhoneNumberDesc(national_number_pattern='11[24]', example_number='112', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:1(?:[2-48]|6(?:00[06]|111))|619[0-2]|8(?:01|1[0238]|28|30|5[13]|8[18]))', example_number='112', possible_length=(3, 4, 5, 6)),
    short_data=True)
