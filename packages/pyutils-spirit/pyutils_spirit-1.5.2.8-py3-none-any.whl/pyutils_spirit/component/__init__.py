from pyutils_spirit.component.components import CitiesComponent

from pyutils_spirit.util.cities import get_provinces, get_cities

CitiesComponent(get_cities_func=get_cities, get_provinces_func=get_provinces)

print("component module initialized")
