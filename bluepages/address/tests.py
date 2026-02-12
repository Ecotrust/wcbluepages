from django.test import TestCase
from address.models import Address, City, State, Country


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


class StateModelTest(TestCase):
    def create_state(self, name="Oregon", postal_code="OR", country=None):
        if not country:
            country = CountryModelTest.create_country(self)
        return State.objects.create(name=name, postal_code=postal_code, country=country)

    def test_state_creation(self):
        new_state = self.create_state()
        self.assertTrue(isinstance(new_state, State))
        self.assertEqual(str(new_state), new_state.name)


class CityModelTest(TestCase):
    def create_city(self, name="Portland", state=None):
        if state is None:
            state = StateModelTest.create_state(self)
        if not state:  # workaround to test None, but also populate by default
            state = None
        return City.objects.create(name=name, state=state)

    def test_city_creation(self):
        new_city = self.create_city(state=False)
        self.assertTrue(isinstance(new_city, City))
        self.assertEqual(str(new_city), new_city.name)
        new_city = self.create_city()
        self.assertEqual(
            str(new_city), "{}, {}".format(new_city.name, new_city.state.postal_code)
        )


class AddressModelTest(TestCase):
    def create_address(
        self,
        line_1="1140 SE 7th Avenue",
        line_2="Suite 150",
        city=None,
        zip_code="97214",
    ):
        if city is None:
            city = CityModelTest.create_city(self)
        return Address.objects.create(
            line_1=line_1, line_2=line_2, city=city, zip_code=zip_code
        )

    def test_address_creation(self):
        new_address = self.create_address()
        self.assertTrue(isinstance(new_address, Address))
        self.assertEqual(
            str(new_address),
            "{} {} {} {} {}".format(
                new_address.line_1,
                new_address.line_2,
                new_address.city,
                new_address.zip_code,
                new_address.city.state.country.postal_code,
            ),
        )
