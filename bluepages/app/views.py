import csv
from datetime import datetime
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect, Http404, FileResponse, HttpResponse
from django.shortcuts import render
from django.views import View
import os
import json
import tempfile

from app.models import Region, Topic, Entity, Contact, Record, RegionState, ContactSuggestion, RecordSuggestion
from app.forms import ContactSuggestionForm, RecordSuggestionForm, UserProfileForm, ContactForm, RecordForm

def home(request):
    context = {}
    if request.user.is_authenticated or not settings.REQUIRE_ACCOUNT:
        return render(request, "home.html", context)

    return render(request, "welcome.html", context)

def filterContactsRequest(request):
    filters = {}
    if request.method == 'POST':
        filters = json.loads(request.POST.get('data'))
    contacts = filterContacts(filters)
    return JsonResponse(contacts)

def exportCSVList(request):
    filters = {}
    if request.method == 'POST':
        filters = json.loads(request.POST.get('data'))
    contacts = filterContacts(filters, format='dict')['contacts']

    try:
        prefix = '{}_bluepages_'.format(datetime.now().strftime("%Y-%m-%d_%H%M%S"))
        csv_file = tempfile.NamedTemporaryFile(prefix=prefix, suffix=".csv", delete=False)


        with open(csv_file.name, 'w') as csv_contents:
            fieldnames = [
                'last_name', 'first_name', 'middle_name', 'post_title', 'title', 'full_name', 'pronouns',
                'job_title', 'expertise', 
                'entity_name', 'entity_type', 'entity_website', 'entity_address', 'entity_phone', 'entity_fax', 'entity_parent',
                'email', 'phone', 'mobile_phone', 'office_phone', 'fax', 'address', 'preferred_contact_method',
                'topics', 'regions',
                'date_created', 'date_modified',
                'notes', 'id', 'entity_id'
            ]
            writer = csv.DictWriter(csv_contents, fieldnames=fieldnames)

            writer.writeheader()
            for contact in contacts.order_by('last_name', 'first_name', 'middle_name', 'post_title', 'entity__name', 'job_title'):
                contact_dict = contact.to_dict(flat=True)
                contact_dict.pop("is_test_data")
                contact_dict.pop("show_on_entity_page")
                writer.writerow(contact_dict)


        response = FileResponse(open(csv_file.name, 'rb'))
        return response

    finally:
        os.remove(csv_file.name)


def stringMatch(targets, match_list):
    for match in match_list:
        match_found = False
        for target in targets:
            if match.lower() in target.lower():
                match_found = True
                break
        if not match_found:
            return False
            
    return True

def filterContacts(filters={}, format='datatable'):
    # TODO: Consider faceted searches and indices
    #   https://www.enterprisedb.com/postgres-tutorials/how-implement-faceted-search-django-and-postgresql
    contacts = Contact.objects.filter(is_test_data=False)
    if ('entities' not in filters.keys() or len(filters['entities']) == 0) and ('topics' not in filters.keys() or len(filters['topics']) == 0) and ('map_regions' not in filters.keys() or len(filters['map_regions']) == 0):
        public_ids = [contact.pk for contact in contacts if contact.public]
        contacts = contacts.filter(pk__in=public_ids)
    if 'entities' in filters.keys() and len(filters['entities']) > 0:
        contacts = contacts.filter(entity__pk__in=filters['entities'])
    if 'topics' in filters.keys() and len(filters['topics']) > 0:
        records = Record.objects.filter(contact__in=contacts, topic__pk__in=filters['topics'])
        contact_ids = list(set([x.contact.pk for x in records]))
        contacts = contacts.filter(pk__in=contact_ids)
    else:
        records = Record.objects.all()
    if 'map_regions' in filters.keys() and len(filters['map_regions']) > 0:
        records = records.filter(regions__pk__in=filters['map_regions'])
        contact_ids = list(set(x.contact.pk for x in records))
        contacts = contacts.filter(pk__in=contact_ids)
    if 'text' in filters.keys() and len(filters['text']) > 0:
        text_ids = [x.pk for x in contacts if stringMatch([x.full_name, x.job_title, x.entity.name], filters['text'])]

        contacts = contacts.filter(pk__in=text_ids)

    # TODO: Faster smarter queries and facets
    filters = {
        'Entities': getEntityFacetFilters(contacts),
        'Topics': getTopicFacetFilters(contacts),
        'Regions': getRegionFacetFilters(contacts)
    }
    
    if format == 'datatable':
        contacts_list = []
        for x in contacts.order_by('last_name', 'first_name', 'middle_name', 'post_title', 'entity__name', 'job_title'):
            if not x.entity:
                entity_name = 'Unspecified'
                entity_id = None
            else:
                entity_name = x.entity.name
                entity_id = x.entity.pk
            contacts_list.append({
                'id':x.pk, 
                'name': x.simple_name,
                'role': x.job_title,
                'entity': entity_name, 
                'entity_id': entity_id 
            })
    else:
        contacts_list = contacts

    return {
        'filters': filters,
        'contacts': contacts_list
    }

def getProfile(request):
    context = {
        'user': request.user
    }
    return render(request, "profile_modal.html", context)

class editProfile(View):
    template_name='generic_form.html' 
    extra_context={}

    def get(self, request):
        profile_form = UserProfileForm(instance=request.user)
        context = {'form': profile_form.as_p()}
        context.update(self.extra_context)
        return render(request, self.template_name, context)

    def post(self, request):
        profile_form = UserProfileForm(request.POST, instance=request.user)
        context = {'form': profile_form.as_p()}
        context.update(self.extra_context)
        if profile_form.is_valid():
            profile_form.save()
            context = {'form': 'Your profile has been updated.', 'hide_submit': True}
        return render(request, self.template_name, context)

class changePassword(View):
    template_name='generic_form.html'
    extra_context={}

    def get(self, request):
        password_form = PasswordChangeForm(user=request.user)
        context = {'form': password_form.as_p()}
        context.update(self.extra_context)
        return render(request, self.template_name, context)

    def post(self, request):
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        context = {'form': password_form.as_p()}
        context.update(self.extra_context)
        if password_form.is_valid():
            password_form.save()
            context['message'] = 'Your password has been updated. You will now be logged out. Please log in again with your new password. <span id="password-reset-success"></span>'
            context['form'] = ''
            context['hide_submit'] = True

        return render(request, self.template_name, context)
        
def getEntityFacetFilters(contacts=None):
    if not contacts:
        contacts = Contact.objects.all()

    entities = []
    for entity in Entity.objects.all().order_by('name'):
        entity_dict = {
            'name': entity.name, 
            'id': entity.pk, 
            'count': contacts.filter(entity=entity).count()
        }
        entities.append(entity_dict)
    return entities

def getTopicFacetFilters(contacts=None):
    if not contacts:
        contacts = Contact.objects.all()

    topics_dict = {}
    for topic in Topic.objects.all().order_by('name'):
        topics_dict[topic.name] = {'name': topic.name, 'id': topic.pk, 'count': 0}
    for contact in contacts:
        contact_topics = []
        for record in contact.record_set.all():
            contact_topics.append(record.topic)
        contact_topics = list(set(contact_topics))
        for topic in contact_topics:
            topics_dict[topic.name]['count'] += 1
    
    topic_names = list(topics_dict.keys())
    topic_names.sort()
    final_topics = []
    for topic_name in topic_names:
        final_topics.append(topics_dict[topic_name])

    return final_topics

def getRegionFacetFilters(contacts=None):
    if not contacts:
        contacts = Contact.objects.all()

    regions_dict = {
        'Washington': {"id": 'WA', 'count': 0},
        'Oregon': {"id": 'OR', 'count': 0},
        'California': {"id": 'CA', 'count': 0},
        'Offshore': {"id": 'O', 'count': 0},
        'Middle-depth': {"id": 'M', 'count': 0},
        'Nearshore': {"id": 'N', 'count': 0},
    }
    washington = RegionState.objects.get(postal_code="WA")
    oregon = RegionState.objects.get(postal_code="OR")
    california = RegionState.objects.get(postal_code="CA")
    states = [washington, oregon, california]
    depths = ["O", "M", "N"]
    for contact in contacts:
        contact_regions = []
        for record in contact.record_set.all():
            if len(contact_regions) == 6:
                break
            for state in states:
                contact_regions.append(state.postal_code)
            for depth in depths:
                contact_regions.append(depth)
        for region_index in regions_dict.keys():
            region = regions_dict[region_index]
            if region['id'] in contact_regions:
                region['count'] += 1

    final_regions = [
        {'name': 'Washington', 'id': 'WA', 'count': regions_dict['Washington']['count']},
        {'name': 'Oregon', 'id': 'OR', 'count': regions_dict['Oregon']['count']},
        {'name': 'California', 'id': 'CA', 'count': regions_dict['California']['count']},
        {'name': 'Offshore', 'id': 'OS', 'count': regions_dict['Offshore']['count']},
        {'name': 'Middle-depth', 'id': 'MD', 'count': regions_dict['Middle-depth']['count']},
        {'name': 'Nearshore', 'id': 'NS', 'count': regions_dict['Nearshore']['count']},
    ]

    return [x for x in final_regions if x['count'] > 0]

def formatSuggestionMenuEntry(contact_suggestion):
    return {
        'id': contact_suggestion.id,
        'name': str(contact_suggestion),
        'contact_name': contact_suggestion.contact_name,
        'status': contact_suggestion.status,
        'description': contact_suggestion.description,
        'date_created': contact_suggestion.date_created.strftime('%m/%d/%Y %I:%M %p'),
        'date_modified': contact_suggestion.date_modified.strftime('%m/%d/%Y %I:%M %p'),
        'topics': [{'id': x.pk, 'topic': str(x.topic), 'topic_id': x.topic.pk, 'status': x.status} for x in contact_suggestion.recordsuggestion_set.all()]
    }

def getSuggestionMenu(request):
    user_suggestions = [
        formatSuggestionMenuEntry(contact_suggestion)
        for contact_suggestion in ContactSuggestion.objects.filter(user=request.user, status='Pending').order_by('last_name', 'first_name', 'date_modified', 'date_created')
    ]
    for contact_suggestion in ContactSuggestion.objects.filter(user=request.user).exclude(status='Pending').order_by('status', 'last_name', 'first_name', 'date_modified', 'date_created'):
        user_suggestions.append(formatSuggestionMenuEntry(contact_suggestion))
    if len(user_suggestions) > 0:
        return render(request, 'suggestion_menu.html', {'suggestions': user_suggestions})
    else:
        return JsonResponse({'has_suggestions': False})

def contactSuggestionMenu(request, contact_id=None):
    if request.method == 'POST':
        pass
    else:
        if contact_id:
            contact_suggestion = ContactSuggestion.objects.get(pk=contact_id)
            context = {
                'contact': {
                    'id': contact_suggestion.pk,
                    'name':  contact_suggestion.contact_name,
                    'job_title': contact_suggestion.job_title,
                    'entity_name': str(contact_suggestion.entity),
                    'email': contact_suggestion.email,
                    'phone': contact_suggestion.phone,
                    'address': contact_suggestion.full_address(),
                    'records': contact_suggestion.recordsuggestion_set.all().order_by('topic'),
                    'description': contact_suggestion.description,
                    'status': contact_suggestion.status
                }
            }
            return render(request, 'contact_suggestion_menu.html', context)
        else:
            pass

def deleteSuggestedContact(request, contact_id=None):
    contact_suggestion_matches = ContactSuggestion.objects.filter(pk=contact_id, user=request.user)
    for match in contact_suggestion_matches:
        match.delete()
    return JsonResponse({
        'status': 200,
        'success': True,
        'message': 'Suggestion deleted.'
    })

def deleteSuggestedRecord(request, record_id=None):
    record_suggestion_matches = RecordSuggestion.objects.filter(pk=record_id, user=request.user)
    for match in record_suggestion_matches:
        match.delete()
    return JsonResponse({
        'status': 200,
        'success': True,
        'message': 'Topic Record deleted.'
    })

def contactSuggestionForm(request, contact_id=None):
    action = '/suggestion_form'
    contact_suggestion_record = False
    if contact_id:
        action = action + "/{}/".format(contact_id)
        contact_suggestion_record_matches = ContactSuggestion.objects.filter(pk=contact_id, user=request.user)
        if len(contact_suggestion_record_matches) == 1:
            contact_suggestion_record = contact_suggestion_record_matches[0]
    if request.method == 'POST':
        if contact_suggestion_record:
            contact_form = ContactSuggestionForm(request.POST, instance=contact_suggestion_record)
        else:
            contact_form = ContactSuggestionForm(request.POST)
        if contact_form.is_valid():
            contact_suggestion = contact_form.save()
            return JsonResponse({'contact_suggestion': {
                'id': contact_suggestion.id,
                'name': str(contact_suggestion),
                'contact_name': contact_suggestion.contact_name,
                'topics': [{'id': x.pk, 'topic': str(x.topic), 'topic_id': x.topic.pk} for x in contact_suggestion.recordsuggestion_set.all()]
                }
            })
    else:
        if contact_suggestion_record:
            contact_form =ContactSuggestionForm(instance=contact_suggestion_record)
        else:
            contact_form = ContactSuggestionForm(initial={'user':request.user, 'status':'Pending'})
    context = {
        'contact_form': contact_form,
        'action': action,
        'contact_id': contact_id
    }
    return render(request, 'suggestion_form.html', context)

def recordSuggestionForm(request, contact_id, record_id=None):
    contact_suggestion = ContactSuggestion.objects.get(pk=contact_id)
    record_suggestion = False
    action = '/record_suggestion_form/{}/'.format(contact_id)
    if record_id:
        record_suggestion_matches = RecordSuggestion.objects.filter(pk=record_id, user=request.user)
        if len(record_suggestion_matches) == 1:
            record_suggestion = record_suggestion_matches[0]
            action += "{}/".format(record_suggestion.pk)
    if request.method == 'POST':
        if record_suggestion:
            record_form = RecordSuggestionForm(request.POST, instance=record_suggestion)
        else:
            record_form = RecordSuggestionForm(request.POST)
        if record_form.is_valid():
            record_form.save()
            return JsonResponse({'contact_suggestion': {
                'id': contact_suggestion.id,
                'name': str(contact_suggestion),
                'contact_name': contact_suggestion.contact_name,
                'topics': [{'id': x.pk, 'topic': str(x.topic), 'topic_id': x.topic.pk} for x in contact_suggestion.recordsuggestion_set.all()]
                }
            })

    else:
        if record_suggestion:
            record_form = RecordSuggestionForm(instance=record_suggestion)
        else:
            record_form = RecordSuggestionForm(initial={'user': request.user, 'status': 'Pending', 'contact_suggestion':contact_suggestion})

    context = {
        'contact_name': contact_suggestion.contact_name,
        'contact_id': contact_suggestion.pk,
        'record_form': record_form,
        'action': action
    }
    return render(request, 'record_suggestion_form.html', context)

def wireframe(request):

    context = {}

    return render(request, "wireframe.html", context)

def contactList(request):
    filters = {}
    if request.method == 'POST':
        filters = json.loads(request.POST.get('data'))
    contacts = filterContacts(filters)['contacts']
    return JsonResponse({'contacts': contacts})

def contactDetail(request, contact_id):
    try:
        contact = Contact.objects.get(pk=contact_id)
        response = contact.to_dict()
    except Exception as e:
        response = {
            'status': 'Error',
            'message': 'Contact with id {} not found'.format(contact_id)
        }
    return JsonResponse(response)
    
def contactDetailHTML(request, contact_id):
    try:
        contact = Contact.objects.get(pk=contact_id)
        json_ld = json.dumps(getContactJsonLd(request, contact, render=True), indent=2)
        form = ContactForm(data=model_to_dict(contact))
    except Exception as e:
        raise Http404("Contact does not exist")
    return render(request, 'contact_detail_page.html', {'contact': contact, 'JSON_LD': json_ld, 'form': form, 'embedded': False})

def contactDetailEmbedded(request, contact_id):
    try:
        contact = Contact.objects.get(pk=contact_id)
        json_ld = json.dumps(getContactJsonLd(request, contact, render=True), indent=2)
        form = ContactForm(data=model_to_dict(contact))
    except Exception as e:
        raise Http404("Contact does not exist")
    return render(request, 'contact_detail_embedded.html', {'contact': contact, 'JSON_LD': json_ld, 'form': form, 'embedded': True})

def getContactJsonLd(request, contact, render=False):
    if type(contact) == int:
        try:
            contact = Contact.objects.get(pk=contact)
        except Exception as e:
            raise Http404("Contact does not exist")
    site = get_current_site(request)

    context = {
        "@vocab": "http://schema.org/",
    }

    doc = {
        "@context": {
            "@vocab": "https://schema.org/"
        },
        "@id": "https://{}/contacts/{}/".format(site, contact.pk),
        "@type": "Person",
        "name": contact.full_name,
        "jobTitle": contact.job_title,
        "telephone": str(contact.phone),
        # "url": contact.url if contact.url else None,
        "knowsAbout": [
            # {
            # "@type": "Text",
            # "description": "Invasive species in brackish water"
            # },
            # {
            # "@type": "URL",
            # "url": "https://www.wikidata.org/wiki/Q183368"
            # },
            # {
            # "@id": "https://example.org/id/course/x",
            # "@type": "Course",
            # "description": "In this course ...",
            # "url": "URL to the course"
            # }
        ],
        # "identifier": {
        #     "@id": "https://{}/contacts/{}/".format(site, contact.pk),
        #     "@type": "PropertyValue",
        #     "propertyID": "https://registry.identifiers.org/registry/orcid",
        #     "url": "https://orcid.org/0000-0002-2257-9127",
        #     "description": "Optional description of this record..."
        # },
        # "nationality": [
        #     {
        #         "@type": "Country",
        #         "name": contact.addresss.country if contact.address else None
        #     },
        #     {
        #         "@type": "DefinedTerm",
        #         "url": "https://unece.org/trade/cefact/unlocode-code-list-country-and-territory",
        #         "inDefinedTermSet": "UN/LOCODE Code List by Country and Territory",
        #         "name": "United States",
        #         "termCode": "US"
        #     } if contact.address and contact.address.country == 'USA' else None
        # ],
        # "knowsLanguage" :{
        #     "@type": "Language",
        #     "name": "Spanish",
        #     "alternateName": "es"
        # }
    }

    if contact.country:
        doc['nationality'] = [
            {
                "@type": "Country",
                "name": contact.country
            },
            {
                "@type": "DefinedTerm",
                "url": "https://unece.org/trade/cefact/unlocode-code-list-country-and-territory",
                "inDefinedTermSet": "UN/LOCODE Code List by Country and Territory",
                "name": "United States",
                "termCode": "US"
            } if contact.country == 'USA' else None
        ]
    for record in contact.record_set.all():
        doc['knowsAbout'].append(
            {
                "@type":"Text",
                "description":str(record.topic)
            },
            # {
            # "@type": "URL",
            # "url": "https://www.wikidata.org/wiki/Q188989"
            # },
        )
    doc['@context'] = context


    # The above is formatted correctly - I'm not sure we need jsonld (RDH 2023-02-07)
    # compacted = jsonld.compact(doc, context)

    if render:
        return doc
    else:
        return JsonResponse(doc)

def entityList(request): 
    filters = {}
    entities = {
        'entities': []
    }
    for entity in Entity.objects.all().order_by('name'):
        entities['entities'].append(entity.to_dict())
    return JsonResponse(entities)
def entityDetail(request, id):
    try:
        entity = Entity.objects.get(pk=id)
        response = entity.to_dict()
    except Exception as e:
        response = {
            'status': 'Error',
            'message': 'Error with id {} not found'.format(id)
        }
    return JsonResponse(response)
def entityDetailHTML(request, id):
    try:
        entity = Entity.objects.get(pk=id)
        json_ld = 'TODO'
    except Exception as e:
        raise Http404("Entity does not exist")
    return render(request, 'entity_detail_html.html', {'entity': entity, 'JSON_LD': json_ld, 'embedded': False})

def entityDetailEmbedded(request, id):
    try:
        entity = Entity.objects.get(pk=id)
        json_ld = 'TODO'
    except Exception as e:
        raise Http404("Entity does not exist")
    return render(request, 'entity_detail_embedded_wrapper.html', {'entity': entity, 'JSON_LD': json_ld, 'embedded': True})

def exploreEntitiesPage(request):
    entityExploreTree = buildExploreEntityTree()
    context = {
        'entities': entityExploreTree,
    }
    return render(request, "explore/entityPageWrapper.html", context)

def exploreEntitiesEmbedded(request):
    entityExploreTree = buildExploreEntityTree()
    context = {
        'entities': entityExploreTree,
    }
    return render(request, "explore/entityEmbeddedWrapper.html", context)

def getEntityChildrenTree(entity):
    children = []
    # if entity.children:
    if entity.children.count() > 0:
        for child in entity.children:
            child_dict = child.to_dict(flat=True)
            child_dict['children'] = getEntityChildrenTree(child)
            children.append(child_dict)
    return children

def buildExploreEntityTree():
    entity_tree = []
    for entity in Entity.objects.all().order_by('name'):
        if entity.is_prime:
            entity_dict = entity.to_dict(flat=True)
            entity_dict['children'] = getEntityChildrenTree(entity)
            entity_tree.append(entity_dict)
    
    return entity_tree


####################################
#   ADMIN VIEWS                    #
####################################

def getSuggestionInitialValues(suggestion):
    initial = {}
    fields = [
        'title',
        'last_name',
        'first_name',
        'middle_name',
        'post_title',
        'pronouns',
        'entity',
        'job_title',
        'expertise',
        'email',
        'phone',
        'mobile_phone',
        'office_phone',
        'fax',
        'line_1',
        'line_2',
        'city',
        'state',
        'country',
        'zip_code',
        'preferred_contact_method',
        'show_on_entity_page',
        'notes'
    ]

    if suggestion.contact:
        # When overriding contact, 'null' values should be ignored
        # This is especially true for 'entity' and 'address' drop-downs
        # This is a gray area for 'show_on_entity_page' - a user-change can't
        # be explicit about wanting to change visibility to 'default' (val=None)
        for field in fields:
            if hasattr(suggestion, field):
                value = getattr(suggestion, field)
                if not value in [None, '']:
                    initial[field] = value
    else:
        for field in fields:
            if hasattr(suggestion, field):
                # Supports values including False and None
                value = getattr(suggestion, field)
            else:
                value = None
            initial[field] = value
    
    return initial

def buildReviewRow(suggestion, contact, contact_form, field, contact_field=None, type='td', hidden=False, row_style=None):
    row = {
        'element': type,
        'field': field,
        'hidden': hidden,
    }
    if not contact_field:
        contact_field = field
    match = False
    overwrite = not getattr(suggestion, field) in [None, '']
    cells = [
        { 'value': getattr(suggestion, field), }
    ]
    try:
        cells.append({ 
            'value':contact_form.fields[contact_field].get_bound_field(contact_form, contact_field),
            'is_field': True,
        }) 
    except (AttributeError, KeyError) as e:
        cells.append({ 
            'value':'----'
        })
    if contact:
        if hasattr(contact, field):
            cells.insert(1, { 
                'value':getattr(contact, field)
            })
        else:
            cells.insert(1, { 
                'value':'----'
            })
        if cells[0]['value'] == cells[1]['value']:
            match = True
            overwrite = False
        else:
            if not row_style and getattr(suggestion, field):
                row_style = 'attention'

    try:
        cells.insert(0, { 
            'value':cells[-1]['value'].label
        })
    except AttributeError as e:
        cells.insert(0, { 
            'value':field
        })
    try:
        cells.append({ 
            'value':cells[-1]['value'].help_text
        })
    except AttributeError as e:
        cells.append({ 
            'value':' '
        })

    row['cells'] = cells
    row['match'] = match
    row['overwrite'] = overwrite
    row['style'] = row_style

    return row

@staff_member_required
def adminSuggestionReviewMenu(request, suggestion_id):
    suggestion = None
    contact = None
    message = 'Contact suggestion matching ID {} not found.'.format(suggestion_id)
    rows = []
    contact_form = None

    try:
        suggestion = ContactSuggestion.objects.get(pk=suggestion_id)
        message = None
        contact = suggestion.contact

        if request.method == 'POST':
            contact_form = ContactForm(request.POST, instance=contact)
            if contact_form.is_valid():
                contact = contact_form.save()
                message = "Contact '{}' updated.".format(suggestion.contact)
                messages.add_message(request, messages.SUCCESS, message, extra_tags='success', fail_silently=False)
                try:
                    suggestion.status = 'Approved'
                    suggestion.contact = contact
                    suggestion.save()
                    message = "Contact Suggestion '{}' approved.".format(suggestion)
                    messages.add_message(request, messages.SUCCESS, message, extra_tags='success', fail_silently=False)


                    for record_suggestion in suggestion.recordsuggestion_set.all():
                        record_approve_name = 'approve-record-suggestion-{}'.format(record_suggestion.pk)
                        if record_approve_name in request.POST.keys() and request.POST[record_approve_name] == 'on':
                            record_suggestion.status = 'Approved'
                        else:
                            record_suggestion.status = 'Declined'
                        try:
                            record_suggestion.save()
                            (record, rec_create_status) = Record.objects.get_or_create(contact=contact, topic=record_suggestion.topic)
                            record.regions.set(record_suggestion.regions.all())
                            record.save()
                            message = "Record Suggestion '{}' {}.".format(record_suggestion, record_suggestion.status)
                            messages.add_message(request, messages.SUCCESS, message, extra_tags='success', fail_silently=False)
                        except Exception as e:
                            message = "Error saving record Suggestion '{}'.".format(suggestion)
                            messages.add_message(request, messages.ERROR, message, extra_tags='error', fail_silently=False)

                except Exception as e:
                    message = "Error updating status of '{}'.".format(suggestion)
                    messages.add_message(request, messages.ERROR, message, extra_tags="error", fail_silently=False)
                return HttpResponseRedirect('/admin/app/contactsuggestion/{}/change/'.format(suggestion_id))

        initial_dict = getSuggestionInitialValues(suggestion)
        contact_form = ContactForm(instance=contact, initial=initial_dict)
        header_cells = [{ 
                'value':'label'
            }, { 
                'value':'Suggestion'
            }, { 
                'value':'Updated Form'
            }, { 
                'value':''
            }]
        if contact:
            header_cells.insert(2, { 
                'value':'Current Record'
            })
        rows.append({
            'element': 'th',
            'cells': header_cells
        })

        # Name
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'title'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'last_name'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'first_name'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'middle_name'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'post_title'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'pronouns'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'entity'))
        # handle entity name, sub_entity!!!
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'other_entity_name'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'sub_entity_name'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'job_title'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'expertise'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'email'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'phone'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'mobile_phone'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'office_phone'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'fax'))
        # Handle addresses!
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'line_1'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'line_2'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'city'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'state'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'country'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'zip_code'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'preferred_contact_method'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'show_on_entity_page'))
        rows.append(buildReviewRow(suggestion, contact, contact_form, 'notes'))

        record_suggestions = []
        contact_topics = {}
        if contact:
            for record in contact.record_set.all():
                contact_topics[str(record.topic.id)] = record

        for record_suggestion in suggestion.recordsuggestion_set.all().order_by('topic'):
            overwrite = str(record_suggestion.topic.id) in contact_topics.keys()
            added_regions = []
            removed_regions = []
            shared_regions = []
            if overwrite:
                contact_record = contact_topics[str(record_suggestion.topic.id)]
                for region in record_suggestion.regions.all():
                    if region not in contact_record.regions.all():
                        added_regions.append(region)
                    else:
                        shared_regions.append(region)
                for region in contact_record.regions.all():
                    if region not in record_suggestion.regions.all():
                        removed_regions.append(region)
            else:
                added_regions = [x for x in record_suggestion.regions.all()]


            record_suggestions.append({
                'record': record_suggestion,
                'overwrite': overwrite,
                'added_regions': added_regions,
                'removed_regions': removed_regions,
                'shared_regions': shared_regions,
            })

    except Exception as e:
        print(e)
        pass

    context = {
        'message': message,
        'suggestion': suggestion,
        'contact': contact,
        'contact_form': contact_form,
        'table': {'rows': rows},
        'record_suggestions': record_suggestions, 
        'contact_topics': contact_topics
    }
    return render(request, 'admin/app/contactsuggestion/review_form.html', context)

@staff_member_required
def adminSuggestionRejection(request, suggestion_id):
    message = "An error occurred. Please try again."
    try:
        suggestion = ContactSuggestion.objects.get(pk=suggestion_id)
        try:
            suggestion.status = "Declined"
            suggestion.save()
            message = "Contact suggestion '{}' successfully declined.".format(str(suggestion))
            messages.add_message(request, messages.SUCCESS, message, extra_tags='success', fail_silently=False)
            return HttpResponseRedirect('/admin/app/contactsuggestion/')
        except Exception as e:
            message = "An error occurred attempting to save rejection for suggestion {}".format(suggestion)
    except Exception as e:
        message = "An error occurred: Unable to identify a Contact Suggestion with given id '{}'.".format(suggestion_id)
    # return render(request, 'admin/app/error_page.html', {'message': message})
    messages.add_message(request, messages.ERROR, message, extra_tags='error', fail_silently=False)
    return HttpResponseRedirect('/admin/app/contactsuggestion/'.format(suggestion_id), {'messages': [{'tags': 'error', 'message': message}]})

####################################
#   REGION PICKER                  #
####################################

def regionJSON(request):
    regions = Region.objects.all();
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    for region in regions:
        geometry = json.loads(region.geometry.json)
        properties = {
            'id': region.id,
            'name': region.name,
            'depth': region.depth_type,
            'states': ','.join([f'{x.postal_code}' for x in region.states.all().order_by('postal_code')])
        }
        region_json = {
            'type': 'Feature',
            'geometry': geometry,
            'properties': properties
        }
        geojson['features'].append(region_json)
    
    return JsonResponse(geojson)

def regionPicker(request):
    context = {}

    return render(request, 'region_picker.html', context)
