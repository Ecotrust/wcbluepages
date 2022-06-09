from django.db import models

# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=254)
    postal_code = models.CharField(max_length=254, help_text="i.e. 'USA'")

    class Meta:
        ordering = ['name',]
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=254)
    postal_code = models.CharField(max_length=4, help_text="i.e. 'WA'")
    country = models.ForeignKey(
        'Country',
        null=True, blank=True, default=None,
        on_delete = models.SET_NULL
    )

    class Meta:
        ordering = ['name', 'country']

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=254)
    state = models.ForeignKey(
        'State',
        blank=True, null=True, default=None,
        on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ['name', 'state']
        verbose_name_plural = 'Cities'

    def __str__(self):
        if self.state:
            return "{}, {}".format(self.name, self.state.postal_code)
        else:
            return self.name

class Address(models.Model):
    line_1 = models.CharField(max_length=254)
    line_2 = models.CharField(max_length=254, blank=True, default=None)
    city = models.ForeignKey(
        'City',
        null=True, blank=True, default=None,
        on_delete=models.SET_NULL
    )
    zip_code = models.CharField(max_length=254)

    class Meta:
        ordering = ['city', 'zip_code', 'line_1', 'line_2']
        verbose_name_plural = 'Addresses'

    def __str__(self):
        full_address = self.line_1
        if self.line_2:
            full_address = "{} {}".format(full_address, self.line_2)
        if self.city:
            full_address = "{} {}".format(full_address, self.city)
        full_address = "{} {}".format(full_address, self.zip_code)
        if self.city and self.city.state and self.city.state.country:
            full_address = "{} {}".format(full_address, self.city.state.country.postal_code)
        
        return full_address