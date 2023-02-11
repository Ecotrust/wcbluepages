from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.gis.db.models import GeometryField
from django.urls import reverse

from phone_field import PhoneField

from django.contrib.auth.models import User
User._meta.get_field('email')._unique = True

PUBLIC_CHOICES = [
    (None, 'Default'),
    (True, 'Public'),
    (False, 'Filtered'),
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

    def to_dict(self, include_geometry=False, format='json'):
        out_dict = {
            'id': self.pk,
            'region_id': self.id,
            'name': self.name,
            'depth_type': self.depth_type,
            'region_number': self.id_num,
            'states ': [state.postal_code for state in self.states.all()],
        }
        if include_geometry and hasattr(self.geometry, format):
            out_dict['geometry'] = getattr(self.geometry, format)

        return out_dict

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
        "Filtered: Contacts only disoverable via region/topic search.<br />" +
        "Default: Do whatever the parent entity does."
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

    def allow_show_contacts(self):
        if not self.show_contacts == None:
            # explicitly set
            return self.show_contacts
        else:
            # do what may parent (or nearest non-wishy-washy ancestor) does
            if not self.parent == None:
                return parent.allow_show_contacts()
        # default to transparency
        return True

    def to_dict(self, include_contacts=False, flat=False):
        
        out_dict = {
            'id': self.pk,
            'name': str(self),
            'entity_type': self.entity_type,
            'website': self.website,
            'address': str(self.address),
            'email': self.email,
            'phone': str(self.phone),
            'fax': str(self.fax),
            'show_contacts': self.allow_show_contacts(),
            'notes': self.notes
        }

        if include_contacts and self.allow_show_contacts() and not flat:
            out_dict['contacts'] = [contact.to_dict(include_records=False) for contact in self.contacts_set.all()]

        if flat or self.parent == self:
            out_dict['parent'] = str(self.parent)
        else:
            out_dict['parent'] = self.parent.to_dict(include_contacts=False, flat=flat) if self.parent else None

        return out_dict


# Topic
class Topic(models.Model):
    name = models.CharField(
        max_length=254, 
        verbose_name='Name of Topic'
    )
    notes = models.TextField(null=True, blank=True, default=None)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['name',], name='unique_topic')
        ]

    def __str__(self):
        return self.name

# Record - ties contact to topic to geographies
class RecordBase(models.Model):
    topic = models.ForeignKey(
        'Topic',
        on_delete=models.CASCADE,
    )
    regions = models.ManyToManyField(Region)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

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
        constraints = [
            models.UniqueConstraint(fields=['topic', 'contact'], name='unique_record')
        ]

    def __str__(self):
        return "{}: {}".format(self.topic, self.contact)

    def to_dict(self, include_contact=False, include_regions=True, include_geometry=False):
        out_dict = {
            'id': self.pk,
            'name': str(self),
            'topic': str(self.topic),
            'date_created': self.date_created.strftime('%m-%d-%Y'),
            'date_modified': self.date_modified.strftime('%m-%d-%Y')
        }

        if include_contact:
            out_dict['contact'] = self.contact.to_dict()
        
        if include_regions:
            out_dict['regions'] = [region.to_dict(include_geometry=include_geometry) for region in self.regions.all()]

        return out_dict

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
        verbose_name='Entity/Organization',
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
        verbose_name='Area(s) of expertise'
    )
    email = models.EmailField(
        max_length=254,
        blank=True, default='',
    )
    phone = PhoneField(blank=True, null=True, default=None, verbose_name="Work/Desk phone no.")
    mobile_phone = PhoneField(blank=True, null=True, default=None, verbose_name="Mobile phone no.")
    office_phone = PhoneField(blank=True, null=True, default=None, verbose_name="Department/General phone no.")
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
        help_text='i.e. email, phone, no preference, etc...'
    )
    show_on_entity_page = models.BooleanField(
        null=True, blank=True, 
        choices=PUBLIC_CHOICES, 
        default=None,
        verbose_name='Contact Visibility',
        help_text="Public: Display contact on the entity page.<br />" +
        "Filtered: Contact only disoverable via region/topic search.<br />" +
        "Default: Do whatever the entity does."
    )
    notes = models.TextField(null=True, blank=True, default=None)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
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

    @property
    def public(self):
        if not self.show_on_entity_page == None:
            return self.show_on_entity_page
        else:
            if self.entity:
                return self.entity.allow_show_contacts()
        return True

class Contact(ContactBase):
    is_test_data = models.BooleanField(
        default=False
    )

    def to_dict(self, include_entity=True, include_records=True, include_regions=True, include_geometry=False, flat=False):
        # Maybe: list of rough region types that their regions fall into (state/depth)
        out_dict = {
            'id': self.pk,
            'full_name': self.full_name,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'post_title': self.post_title,
            'title': self.title,
            'pronouns': self.preferred_pronouns,
            'job_title': self.job_title,
            'expertise': self.expertise,
            'email': self.email,
            'phone': str(self.phone),
            'mobile_phone': str(self.mobile_phone),
            'office_phone': str(self.office_phone),
            'fax': str(self.fax),
            'address': str(self.address),
            'preferred_contact_method': self.preferred_contact_method,
            'show_on_entity_page': self.show_on_entity_page,
            'is_test_data': self.is_test_data,
            'notes': self.notes,
            'date_created': self.date_created.strftime('%m-%d-%Y'),
            'date_modified': self.date_modified.strftime('%m-%d-%Y'),
        }

        if include_entity:
            entity = self.entity.to_dict(include_contacts=False, flat=flat)
            if flat:
                out_dict['entity_name'] = entity['name']
                out_dict['entity_type'] = entity['entity_type']
                out_dict['entity_website'] = entity['website']
                out_dict['entity_address'] = entity['address']
                out_dict['entity_phone'] = entity['phone']
                out_dict['entity_parent'] = entity['parent']

            else:
                out_dict['entity'] = entity

        if include_records:
            records = [record.to_dict(include_regions=include_regions, include_geometry=include_geometry) for record in self.record_set.all().order_by('topic__name')]
            if flat:
                topics = []
                region_ids = []
                for record in records:
                    topics.append(record['topic'])
                    for region in record['regions']:
                        region_ids.append(region['id'])
                topics = list(set(topics))
                out_dict['topics'] = ', '.join(topics)
                regions = [x.name for x in Region.objects.filter(id__in=region_ids).order_by('name')]
                out_dict['regions'] = ', '.join(regions)
            else:
                out_dict['records'] = records

        return out_dict

    def get_absolute_url(self):
        return reverse('contact_detail_html', args=[str(self.id)])

    class Meta:
        ordering = ['last_name', 'first_name', 'middle_name', 'entity', 'job_title']
        abstract = False

class ContactSuggestion(ContactBase):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="User proposing this change")
    contact = models.ForeignKey('Contact', blank=True, null=True, default=None, on_delete=models.SET_NULL, verbose_name="Contact to edit", help_text="If suggesting edits for an existing contact, identify them here.")
    self_suggestion = models.BooleanField(default=False, verbose_name='I am the contact', help_text='this record is my own information about me')
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
    sub_entity_name = models.CharField(max_length=254, blank=True, default='', verbose_name='Division/Sub-entity', help_text='If contact belongs to a specific division within their organization, please specify it here.')
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

    @property
    def contact_address(self):
        if self.contact:
            current_address = self.contact.address
        else:
            current_address = {
                'line_1': '',
                'line_2': '',
                'city': '',
                'state': '',
                'zip_code': '',
                'country': '',
            }
        
        proposed_address = {
            'line_1': self.address_line_1,
            'line_2': self.address_line_2,
            'city': self.address_city,
            'state': self.address_state,
            'zip_code': self.address_zip_code,
            'country': self.address_country,
        }

        address = {
            'current_address': current_address,
            'proposed_address': proposed_address
        }
        
        return address
        
    def clean(self):
        if not self.pk and self.contact and self.status == 'Pending':
            matches = ContactSuggestion.objects.filter(contact=self.contact, user=self.user, status=self.status)
            if matches.count() > 0:
                raise ValidationError('You already have a suggested edit pending for this contact. Please edit your existing suggestion.')

    class Meta:
        ordering = ['last_name', 'first_name', 'middle_name', 'entity', 'job_title', 'user__username']
        constraints = [
            models.UniqueConstraint(fields=['user', 'contact', 'status'], condition=(models.Q(status="Pending") & ~models.Q(contact=None)), name='unique_contact_suggestion'),
        ]

class RecordSuggestion(RecordBase):
    contact_suggestion = models.ForeignKey('ContactSuggestion', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="User proposing this change")
    status = models.CharField(max_length=20, default='Pending', choices=SUGGESTION_STATUS_CHOICES, verbose_name="Suggestion status", help_text="Has suggestion been approved or declined?")

    def clean(self):
        if not self.pk and self.contact_suggestion.status == 'Pending' and self.status == 'Pending':
            matches = RecordSuggestion.objects.filter(contact_suggestion=self.contact_suggestion, topic=self.topic, status=self.status)
            if matches.count() > 0:
                raise ValidationError('You already have a suggested edit pending for this contact for this topic. Please edit your existing suggestion.')

    class Meta:
        ordering = ['topic', 'contact_suggestion']
        constraints = [
            models.UniqueConstraint(fields=['user', 'topic', 'contact_suggestion', 'status'], condition=models.Q(status="Pending"), name='unique_record_suggestion')
        ]

    def __str__(self):
        return "{}: {}".format(self.topic, self.contact_suggestion)
