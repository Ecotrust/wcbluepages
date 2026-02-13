from django.db import models


# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=254)
    postal_code = models.CharField(max_length=254, help_text="i.e. 'USA'")

    class Meta:
        ordering = [
            "name",
        ]
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class Address(models.Model):
    line_1 = models.CharField(max_length=254)
    line_2 = models.CharField(max_length=254, blank=True, default=None)
    city = models.CharField(max_length=150, blank=True, null=True, default=None)
    state = models.CharField(
        max_length=150,
        verbose_name="State/Province",
        blank=True,
        null=True,
        default=None,
    )
    country = models.CharField(max_length=150, blank=True, null=True, default=None)
    zip_code = models.CharField(max_length=25, verbose_name="Zip/Postal Code")

    class Meta:
        ordering = ["city", "zip_code", "line_1", "line_2"]
        verbose_name_plural = "Addresses"

    def __str__(self):
        full_address = self.line_1
        if self.line_2:
            full_address = "{} {}".format(full_address, self.line_2)
        if self.city:
            full_address = "{} {}".format(full_address, self.city)
        if self.state:
            full_address = "{}, {}".format(full_address, self.state)
        full_address = "{} {}".format(full_address, self.zip_code)
        if self.city and self.state and self.country:
            full_address = "{} {}".format(full_address, self.country)

        return full_address
