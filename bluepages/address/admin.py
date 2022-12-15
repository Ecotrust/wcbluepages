from django.contrib import admin
from django.db.models import Value
from django.db.models.functions import Concat
from address.models import Address, Country
from reversion.admin import VersionAdmin

class CountryAdmin(VersionAdmin):
    list_display = ('name', 'postal_code')

class AddressAdmin(VersionAdmin):
    search_fields = ['line_1', 'line_2', 'city_search', 'zip_code']
    list_display = ('line_1', 'line_2', 'city', 'state', 'zip_code', 'country')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.alias(
            city_search=Concat(
                "city", Value(" "),
                "state", Value(" "),
                "country", Value(" "),
            )
        )
        return qs

admin.site.register(Country, CountryAdmin)
admin.site.register(Address, AddressAdmin)