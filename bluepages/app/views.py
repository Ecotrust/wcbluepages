from django.http import JsonResponse
from django.shortcuts import render
from app.models import Region
import json
# Create your views here.
def home(request):

    context = {}

    if request.user.is_authenticated:
        return wireframe(request)

    return render(request, "welcome.html", context)


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
