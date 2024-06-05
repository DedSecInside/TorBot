"""Auto-generated file, do not edit by hand. LK metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_LK = PhoneMetadata(id='LK', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='1\\d{2,3}', possible_length=(3, 4)),
    toll_free=PhoneNumberDesc(national_number_pattern='11[02689]', example_number='110', possible_length=(3,)),
    emergency=PhoneNumberDesc(national_number_pattern='11[02689]', example_number='110', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:1[024-9]|3(?:00|1[2-49]|2[23]|3[1-3]|44|5[07]|[67]9|88|9[039])|9(?:0[0-2589]|1[0-357-9]|2[0-25689]|3[0389]|4[0489]|5[014-69]|6[0-2689]|7[03579]|8[02457-9]|9[0-2569]))', example_number='110', possible_length=(3, 4)),
    short_data=True)
