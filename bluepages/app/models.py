from django.db import models
from django.contrib.gis.db.models import GeometryField
from address.models import AddressField
from phone_field import PhoneField

# Region
class Region(models.Model):
    objects = models.Manager()
    name = models.CharField(
        max_length=254, 
        blank=True, null=True, default=None,
        verbose_name='Name of Region'
    )
    geometry = GeometryField(
        srid=3857,
        null=True, blank=True,
        verbose_name="Region Boundary",
        default=None
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# Entity
class Entity(models.Model):
    name = models.CharField(
        max_length=254, 
        verbose_name='Name of Entity'
    )
    website = models.URLField(
        max_length=200,
        blank=True, default=None,
    )
    address = AddressField(blank=True, default=None)
    email = models.EmailField(
        max_length=254,
        blank=True, default=None,
    )
    phone = PhoneField(blank=True, null=True, default=None,)
    parent = models.ForeignKey(
        'Entity', 
        blank=True, null=True, default=None,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return "{} ({})".format(self.name, str(self.parent))
        return self.name

# Topic
class Topic(models.Model):
    name = models.CharField(
        max_length=254, 
        verbose_name='Name of Topic'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# Contact
class Contact(models.Model):
    title = models.CharField(
        max_length=254, 
        blank=True, 
        verbose_name='Title',
        help_text = 'Ms., Sir, Sra., etc...'
    )
    first_name = models.CharField(
        max_length=254, 
        blank=True, 
        verbose_name='First/Given Name'
    )
    last_name = models.CharField(
        max_length=254, 
        verbose_name='Last/Family Name'
    )
    middle_name = models.CharField(
        max_length=254, 
        blank=True, 
        verbose_name='Middle Name(s)/Initial(s)'
    )
    post_title = models.CharField(
        max_length=254, 
        blank=True, 
        verbose_name='Additional Titles',
        help_text = 'Esq., III, Jr., etc...'
    )
    preferred_pronouns = models.CharField(
        max_length=254, 
        blank=True, 
        verbose_name='Preferred Pronouns',
        help_text="She/Her, They/Them, etc...",
    )
    entity = models.ForeignKey(
        'Entity',
        null=True, blank=True, default=None,
        on_delete=models.SET_NULL
    )
    job_title = models.CharField(
        max_length=254, 
        blank=True, 
        verbose_name='Job Title/Position'
    )
    expertise = models.CharField(
        max_length=254, 
        blank=True, 
        verbose_name='Expertise',
    )
    email = models.EmailField(
        max_length=254,
        blank=True, default=None,
    )
    phone = PhoneField(blank=True, null=True, default=None,)
    address = AddressField(blank=True, default=None)

    class Meta:
        ordering = ['last_name', 'first_name', 'middle_name', 'entity', 'job_title']

    def __str__(self):
        full_name = self.last_name
        if self.first_name:
            full_name = "{}, {}".format(full_name, self.first_name)
            if self.middle_name:
                full_name = "{} {}".format(full_name, self.middle_name)
        elif self.middle_name:
            full_name = "{}, {}".format(full_name, self.middle_name)
        if self.title:
            full_name = "{} {}".format(self.title, full_name)
        if self.post_title:
            full_name = "{} {}".format(full_name, self.post_title)
        
        return full_name


# Record (M2M support - ties contact to topic to geographies)
class Record(models.Model):
    contact = models.ForeignKey(
        'Contact',
        on_delete=models.CASCADE,
    )
    topic = models.ForeignKey(
        'Topic',
        on_delete=models.CASCADE,
    )
    regions = models.ManyToManyField(Region)

    class Meta:
        ordering = ['topic', 'contact']

    def __str__(self):
        return "{}: {}".format(self.topic, self.contact)