from django.test import TestCase
from app.models import Region
# from django.utils import timezone
from django.core.urlresolvers import reverse

# Models Tests

## Geography
class RegionModelTest(TestCase):
    def create_region(self, name="Test Region Name"):
        return region.objects.create(name=name)

    def test_region_creation(self):
        new_region = self.create_geography()
        self.assertTrue(isinstance(new_region, Region))
        self.assertEqual(new_region.__unicode__(), new_region.title())

## Entity

## Topic

## Contact

## Record