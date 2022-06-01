from django.test import TestCase
from app.models import *
# from django.utils import timezone
from django.core.urlresolvers import reverse

# Models Tests

## Geography
class GeographyModelTest(TestCase):
    def create_geography(self):
        return True;
    # def create_geography(self, title="only a test", body="yes, this is only a test"):
    #     return Geography.objects.create()

    def test_geography_creation(self):
        new_geography = self.create_geography()
        self.assertTrue(isinstance(new_geography, Geography))
        self.assertEqual(new_geography.__unicode__(), new_geography.title())

## Entity

## Topic

## Contact

## Record