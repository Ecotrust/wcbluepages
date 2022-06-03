from django.contrib import admin
from address.models import Address, Country, State, City
from reversion.admin import VersionAdmin

class CountryAdmin(VersionAdmin):
    pass
class StateAdmin(VersionAdmin):
    pass
class CityAdmin(VersionAdmin):
    pass
class AddressAdmin(VersionAdmin):
    pass

admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Address, AddressAdmin)