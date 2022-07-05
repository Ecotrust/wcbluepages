from django.contrib import admin
from django.db.models import Value
from django.db.models.functions import Concat
from address.models import Address, Country, State, City
from reversion.admin import VersionAdmin

class CountryAdmin(VersionAdmin):
    list_display = ('name', 'postal_code')

class StateAdmin(VersionAdmin):
    list_display = ('name', 'postal_code', 'country')

class CityAdmin(VersionAdmin):
    list_display = ('name', 'state')

class AddressAdmin(VersionAdmin):
    search_fields = ['line_1', 'line_2', 'city_search', 'zip_code']
    list_display = ('line_1', 'line_2', 'city', 'state', 'zip_code', 'country')

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