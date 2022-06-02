from django.test import TestCase
from app.models import Region, Entity, Topic, Contact, Record

# Models Tests

## Geography
class RegionModelTest(TestCase):
    def create_region(
        self,
        name="Oregon Coast",
        geometry_json = (
            (-13604160.378157955, 5707298.111959826),
            (-13634735.189472025, 5136160.636612991),
            (-14637589.000573538, 5121484.7271822365),
            (-14629028.053405602, 5853241.877965657),
            (-13804731.140378261, 5818998.089293898),
            (-13692215.83474248, 5821444.074199024),
            (-13665310.0007861, 5750510.51195038),
            (-13650634.091355344, 5721158.693088872),
            (-13604160.378157955, 5707298.111959826)
        )
    ):
        from django.contrib.gis.geos import Polygon
        geom = Polygon(geometry_json)

        return Region.objects.create(name=name, geometry=geom)

    def test_region_creation(self):
        new_region = self.create_region()
        self.assertTrue(isinstance(new_region, Region))
        self.assertEqual(str(new_region), new_region.name)

## Entity
class EntityModelTest(TestCase):
    def create_entity(
        self,
        name = 'Ecotrust',
        website = 'https://www.ecotrust.org',
        address = None,
        email = 'ksdev@ecotrust.org',
        phone = '+1.503.227.6225',
        fax = '+1.503.222.1517',
        parent = None,
    ):
        return Entity.objects.create(
            name=name,
            website=website,
            address=address,
            email=email,
            phone=phone,
            fax=fax,
            parent=parent
        )

    def test_entity_creation(self):
        new_entity = self.create_entity()
        self.assertTrue(isinstance(new_entity, Entity))
        self.assertEqual(str(new_entity), new_entity.name)
        # Test against self-referential infinite loops:
        new_entity.parent = new_entity
        self.assertEqual(str(new_entity), '{} ({})'.format(new_entity.name, new_entity.get_root_organization()))
        parent_entity = self.create_entity(name='Ecotrust Prime')
        new_entity.parent = parent_entity
        self.assertEqual(str(new_entity), '{} ({})'.format(new_entity.name, new_entity.get_root_organization()))



## Topic
class TopicModelTest(TestCase):
    def create_topic(
        self,
        name="Aquaculture",
    ):
        return Topic.objects.create(name=name)

    def test_topic_creation(self):
        new_topic = self.create_topic()
        self.assertTrue(isinstance(new_topic, Topic))
        self.assertEqual(str(new_topic), new_topic.name)

## Contact
class ContactModelTest(TestCase):
    def create_contact(
        self,
        last_name="Contact",
        first_name='',
        middle_name='',
        title='',
        post_title='',
        preferred_pronouns='',
        entity=None,
        job_title='Software Tester',
        expertise='',
        email='',
        phone='',
        fax='',
        address=None,
    ):
        return Contact.objects.create(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            title=title,
            post_title=post_title,
            preferred_pronouns=preferred_pronouns,
            entity=entity,
            job_title=job_title,
            expertise=expertise,
            email=email,
            phone=phone,
            fax=fax,
            address=address,
        )

    def test_contact_creation(self):
        new_contact = self.create_contact()
        self.assertTrue(isinstance(new_contact, Contact))
        self.assertEqual(str(new_contact), new_contact.last_name)
        new_contact.middle_name = 'R.'
        self.assertEqual(str(new_contact), "{}, {}".format(new_contact.last_name, new_contact.middle_name))
        new_contact.first_name = "Lucky"
        self.assertEqual(str(new_contact), "{}, {} {}".format(new_contact.last_name, new_contact.first_name, new_contact.middle_name))
        new_contact.middle_name = ''
        self.assertEqual(str(new_contact), "{}, {}".format(new_contact.last_name, new_contact.first_name))
        new_contact.title = 'Xs.'
        self.assertEqual(str(new_contact), "{} {}, {}".format(new_contact.title, new_contact.last_name, new_contact.first_name))
        new_contact.post_title = 'Esq.'
        self.assertEqual(str(new_contact), "{} {}, {} {}".format(new_contact.title, new_contact.last_name, new_contact.first_name, new_contact.post_title))


## Record
class RecordModelTest(TestCase):
    def create_record(
        self,
        contact=None,
        topic=None,
        regions=[]
    ):
        new_record = Record.objects.create(contact=contact, topic=topic)
        for region in regions:
            new_record.regions.add(region)
        new_record.save()
        return new_record

    def test_record_creation(self):
        # from ContactModelTest import create_contact
        contact = ContactModelTest.create_contact(self)
        topic = TopicModelTest.create_topic(self)
        region = RegionModelTest.create_region(self)
        new_record = self.create_record(
            contact=contact,
            topic=topic,
            regions=[region,]
        )
        self.assertTrue(isinstance(new_record, Record))
        self.assertEqual(str(new_record), "{}: {}".format(new_record.topic, new_record.contact))
        self.assertEqual(len(new_record.regions.all()), 1)