from pyutils_spirit.spirit_container.annotation import component

from pyutils_spirit.util.cities import get_provinces, get_cities


@component(signature="cities")
class CitiesComponent:

    def __init__(self):
        self.get_cities: callable = get_cities
        self.get_provinces: callable = get_provinces


print("Cities Component Initialized")
