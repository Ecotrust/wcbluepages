from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import json

from app.models import Region, Topic, Entity, Contact, Record, RegionState, ContactSuggestion, RecordSuggestion
from app.forms import ContactSuggestionForm, RecordSuggestionForm

def home(request):
    context = {}
    contacts = Contact.objects.all()
    records = Record.objects.all()
    # TODO: getTopic and getRegion should accept filtered records, NOT contacts
    # TODO: Faster smarter queries and facets
    #   https://www.enterprisedb.com/postgres-tutorials/how-implement-faceted-search-django-and-postgresql
    if request.user.is_authenticated or not settings.REQUIRE_ACCOUNT:
        filters = {
            'Entities': getEntityFacetFilters(contacts),
            'Topics': getTopicFacetFilters(contacts),
            'Regions': getRegionFacetFilters(contacts)
        }

        context['filters'] = filters
        context['contacts'] = [
            {
                'id':x.pk, 
                'name': x.full_name,
                'role': x.job_title,
                'entity': x.entity.name, 
                'entity_id': x.entity.pk 
            } for x in contacts.order_by('last_name', 'first_name', 'middle_name', 'title', 'post_title', 'entity__name')
        ]
        return render(request, "home.html", context)

    return render(request, "welcome.html", context)

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
        if entity_dict['count'] > 0:
            entities.append(entity_dict)
    return entities

def getTopicFacetFilters(contacts=None):
    if not contacts:
        contacts = Contact.objects.all()

    topics_dict = {}
    for contact in contacts:
        contact_topics = []
        for record in contact.record_set.all():
            contact_topics.append(record.topic)
        contact_topics = list(set(contact_topics))
        for topic in contact_topics:
            if topic.name not in topics_dict.keys():
                topics_dict[topic.name] = {'name': topic.name, 'id': topic.pk, 'count':0}
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
                if state.name not in contact_regions and record.regions.filter(states=state).count() > 0:
                    contact_regions.append(state.postal_code)
            for depth in depths:
                if depth not in contact_regions and record.regions.filter(depth_type=depth).count() > 0:
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

def getSuggestionMenu(request):
    user_suggestions = [
        {
            'id': contact_suggestion.id,
            'name': str(contact_suggestion),
            'contact_name': contact_suggestion.contact_name,
            'status': contact_suggestion.status,
            'description': contact_suggestion.description,
            'date_created': contact_suggestion.date_created.strftime('%m/%d/%Y %I:%M %p'),
            'date_modified': contact_suggestion.date_modified.strftime('%m/%d/%Y %I:%M %p'),
            'topics': [{'id': x.pk, 'topic': str(x.topic), 'topic_id': x.topic.pk} for x in contact_suggestion.recordsuggestion_set.all()]
        } 
        for contact_suggestion in ContactSuggestion.objects.filter(user=request.user).order_by('status', 'last_name', 'first_name', 'date_modified', 'date_created')
    ]
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
                    'address': contact_suggestion.contact_address,
                    'records': contact_suggestion.recordsuggestion_set.all().order_by('topic'),
                    'description': contact_suggestion.description,
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
