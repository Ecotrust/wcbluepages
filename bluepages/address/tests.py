from django.test import TestCase
from address.models import Address, Country


class CountryModelTest(TestCase):
    def create_country(
        self,
        name="United States of America",
        postal_code="USA",
    ):
        return Country.objects.create(name=name, postal_code=postal_code)

    def test_county_creation(self):
        new_country = self.create_country()
        self.assertTrue(isinstance(new_country, Country))
        self.assertEqual(str(new_country), new_country.name)


class AddressModelTest(TestCase):
    def create_address(
        self,
        line_1="1140 SE 7th Avenue",
        line_2="Suite 150",
        city="Portland",
        zip_code="97214",
    ):
        return Address.objects.create(
            line_1=line_1, line_2=line_2, city=city, zip_code=zip_code
        )

    def test_address_creation(self):
        new_address = self.create_address()
        self.assertTrue(isinstance(new_address, Address))
        self.assertEqual(
            str(new_address),
            "{} {} {} {}".format(
                new_address.line_1,
                new_address.line_2,
                new_address.city,
                new_address.zip_code,
            ),
        )
