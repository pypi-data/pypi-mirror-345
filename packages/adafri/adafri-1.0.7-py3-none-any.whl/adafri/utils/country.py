import pycountry
import gettext

class Country(object):
    def __init__(self, locales=['fr']):
        self.locales = locales;
    
    def get_countries(self):
        lang =  gettext.translation('iso3166-1', pycountry.LOCALES_DIR, languages=self.locales);
        lang.install()
        countries_list = list(pycountry.countries)
        countries = []
        for c in countries_list:
            country = self.get_country(country=c)
            countries.append(country)
        return countries;
    
    def get_country(self, country=None, country_code=None):
        c = country;
        data_country = None;
        if country is None:
            if country_code is None:
                return data_country;
        
            c = pycountry.countries.lookup(country_code);
        
        if c is not None:
            name = getattr(c, 'name', '')
            data_country = {
                "name": _(name),
                "official_name": _(getattr(c, 'official_name', name)),
                "numeric": getattr(c, 'numeric', ''),
                "alpha_2": getattr(c, 'alpha_2', None),
                "alpha_3": getattr(c, 'alpha_3', None),
                'flag': getattr(c, 'flag', None),
            }
        return data_country