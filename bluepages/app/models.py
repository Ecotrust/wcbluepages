from django.db import models
from django.contrib.gis.db.models import GeometryField
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

ENTITY_TYPE_CHOICES = [
    (None, 'Unspecified'),
    ('Tribal', 'Tribal'),
    ('Federal', 'Federal'),
    ('State', 'State'),
]

SUGGESTION_STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Declined', 'Declined'),
]

# Region
class RegionState(models.Model):
    name = models.CharField(max_length=254)
    postal_code = models.CharField(max_length=4, help_text="i.e. 'WA'")
    country = models.ForeignKey(
        'address.Country',
        null=True, blank=True, default=None,
        on_delete = models.SET_NULL
    )

    class Meta:
        ordering = ['name', 'country']

    def __str__(self):
        return self.name

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
    states = models.ManyToManyField(RegionState, verbose_name='States')


    class Meta:
        ordering = ['id']

    def __str__(self):
        states = ','.join([f'st:{x.postal_code}' for x in self.states.all().order_by('postal_code')])
        verbose_name = f'{self.id} | {states} | {self.name} | depth:{self.depth_type}'
        return verbose_name

# Entity
class Entity(models.Model):
    name = models.CharField(
        max_length=254, 
        verbose_name='Name of Entity'
    )
    entity_type = models.CharField(
        null=True, blank=True,
        max_length=15,
        choices=ENTITY_TYPE_CHOICES,
        default=None,
        verbose_name='Type of Entity'
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
class RecordBase(models.Model):
    topic = models.ForeignKey(
        'Topic',
        on_delete=models.CASCADE,
    )
    regions = models.ManyToManyField(Region)

    class Meta:
        abstract = True

class Record(RecordBase):
    contact = models.ForeignKey(
        'Contact',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['topic', 'contact']
        abstract = False

    def __str__(self):
        return "{}: {}".format(self.topic, self.contact)

# Contact
class ContactBase(models.Model):
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
    preferred_contact_method = models.CharField(
        max_length=254, 
        blank=True, default='',
        verbose_name='Preferred contact method(s)',
    )
    notes = models.TextField(null=True, blank=True, default=None)
    
    class Meta:
        ordering = ['last_name', 'first_name', 'middle_name', 'entity', 'job_title']
        abstract = True

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

    @property 
    def full_name(self):
        return str(self)

class Contact(ContactBase):
    address = models.ForeignKey(
        'address.Address',
        blank=True, null=True, default=None,
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
    is_test_data = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ['last_name', 'first_name', 'middle_name', 'entity', 'job_title']
        abstract = False

class ContactSuggestion(ContactBase):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="User proposing this change")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    contact = models.ForeignKey('Contact', blank=True, null=True, default=None, on_delete=models.SET_NULL, verbose_name="Contact to edit", help_text="If suggesting edits for an existing contact, identify them here.")
    last_name = models.CharField(
        max_length=254, 
        blank=True, default='',
        verbose_name='Last/Family Name'
    )
    address_line_1 = models.CharField(max_length=254, blank=True, null=True, default=None)
    address_line_2 = models.CharField(max_length=254, blank=True, null=True, default=None)
    address_city = models.CharField(max_length=150, blank=True, null=True, default=None)
    address_state = models.CharField(max_length=150, verbose_name='State/Province', blank=True, null=True, default=None)
    address_country = models.CharField(max_length=150, blank=True, null=True, default=None)
    address_zip_code = models.CharField(max_length=25, blank=True, null=True, default=None, verbose_name='Zip/Postal Code')
    other_entity_name = models.CharField(max_length=254, blank=True, default='', verbose_name='Other Entity Name', help_text = 'If contact belongs to an unlisted entity, name it here.')
    status = models.CharField(max_length=20, default='Pending', choices=SUGGESTION_STATUS_CHOICES, verbose_name="Suggestion status", help_text="Has suggestion been approved or declined?")
    description = models.TextField(null=True, blank=True, default=None, verbose_name="Describe the proposed update", help_text="If you are updating an existing contact, what specific changes are you trying to propose in this form?")


    def __str__(self):
        if self.contact:
            contact_name= str(self.contact)
        else:
            contact_name = super().__str__()
        return "{}: {}".format(str(self.user), contact_name)

    @property
    def contact_name(self):
        if self.contact:
            return str(self.contact)
        else:
            return 'new ({})'.format(super().__str__())

    class Meta:
        ordering = ['last_name', 'first_name', 'middle_name', 'entity', 'job_title', 'user__username']

class RecordSuggestion(RecordBase):
    contact_suggestion = models.ForeignKey('ContactSuggestion', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="User proposing this change")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='Pending', choices=SUGGESTION_STATUS_CHOICES, verbose_name="Suggestion status", help_text="Has suggestion been approved or declined?")

    class Meta:
        ordering = ['topic', 'contact_suggestion']

    def __str__(self):
        return "{}: {}".format(self.topic, self.contact_suggestion)
