import Map from 'ol/Map';
import OSM from 'ol/source/OSM';
import VectorSource from 'ol/source/Vector';
import VectorLayer from 'ol/layer/Vector';
import TileLayer from 'ol/layer/Tile';
import View from 'ol/View';
import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';
import Text from 'ol/style/Text';
import GeoJSON from 'ol/format/GeoJSON';

var $ = require( "jquery" );

app.getRecordMapLabel = function(feature) {
    let text = feature.get('name');
    return text;
}

app.recordMapStyleFunction = function(feature) {
    var label = getRecordMapLabel(feature);
    return new Style({
        stroke: new Stroke({
            color: 'rgba(0,55,255,1.0)',
            width: 1,
        }),
        fill: new Fill({
            color: 'rgba(0, 155, 255, 0.3)',
        }),
        text: new Text({
            text: label,
            stroke: new Stroke({
                color: 'white',
                width: 1
            }),
            font: 'bold 12px sans-serif'
        })
    });
}

app.recordMapRegionSource = new VectorSource({
    features: []
});

app.recordMapVectorLayer = new VectorLayer({
    source: app.recordMapRegionSource,
    style: app.recordMapStyleFunction,
});

// Selection logic largely taken from OL examples:
//  https://openlayers.org/en/latest/examples/select-features.html
//  https://openlayers.org/en/latest/examples/select-multiple-features.html

app.recordMapSelected = [];

app.recordMapSelectedStyleFunction = function(feature) {
    var label = getLabel(feature);
    let selectedStyle = new Style({
        fill: new Fill({
            color: 'rgba(255,255,255,0.1)'
        }),
        stroke: new Stroke({
            color: 'rgba(255,0,255,1.0)',
            width: 2,
        }),
        text: new Text({
            text: label,
            stroke: new Stroke({
                color: 'white',
                width: 1
            }),
            font: 'bold 12px sans-serif'
        })
    })
    return selectedStyle;
}

app.recordMapToggleFeatureSelection = function(feature)  {
    const selIndex = app.recordMapSelected.indexOf(feature);
    if (selIndex < 0) {
        app.recordMapSelected.push(feature);
        feature.setStyle(app.recordMapSelectedStyleFunction(feature));
        $("#id_regions option[value='" + feature.get('id') + "']").prop("selected", true);
    } else {
        app.recordMapSelected.splice(selIndex, 1);
        feature.setStyle(undefined);
        $("#id_regions option[value='" + feature.get('id') + "']").prop("selected", false);
    }
}

// Map and Form interactions:
app.recordMapUpdateFilters = function() {
    let regions = app.recordMapVectorLayer.getSource().getFeatures();
    let filtered_regions = [];
    let states = [];
    let depths = [];

    if ($('#washington').is(":checked")) { states.push('WA')};
    if ($('#oregon').is(":checked")) { states.push('OR')};
    if ($('#california').is(":checked")) { states.push('CA')};

    if ($('#offshore').is(":checked")) { depths.push('O')};
    if ($('#middepth').is(":checked")) { depths.push('M')};
    if ($('#nearshore').is(":checked")) { depths.push('N')};

    if (states.length == 0 || states.length == 3) {
        filtered_regions = regions;
    } else {
        for (var region_idx = 0; region_idx < regions.length; region_idx++) {
            var region = regions[region_idx];
            for (let state_idx = 0;  state_idx < states.length; state_idx++) {
                var state = states[state_idx];
                if (region.get('states').indexOf(state) >= 0 && filtered_regions.indexOf(region) < 0 ) {
                    filtered_regions.push(region);
                }
            }
        }
    }

    let final_regions = [];
    if (depths.length == 0 || depths.length == 3) {
        final_regions = filtered_regions;
    } else {
        for (var region_idx = 0; region_idx < filtered_regions.length; region_idx++) {
            var region = filtered_regions[region_idx];
            for (let depth_idx = 0; depth_idx < depths.length; depth_idx++) {
                var depth = depths[depth_idx];
                if (region.get('depth') == depth && final_regions.indexOf(region) < 0) {
                    final_regions.push(region);
                }
            }
        }
    }

    if (states.length == 0 && depths.length == 0) {
        final_regions = [];
    }

    for (var region_idx = 0; region_idx < regions.length; region_idx++) {
        var region = regions[region_idx];
        if (final_regions.indexOf(region) >= 0 && app.recordMapSelected.indexOf(region) < 0) {
            //select unselected region:
            app.recordMapToggleFeatureSelection(region);
        } else if (final_regions.indexOf(region) < 0 && app.recordMapSelected.indexOf(region) >= 0) {
            // unselect previously selected region:
            app.recordMapToggleFeatureSelection(region);
        }
    }

}

// Load Regions onto map
app.recordMapZoomToBufferedExtent = function(extent, buffer) {
    if (buffer > 1.0) {
      buffer = buffer/100.0;
    }
    let width = Math.abs(extent[2]-extent[0]);
    let height = Math.abs(extent[3]-extent[1]);
    let w_buffer = width * buffer;
    let h_buffer = height * buffer;
    let buf_west = extent[0] - w_buffer;
    let buf_east = extent[2] + w_buffer;
    let buf_south = extent[1] - h_buffer;
    let buf_north = extent[3] + h_buffer;
    let buffered_extent = [buf_west, buf_south, buf_east, buf_north];
    record_map.getView().fit(buffered_extent, {'duration': 1000});
  }

// const clearInputs = function() {
//     $('input').prop('checked', false);
//     $('textarea').val('');
// }

// Prep Form
app.loadRecordSuggestionForm = function() {
    app.recordMapSelected = [];
    app.record_map = new Map({
        layers: [
            new TileLayer({
                source: new OSM
            }),
            app.recordMapVectorLayer
        ],
        target: 'record_map',
        view: new View({
            center: [
                -13803616.858365921,    // -124
                4865942.279503175       // 40 
            ],
            zoom: 5,
        })
    });

    // clearInputs();
    
    record_map.on('singleclick', function(e) {
        record_map.forEachFeatureAtPixel(e.pixel, app.recordMapToggleFeatureSelection);
    });
    
    $('#filter-boxes-wrapper :checkbox').change(app.recordMapUpdateFilters);
    
    $.ajax({
        url:'/static/app/data/regions.json',
        dataType: 'json'
    })
    .done(function(data) {
        var features = new GeoJSON().readFeatures(data);
        // Flush any pre-existing features to clear out selection.
        debugger;
        if (app.recordMapRegionSource.getFeatures.length < 1) {
            app.recordMapRegionSource.addFeatures(features);
        }
        app.recordMapZoomToBufferedExtent(app.recordMapRegionSource.getExtent(), 0.1);
    });
}
