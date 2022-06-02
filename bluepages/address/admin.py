from django.contrib import admin
from address.models import Address, Country, State, City

# Register your models here.
admin.site.register(Address)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)