from django.http import JsonResponse
from django.shortcuts import render
from app.models import Region
import json
# Create your views here.
def home(request):

    context = {}

    return render(request, "welcome.html", context)




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
        region_json = json.loads(region.geometry.json)
        region_json['properties'] = {
            'id': region.id,
            'name': region.name,
            'depth': region.depth_type
        }
        geojson['features'].append(region_json)
    
    return JsonResponse(geojson)

def regionPicker(request):
    context = {}

    return render(request, 'region_picker.html', context)