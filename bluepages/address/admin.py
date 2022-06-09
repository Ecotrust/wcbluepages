from django.contrib import admin
from django.db.models import Value
from django.db.models.functions import Concat
from address.models import Address, Country, State, City
from reversion.admin import VersionAdmin

class CountryAdmin(VersionAdmin):
    pass
class StateAdmin(VersionAdmin):
    pass
class CityAdmin(VersionAdmin):
    pass
class AddressAdmin(VersionAdmin):
    search_fields = ['line_1', 'line_2', 'city_search', 'zip_code']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.alias(
            city_search=Concat(
                "city__name", Value(" "),
                "city__state__name", Value(" "),
                "city__state__postal_code", Value(" "),
            )
        )
        return qs

admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Address, AddressAdmin)