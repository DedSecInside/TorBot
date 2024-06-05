"""Auto-generated file, do not edit by hand. PT metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_PT = PhoneMetadata(id='PT', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='1\\d\\d(?:\\d(?:\\d{2})?)?', possible_length=(3, 4, 6)),
    toll_free=PhoneNumberDesc(national_number_pattern='11[257]|1(?:16\\d\\d|5[1589]|8[279])\\d', example_number='112', possible_length=(3, 4, 6)),
    emergency=PhoneNumberDesc(national_number_pattern='11[25]', example_number='112', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:0(?:45|5[01])|1(?:[2578]|600[06])|4(?:1[45]|4)|583|6(?:1[0236]|3[02]|9[169]))|1(?:1611|59)1|1[068]78|1[08]9[16]|1(?:0[1-38]|40|5[15]|6[258]|82)0', example_number='112', possible_length=(3, 4, 6)),
    short_data=True)
