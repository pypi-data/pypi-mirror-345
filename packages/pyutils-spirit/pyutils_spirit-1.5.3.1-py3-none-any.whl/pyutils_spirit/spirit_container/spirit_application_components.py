from pyutils_spirit.util.cities import get_provinces, get_cities

from pyutils_spirit.spirit_container.annotation import component


@component(signature="cities")
class CitiesComponent:

    def __init__(self, get_cities_func: callable = get_cities, get_provinces_func: callable = get_provinces):
        self.get_cities: callable = get_cities_func
        self.get_provinces: callable = get_provinces_func
