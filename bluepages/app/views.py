from django.http import JsonResponse
from django.shortcuts import render
from app.models import Region, Topic, Entity, Contact, Record, State, ContactSuggestion
from app.forms import ContactSuggestionForm
from django.forms import modelformset_factory
import json
from django.conf import settings

def home(request):
    context = {}
    contacts = Contact.objects.all()
    records = Record.objects.all()
    # TODO: getTopic and getRegion should accept filtered records, NOT contacts
    # TODO: Faster smarter queries and facets
    #   https://www.enterprisedb.com/postgres-tutorials/how-implement-faceted-search-django-and-postgresql
    if request.user.is_authenticated or not settings.REQUIRE_ACCOUNT:
        filters = {
            'Entities': getEntityFeacetFilters(contacts),
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

def getEntityFeacetFilters(contacts=None):
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
    washington = State.objects.get(postal_code="WA")
    oregon = State.objects.get(postal_code="OR")
    california = State.objects.get(postal_code="CA")
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
        
def suggestionForm(request):
    # use formset illustration below to add a'record' formset so users can add up to three record suggestions at once.
    # ContactSuggestionFormSet = modelformset_factory(ContactSuggestion, form=ContactSuggestionForm)
    if request.method == 'POST':
        # formset = ContactSuggestionFormSet(request,POST)
        form = ContactSuggestionForm(request,POST)
        if form.is_valid():
            form.save()
    else:
        # formset = ContactSuggestionFormSet()
        form = ContactSuggestionForm()
    context = {'form': form.as_p}
    return render(request, 'generic_form.html', context)



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
