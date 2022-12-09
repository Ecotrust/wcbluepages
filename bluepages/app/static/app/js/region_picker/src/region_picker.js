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

const getLabel = function(feature) {
    let text = feature.get('name') + "\n(" + feature.get('id') + ")";
    return text;
}

const styleFunction = function(feature) {
    var label = getLabel(feature);
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

const RegionSource = new VectorSource({
    features: []
    // url: '/regions.json',
    // url: '/static/app/data/regions.json',
    // format: new ol.format.GeoJSON()
});

const vectorLayer = new VectorLayer({
    source: RegionSource,
    style: styleFunction,
});

const map = new Map({
    layers: [
        new TileLayer({
            source: new OSM
        }),
        vectorLayer
    ],
    target: 'map',
    view: new View({
        center: [
            -13803616.858365921,    // -124
            4865942.279503175       // 40 
        ],
        zoom: 5,
    })
});

// Selection logic largely taken from OL examples:
//  https://openlayers.org/en/latest/examples/select-features.html
//  https://openlayers.org/en/latest/examples/select-multiple-features.html

let selected = [];

function selectedStyleFunction(feature) {
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

let code_array = [];
// let name_array = [];
const updateSelectedRegionCodes = function() {
    code_array = [];
    // name_array = [];
    for (let i = 0; i < selected.length; i++) {
        code_array.push(selected[i].get('id'));
        // name_array.push(selected[i].get('name'));
    }
    code_array.sort();
    // name_array.sort();
    $('#region-codes').val(code_array.join(';'));
    // $('#region-name').val(name_array.join(';'));
}

const toggleFeatureSelection = function(feature)  {
    const selIndex = selected.indexOf(feature);
    if (selIndex < 0) {
        selected.push(feature);
        feature.setStyle(selectedStyleFunction(feature));
    } else {
        selected.splice(selIndex, 1);
        feature.setStyle(undefined);
    }
    // manage 'selected codes' box now.
    updateSelectedRegionCodes();
}

// Map and Form interactions:
const update_filters = function() {
    let regions = vectorLayer.getSource().getFeatures();
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
        if (final_regions.indexOf(region) >= 0 && selected.indexOf(region) < 0) {
            //select unselected region:
            toggleFeatureSelection(region);
        } else if (final_regions.indexOf(region) < 0 && selected.indexOf(region) >= 0) {
            // unselect previously selected region:
            toggleFeatureSelection(region);
        }
    }

}

// Load Regions onto map
const zoomToBufferedExtent = function(extent, buffer) {
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
    map.getView().fit(buffered_extent, {'duration': 1000});
  }

// utilities
region_picker.copyCodesToClipboard = function() {
    let codes = $('#region-codes').val();
    navigator.clipboard.writeText(codes);
    $('#copy-button').html('Codes copied!')
    window.setTimeout(function() {
        $('#copy-button').html('Copy to clipboard');
    }, 2000);
}

const clearInputs = function() {
    $('input').prop('checked', false);
    $('textarea').val('');
}

// Load Site
$( document ).ready(function() {
    clearInputs();
    
    map.on('singleclick', function(e) {
        map.forEachFeatureAtPixel(e.pixel, toggleFeatureSelection);
    });
    
    $('#filter-boxes-wrapper :checkbox').change(update_filters);
    
    $.ajax({
        // url:'/regions.json',
        url:'/static/app/data/regions.json',
        dataType: 'json'
    })
    .done(function(data) {
        var features = new GeoJSON().readFeatures(data);
        RegionSource.addFeatures(features);
        zoomToBufferedExtent(RegionSource.getExtent(), 0.1);
    });
})

// module.exports = {
//     copyCodesToClipboard
// }