import phonenumbers

class PhoneNumber:
    number: str;
    national_number: str;
    international_number: str;
    dialCode: str;
    country_code: str;

    def __init__(self, number, country_code=None):
        parse = self.parse(number,country_code);
        if parse is not None:
            (
                self.number, self.national_number, 
                self.international_number, self.dialCode,self.country_code
            ) = parse
            try:
                self.parsed = phonenumbers.parse(self.number, self.country_code)
            except:
                pass
    
    def parse(self, _number, _country_code=None):
        try:
            number = _number
            country_code = str(_country_code).upper();
            parsed = phonenumbers.parse(number, country_code);
            national_number = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL);
            international_number = phonenumbers.format_number(phonenumbers.parse(number, country_code), phonenumbers.PhoneNumberFormat.INTERNATIONAL);
            dialCode = parsed.country_code;
            if str(dialCode).startswith('+') is False:
                dialCode = f"+{dialCode}"
            country_code = phonenumbers.region_code_for_country_code(parsed.country_code)
            return number, national_number,international_number,dialCode,country_code;
        except Exception as e:
            return number, None, None, None, country_code;
    
    def to_json(self, _fields=None):
       if getattr(self, 'number', None) is None:
           return None;
       return {
           "number": self.number,
           "national_number": self.national_number,
           "international_number": self.international_number,
           "dialCode": self.dialCode,
           "country_code": self.country_code
       }

    def is_possible(self):
        try:
            return phonenumbers.is_possible_number(self.parsed)
        except:
            return False;
    
    def is_valid(self):
        try:
            return phonenumbers.is_valid_number(self.parsed)
        except:
            return False;

    def is_valid_for_region(self, region: str = None):
        country_code = region;
        if region is None:
            region = self.country_code;
        
        country_code = str(country_code).upper()
        try:
            return phonenumbers.is_valid_number_for_region(phonenumbers.parse(self.number, country_code), country_code)
        except:
            return False;