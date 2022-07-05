from django.db import models
from django.contrib.gis.db.models import GeometryField
from address.models import Address, State
from phone_field import PhoneField

PUBLIC_CHOICES = [
    (None, 'Inherit'),
    (True, 'Public'),
    (False, 'Private'),
]

REGION_TYPE_CHOICES = [
    ('N', 'Near Shore'),
    ('M', 'Mid Water'),
    ('O', 'Offshore')
]

# Region
class Region(models.Model):
    objects = models.Manager()
    id = models.CharField(max_length=6, primary_key=True, verbose_name='Region ID')
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

    depth_type = models.CharField(max_length=1, default='N', choices=REGION_TYPE_CHOICES, verbose_name='Region Depth Type')
    id_num = models.CharField(max_length=4, null=True, blank=True, default=None, verbose_name='Region Number')
    states = models.ManyToManyField(State, verbose_name='States')


    class Meta:
        ordering = ['id']

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
    address = models.ForeignKey(
        'address.Address',
        blank=True, null=True, default=None,
        on_delete=models.SET_NULL
    )
    email = models.EmailField(
        max_length=254,
        blank=True, default=None,
    )
    phone = PhoneField(blank=True, null=True, default=None,)
    fax = PhoneField(blank=True, null=True, default=None,)
    show_contacts = models.BooleanField(
        null=True, blank=True, 
        choices=PUBLIC_CHOICES, 
        default=None,
        help_text="Public: Display all known contacts for this entity on the entity page.<br />" +
        "Private: Contacts only disoverable via region/topic search.<br />" +
        "Inherit: Do whatever the parent entity does."
    )
    parent = models.ForeignKey(
        'Entity', 
        blank=True, null=True, default=None,
        on_delete=models.SET_NULL,
    )
    notes = models.TextField(null=True, blank=True, default=None)

    @property
    def ancestor(self):
        ancestor = self.get_root_organization()
        return str(ancestor)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Entities'

    def get_root_organization(self):
        return self.get_hierarchy()[-1].name

    def get_hierarchy(self, current_hierarchy=[]):
        current_hierarchy.append(self)
        # recursively climb entity family tree to get to root, but don't  fall into infinite loop!
        if self.parent and not self.parent == self:
            return self.parent.get_hierarchy(current_hierarchy)
        return current_hierarchy

    @property
    def hierarchy_string(self):
        hierarchy_list = self.get_hierarchy()
        hierarchy_string = " > ".join([x.name for x in hierarchy_list])
        return hierarchy_string

    def __str__(self):
        if self.parent:
            return f"{self.name} ({self.ancestor})"
        return self.name

# Topic
class Topic(models.Model):
    name = models.CharField(
        max_length=254, 
        verbose_name='Name of Topic'
    )
    notes = models.TextField(null=True, blank=True, default=None)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# Record - ties contact to topic to geographies
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

# Contact
class Contact(models.Model):
    title = models.CharField(
        max_length=254, 
        blank=True, default='',
        verbose_name='Title',
        help_text = 'Ms., Sir, Sra., etc...'
    )
    first_name = models.CharField(
        max_length=254, 
        blank=True, default='',
        verbose_name='First/Given Name'
    )
    last_name = models.CharField(
        max_length=254, 
        verbose_name='Last/Family Name'
    )
    middle_name = models.CharField(
        max_length=254, 
        blank=True, default='',
        verbose_name='Middle Name(s)/Initial(s)'
    )
    post_title = models.CharField(
        max_length=254, 
        blank=True, default='',
        verbose_name='Additional Titles',
        help_text = 'Esq., III, Jr., etc...'
    )
    preferred_pronouns = models.CharField(
        max_length=254, 
        blank=True, default='',
        verbose_name='Preferred Pronouns',
        help_text="She/Her, They/Them, etc...",
    )
    entity = models.ForeignKey(
        'Entity',
        null=True, blank=True, default=None,
        on_delete=models.SET_NULL
    )
    show_on_entity_page = models.BooleanField(
        null=True, blank=True, 
        choices=PUBLIC_CHOICES, 
        default=None,
        help_text="Public: Display contact on the entity page.<br />" +
        "Private: Contact only disoverable via region/topic search.<br />" +
        "Inherit: Do whatever the entity does."
    )
    job_title = models.CharField(
        max_length=254, 
        blank=True, default='',
        verbose_name='Job Title/Position'
    )
    expertise = models.CharField(
        max_length=254, 
        blank=True, default='',
        verbose_name='Expertise',
    )
    email = models.EmailField(
        max_length=254,
        blank=True, default='',
    )
    phone = PhoneField(blank=True, null=True, default=None,)
    fax = PhoneField(blank=True, null=True, default=None,)
    address = models.ForeignKey(
        'address.Address',
        blank=True, null=True, default=None,
        on_delete=models.SET_NULL
    )
    preferred_contact_method = models.CharField(
        max_length=254, 
        blank=True, default='',
        verbose_name='Preferred contact method(s)',
    )
    is_test_data = models.BooleanField(
        default=False
    )
    notes = models.TextField(null=True, blank=True, default=None)
    
    class Meta:
        ordering = ['last_name', 'first_name', 'middle_name', 'entity', 'job_title']

    def __str__(self):
        full_name = self.last_name
        if self.first_name and len(self.first_name) > 0:
            full_name = "{}, {}".format(full_name, self.first_name)
            if self.middle_name and len(self.middle_name) > 0:
                full_name = "{} {}".format(full_name, self.middle_name)
        elif self.middle_name and len(self.middle_name) > 0:
            full_name = "{}, {}".format(full_name, self.middle_name)
        if self.title and len(self.title) > 0:
            full_name = "{} {}".format(self.title, full_name)
        if self.post_title and len(self.post_title) > 0:
            full_name = "{} {}".format(full_name, self.post_title)
        
        return full_name


